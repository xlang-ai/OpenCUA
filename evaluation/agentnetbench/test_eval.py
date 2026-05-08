import unittest

from eval import ActionEvaluator


def make_item(gt_actions, predicted_actions):
    return {
        "ground_truth_actions": gt_actions,
        "predicted_actions": predicted_actions,
    }


class ActionEvaluatorValidityTests(unittest.TestCase):
    def setUp(self):
        self.evaluator = ActionEvaluator()

    def test_import_does_not_require_editdistance_install(self):
        self.assertEqual(self.evaluator.edit_distance("kitten", "sitting"), 3)

    def test_scroll_wrong_direction_is_not_full_credit(self):
        item = make_item(
            [{"type": "scroll", "params": {"amount": -3}}],
            [("scroll", 3)],
        )

        result = self.evaluator.evaluate_action(item)

        self.assertEqual(result["total"], 0.0)
        self.assertEqual(result["actions"]["scroll"], 0.0)

    def test_scroll_same_direction_scores_amount_similarity(self):
        item = make_item(
            [{"type": "scroll", "params": {"amount": -6}}],
            [("scroll", -3)],
        )

        result = self.evaluator.evaluate_action(item)

        self.assertAlmostEqual(result["total"], 0.5)
        self.assertAlmostEqual(result["actions"]["scroll"], 0.5)

    def test_hotkey_order_is_not_ignored(self):
        item = make_item(
            [{"type": "hotkey", "params": {"keys": ["ctrl", "v"]}}],
            [("hotkey", ["v", "ctrl"])],
        )

        result = self.evaluator.evaluate_action(item)

        self.assertEqual(result["total"], 0.0)
        self.assertEqual(result["actions"]["hotkey"], 0.0)

    def test_repeated_key_count_is_not_ignored(self):
        item = make_item(
            [{"type": "press", "params": {"keys": ["down", "down"]}}],
            [("press", ["down"])],
        )

        result = self.evaluator.evaluate_action(item)

        self.assertEqual(result["total"], 0.0)
        self.assertEqual(result["actions"]["press"], 0.0)

    def test_extra_prediction_penalizes_otherwise_correct_action(self):
        item = make_item(
            [
                {
                    "type": "click",
                    "params": {"position": {"x": 0.5, "y": 0.5}},
                    "metadata": {"bboxes": []},
                }
            ],
            [("click", (0.5, 0.5)), ("write", "unexpected")],
        )

        result = self.evaluator.evaluate_action(item)

        self.assertAlmostEqual(result["total"], 0.5)
        self.assertAlmostEqual(result["actions"]["click"], 0.5)


if __name__ == "__main__":
    unittest.main()
