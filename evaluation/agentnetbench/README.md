## AgentNetBench — Offline Evaluation

AgentNetBench provides an offline evaluator for UI interaction trajectories. It compares model-predicted low-level actions (click, moveTo, write, press, scroll, terminate, etc.) against ground-truth actions and reports detailed metrics.

### Supported agents
- qwen25vl (Qwen2.5-VL family)
- aguvis

Qwen matching substrings (case-insensitive): `qwen2.5-vl`, `qwen-vl`, `qwen25vl`, `qwen2.5vl`. Any model name containing `aguvis` selects the Aguvis agent.

### Requirements
- Python 3.9+
- Packages:
  - openai (>=1.0.0)
  - pillow
  - editdistance (optional; the evaluator falls back to a built-in edit-distance implementation if missing)

Install:
```bash
pip install "openai>=1.0.0" pillow editdistance
```

### Data layout
Place trajectory JSON files under a directory, and their corresponding screenshots under an `images/` subfolder.

Example structure:
```
AgentNetBench/
  single_data/
    20240917_xxx.json
    images/
      20240917_xxx_0.png
      20240917_xxx_1.png
```

Minimal trajectory schema (example):
```json
{
  "task_id": "20240917_xxx",
  "high_level_task_description": "Open the browser and search for ...",
  "steps": [
    {
      "image": "20240917_xxx_0.png",
      "ground_truth_actions": [
        { "type": "moveTo", "params": { "position": {"x": 0.42, "y": 0.63} }, "metadata": {"bboxes": []} },
        { "type": "click",  "params": { "position": {"x": 0.42, "y": 0.63} }, "metadata": {"bboxes": []} }
      ]
    }
  ]
}
```

Notes:
- Coordinates are relative (0–1). When metadata bounding boxes are available, evaluation accepts any click/move that falls inside the bbox.
- For write+enter sequences, the evaluator merges them for robust scoring.
- The evaluator does not install packages at import time. Missing optional
  `editdistance` uses a built-in fallback so offline re-evaluation does not
  mutate the runtime environment.
- `press` and `hotkey` compare normalized key sequences while preserving order
  and repeated keys.
- `scroll` compares direction and amount. Opposite-direction scrolls receive no
  credit; same-direction numeric scrolls receive an amount-ratio score.
- Extra predicted actions are penalized by `len(ground_truth_actions) /
  len(predicted_actions)`, preventing a correct first action followed by
  unrelated actions from receiving full credit.

### Run evaluation
```bash
python run.py \
  --data single_data \
  --image_dir single_data/images \
  --output output \
  --model qwen2.5-vl-7b \
  --base_url http://YOUR_OPENAI_COMPATIBLE_SERVER/v1 \
  --api_key YOUR_API_KEY \
  --num_cores 10
```

Tips:
- Any of `qwen2.5-vl`, `qwen-vl`, `qwen25vl`, `qwen2.5vl` in `--model` selects Qwen2.5-VL. Include `aguvis` to select Aguvis.
- Absolute paths are recommended.

### Outputs
Results are written to:
```
<output>/eval_YYYYMMDD_HHMMSS_<sanitized_model>/
  ├─ <task_id>.json           # per-trajectory step-level results
  ├─ metric.json              # summary metrics
  └─ hyperparams.json         # run configuration
```

Per-step result fields include:
- raw_response, parsed_action, predicted_actions
- evaluation.total and evaluation.actions per type
- used_actions and alternative_matched when an alternative ground truth option scores better

### Re-evaluate existing results (without calling the model)
You can re-parse and re-score previously saved outputs (useful after evaluator updates):
```bash
python reeval.py \
  --input_dir output/<eval_dir>
```

### Troubleshooting
- openai import warnings in your IDE: install `openai>=1.0.0`.
- editdistance missing: the evaluator uses a built-in fallback; you can also `pip install editdistance` manually for faster write-action scoring.
- No results or low scores: ensure `--image_dir` points to the correct images and your model name triggers the intended agent.

### License
This repository is intended for research and benchmarking. Please review the project’s root-level license for terms.
