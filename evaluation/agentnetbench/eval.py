#!/usr/bin/env python3
from collections import defaultdict
import math
from typing import Dict, List, Tuple, Any

try:
    import editdistance
except ImportError:
    editdistance = None


class ActionEvaluator:
    """Class to evaluate predicted actions against ground truth actions."""

    def __init__(self):
        """Initialize the evaluator with constants."""
        self.COORD_THRESHOLD = 0.01 * 2 ** 0.5
        self.ALPHA = 120
        self.WRITE_SIMILARITY_THRESHOLD = 0.8

    def edit_distance(self, left: str, right: str) -> int:
        """Return Levenshtein distance without mutating the runtime environment."""
        if editdistance is not None:
            return editdistance.eval(left, right)

        if left == right:
            return 0
        if not left:
            return len(right)
        if not right:
            return len(left)

        previous = list(range(len(right) + 1))
        for i, left_char in enumerate(left, start=1):
            current = [i]
            for j, right_char in enumerate(right, start=1):
                insertion = current[j - 1] + 1
                deletion = previous[j] + 1
                substitution = previous[j - 1] + (left_char != right_char)
                current.append(min(insertion, deletion, substitution))
            previous = current
        return previous[-1]

    def normalize_keys(self, keys: Any) -> List[str]:
        """Normalize key sequences while preserving order and repeated keys."""
        if isinstance(keys, list):
            return [str(key).lower() for key in keys]
        if keys in (None, ""):
            return []
        return [str(keys).lower()]

    def scroll_direction(self, value: Any) -> int:
        """Return -1 for down/negative, 1 for up/positive, 0 if unknown."""
        if isinstance(value, (int, float)):
            if value > 0:
                return 1
            if value < 0:
                return -1
            return 0

        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"up", "positive"}:
                return 1
            if normalized in {"down", "negative"}:
                return -1
            try:
                return self.scroll_direction(float(normalized))
            except ValueError:
                return 0
        return 0

    def scroll_score(self, predicted: Any, ground_truth: Dict[str, Any]) -> float:
        """Score scroll direction and amount instead of action type only."""
        gt_params = ground_truth.get("params", {})
        gt_amount = gt_params.get("amount", gt_params.get("pixels"))
        gt_direction = self.scroll_direction(
            gt_amount if gt_amount is not None else gt_params.get("direction")
        )
        pred_direction = self.scroll_direction(predicted)

        if gt_direction and pred_direction and gt_direction != pred_direction:
            return 0.0
        if gt_direction and not pred_direction:
            return 0.0

        if isinstance(predicted, (int, float)) and isinstance(gt_amount, (int, float)):
            pred_amount = abs(float(predicted))
            true_amount = abs(float(gt_amount))
            if pred_amount == 0 and true_amount == 0:
                return 1.0
            if pred_amount == 0 or true_amount == 0:
                return 0.0
            return min(pred_amount, true_amount) / max(pred_amount, true_amount)

        return 1.0 if gt_direction == pred_direction else 0.0

    def is_point_in_bbox(self, x: float, y: float, bbox: List[float]) -> bool:
        """Check if a point (x,y) is inside a bounding box.
        
        Args:
            x: X coordinate
            y: Y coordinate
            bbox: Bounding box [rel_x, rel_y, rel_width, rel_height]
            
        Returns:
            True if point is inside bbox
        """
        # Ensure all values are floats
        try:
            bbox_x = float(bbox[0])
            bbox_y = float(bbox[1])
            bbox_w = float(bbox[2])
            bbox_h = float(bbox[3])
            x = float(x)
            y = float(y)
            
            return (bbox_x <= x <= bbox_x + bbox_w) and (bbox_y <= y <= bbox_y + bbox_h)
        except (ValueError, TypeError, IndexError) as e:
            print(f"Error in bbox check: {e}, bbox={bbox}, point=({x},{y})")
            return False

    def smooth_coord_score(self, distance: float) -> float:
        """Calculate smooth coordinate score based on distance.
        
        Args:
            distance: Distance between predicted and ground truth coordinates
            
        Returns:
            Score between 0 and 1
        """
        if distance <= self.COORD_THRESHOLD:
            return 1.0
        else:
            return math.exp(-self.ALPHA * (distance - self.COORD_THRESHOLD))

    def evaluate_action(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate predicted actions against ground truth actions.
        
        Args:
            item: Dictionary containing:
                - ground_truth_actions: List of ground truth actions
                - predicted_actions: List of predicted actions from agent
            
        Returns:
            Dictionary containing evaluation scores
        """
        ground_truth = item.get('ground_truth_actions', [])
        predictions = item.get('predicted_actions', [])
        # print(ground_truth)
        # print(predictions)
        if not ground_truth or not predictions:
            print("No ground truth or predicted actions")
            return {"total": 0.0, "actions": {}}

        # Preprocess ground truth actions - merge write+enter
        processed_gt = []
        i = 0
        while i < len(ground_truth):
            current_action = ground_truth[i]
            
            # Check if this is a write action followed by a press enter action
            if (i < len(ground_truth) - 1 and 
                current_action['type'].lower() == 'write' and 
                ground_truth[i+1]['type'].lower() in ['press', 'hotkey']):
                
                next_action = ground_truth[i+1]
                next_keys = next_action['params'].get('keys', [])
                
                # Check if the keys contain only 'enter' or 'return'
                if isinstance(next_keys, list) and len(next_keys) == 1 and next_keys[0].lower() in ['enter', 'return']:
                    # Create a merged action
                    merged_action = dict(current_action)
                    text_param = 'text' if 'text' in current_action['params'] else 'content'
                    merged_action['params'][text_param] = current_action['params'][text_param] + '\n'
                    processed_gt.append(merged_action)
                    i += 2  # Skip both actions
                    continue
            
            # If no merge, add the action as is
            processed_gt.append(current_action)
            i += 1
        
        # Preprocess predicted actions - merge write+enter
        processed_pred = []
        i = 0
        while i < len(predictions):
            current_action = predictions[i]
            
            # Check if this is a write action followed by a press enter action
            if (i < len(predictions) - 1 and 
                current_action[0].lower() == 'write' and
                predictions[i+1][0].lower() == 'press'):
                
                next_keys = predictions[i+1][1]
                
                # Check if the keys contain only 'enter' or 'return'
                if isinstance(next_keys, list) and len(next_keys) == 1 and next_keys[0].lower() in ['enter', 'return']:
                    # Create a merged action
                    processed_pred.append(('write', current_action[1] + '\n'))
                    i += 2  # Skip both actions
                    continue
            
            # If no merge, add the action as is
            processed_pred.append(current_action)
            i += 1
        
        # Use processed actions for evaluation
        ground_truth = processed_gt
        predictions = processed_pred
        action_count_penalty = 1.0
        if len(predictions) > len(ground_truth):
            action_count_penalty = len(ground_truth) / len(predictions)

        scores = defaultdict(float)
        action_counts = defaultdict(int)

        # Handle terminate action
        if ground_truth[0]['type'] == 'terminate':
            if (
                predictions[0][0] == 'terminate'
                and predictions[0][1] == ground_truth[0]['params']['status']
            ):
                return {
                    "total": 1.0 * action_count_penalty,
                    "actions": {"terminate": 1.0 * action_count_penalty}
                }
            else:
                return {"total": 0.0, "actions": {"terminate": 0.0}}

        # Track mismatched action types
        gt_types = [a['type'].lower() for a in ground_truth]
        pred_types = [p[0].lower() for p in predictions]
        
        # Only check if the first predicted action type matches any ground truth action type
        action_match = pred_types[0] in gt_types if pred_types else False
        
        # Simple case: first action type doesn't match
        if not action_match:
            # Create scores dictionary with 0.0 for each ground truth action type
            for gt in ground_truth:
                g_type = gt['type'].lower()
                scores[g_type] = 0.0
            
            return {
                "total": 0.0,
                "actions": dict(scores)
            }
        
        # If first action type matches, proceed with detailed evaluation
        for i, gt in enumerate(ground_truth):
            g_type = gt['type'].lower()  # Convert to lowercase
            action_counts[g_type] += 1
            
            # Skip if we're out of predictions
            if i >= len(predictions):
                scores[g_type] += 0.0
                continue
                
            pred = predictions[i]
            p_type, p_val = pred
            p_type = p_type.lower()  # Convert to lowercase
            
            # If action types don't match for this specific action, give 0 score
            if p_type != g_type:
                scores[g_type] += 0.0
                continue
            
            if g_type in ['click', 'doubleclick', 'rightclick', 'tripleclick']:
                px, py = p_val
                g_pos = gt['params']['position']
                gx, gy = g_pos['x'], g_pos['y']

                # Check bounding boxes for clicks
                if 'metadata' in gt:
                    bboxes = [bbox['rel_bbox'] for bbox in gt['metadata'].get('bboxes', [])]
                    if any(self.is_point_in_bbox(px, py, bbox) for bbox in bboxes):
                        scores[g_type] += 1.0
                        continue

                # Distance-based scoring
                distance = ((px - gx) ** 2 + (py - gy) ** 2) ** 0.5
                scores[g_type] += self.smooth_coord_score(distance)

            elif g_type == 'moveto':
                px, py = p_val
                g_pos = gt['params']['position']
                gx, gy = g_pos['x'], g_pos['y']
                
                # Check bounding boxes for moveTo
                if 'metadata' in gt:
                    bboxes = [bbox['rel_bbox'] for bbox in gt['metadata'].get('bboxes', [])]
                    if any(self.is_point_in_bbox(px, py, bbox) for bbox in bboxes):
                        scores[g_type] += 1.0
                        continue
                
                # Distance-based scoring
                distance = ((px - gx) ** 2 + (py - gy) ** 2) ** 0.5
                scores[g_type] += self.smooth_coord_score(distance)
                
            elif g_type == 'dragto':
                px, py = p_val
                g_pos = gt['params']['position']
                gx, gy = g_pos['x'], g_pos['y']
                
                # Check bounding boxes for dragTo actions
                if 'metadata' in gt:
                    bboxes = [bbox['rel_bbox'] for bbox in gt['metadata'].get('bboxes', [])]
                    if any(self.is_point_in_bbox(px, py, bbox) for bbox in bboxes):
                        scores[g_type] += 1.0
                        continue
                
                # Distance-based scoring for dragTo
                distance = ((px - gx) ** 2 + (py - gy) ** 2) ** 0.5
                scores[g_type] += self.smooth_coord_score(distance)

            elif g_type == 'write':
                g_content = gt['params'].get('content', '') or gt['params'].get('text', '')
                g_content = g_content.lower().strip()
                p_val = p_val.lower().strip()
                
                g_has_newline = g_content.endswith('\n')
                p_has_newline = p_val.endswith('\n')
                g_content = g_content.rstrip('\n')
                p_val = p_val.rstrip('\n')
                
                max_len = max(len(p_val), len(g_content))
                
                if max_len == 0:
                    similarity = 1.0
                else:
                    edit_dist = self.edit_distance(p_val, g_content)
                    similarity = 1.0 - (edit_dist / max_len)
                    
                    if g_has_newline != p_has_newline:
                        similarity *= 0.9
                    
                    if similarity >= self.WRITE_SIMILARITY_THRESHOLD:
                        similarity = 1.0
                    else:
                        similarity = similarity / self.WRITE_SIMILARITY_THRESHOLD
                
                scores[g_type] += similarity

            elif g_type in ['press', 'hotkey']:
                g_keys = gt['params'].get('keys', [])
                
                if isinstance(p_val, list) and isinstance(g_keys, list):
                    normalized_p_keys = self.normalize_keys(p_val)
                    normalized_g_keys = self.normalize_keys(g_keys)

                    if normalized_p_keys == normalized_g_keys:
                        scores[g_type] += 1.0
                    else:
                        scores[g_type] += 0.0
                else:
                    # Fallback to exact match if not list comparison
                    scores[g_type] += 1.0 if p_val == g_keys else 0.0

            elif g_type == 'scroll':
                scores[g_type] += self.scroll_score(p_val, gt)

        # Calculate final scores
        for action_type in scores:
            scores[action_type] /= action_counts[action_type]
            scores[action_type] *= action_count_penalty

        # Calculate total score as average of ground truth action scores
        action_score = sum(scores.values()) / len(scores) if scores else 0.0
        
        # Apply action match penalty if action types don't match
        total_score = action_score * (0.2 if not action_match else 1.0)
        
        return {
            "total": total_score,
            "actions": dict(scores)
        }
