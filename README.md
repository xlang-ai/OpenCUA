
<h1 style="
  font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif;
  font-size:48px;
  font-weight:700;
  line-height:1.25;
  text-align:center;
  margin:0 0 24px;">
  OpenCUA: Open Foundations for Computer-Use Agents
</h1>

<p align="center">
&nbsp&nbsp🌐 <a href="https://opencua.xlang.ai/">Website</a>&nbsp&nbsp | &nbsp&nbsp📑 <a href="https://arxiv.org/abs/2508.09123">Paper</a>&nbsp&nbsp | &nbsp&nbsp🤗 <a href="https://huggingface.co/datasets/xlangai/AgentNet">Dataset</a>&nbsp&nbsp | &nbsp&nbsp🔎 <a href="https://agentnet_data_viewer.xlang.ai/">Data Viewer</a>&nbsp&nbsp | &nbsp&nbsp🤖 <a href="https://huggingface.co/collections/xlangai/opencua-open-foundations-for-computer-use-agents-6882014ebecdbbe46074a68d">Model</a>&nbsp&nbsp | &nbsp&nbsp🔧  <a href="https://agentnet-tool.xlang.ai/">Tool</a>&nbsp&nbsp | &nbsp&nbsp🎮  <a href="https://huggingface.co/spaces/xlangai/OpenCUA-demo">Model Demo</a>&nbsp&nbsp 
</p>

<div align="center">
  <img src="assets/images/main_fig.png" width="600" alt="OpenCUA-7B Performance Scaling">
</div>

<div style="max-width:900px;margin:0 auto;">

## 📢 Updates
- 2026-01-17: 🎉 **vLLM now fully supports OpenCUA-7B, OpenCUA-32B, and OpenCUA-72B!** Thanks to the [Meituan EvoCUA Team](https://github.com/meituan/EvoCUA) for their contributions to vLLM integration. See [vLLM Serve](model/README.md) for usage instructions.

- 2025-12-17: You can now view AgentNet dataset trajectories online via [AgentNet Data Viewer](https://agentnet_data_viewer.xlang.ai/), or use the code in `data/vis/` to visualize your own trajectory data. See [vis/README.md](./data/vis/README.md) for usage instructions. We also summarized the metadata of AgentNet here [Metadata json](https://huggingface.co/datasets/xlangai/AgentNet/blob/main/meta_data_merged.jsonl).


- 2025-11-28: VLLM support of OpenCUA is available at [[Model] Add OpenCUA-7B support #29068](https://github.com/vllm-project/vllm/pull/29068). Super grateful to [lim4349](https://github.com/lim4349) !
  
- 2025-10-12:  <span style="font-weight:bold">[OpenCUA-7B-exl2](https://huggingface.co/sujitvasanth/OpenCUA-7B-exl2) is now live!</span> ⚡️  
  Thanks to [Sujit Vasanth](https://huggingface.co/sujitvasanth) for producing a quantized **exllamav2** version of OpenCUA-7B — enabling much faster inference with lower VRAM usage.  


- 2025-10-03: <span style="color:red; font-weight:bold">New OpenCUA model!</span>🔥 
[OpenCUA-72B](https://huggingface.co/xlangai/OpenCUA-72B-preview) now ranks #1 on the [OSWorld-Verified leaderboard](https://os-world.github.io/). It also has strong grounding ability, 37.3% (SOTA) on UI-Vision 
 and 60.8% on ScreenSpot-Pro.
- 2025-08-13: We released our [paper](https://arxiv.org/abs/2508.09123) and [project page](https://opencua.xlang.ai/). Check it out!

# Introduction
<div style="
  max-width: 880px;              /* 可按需调节整体宽度 */
  margin: 0 auto;               /* 居中容器 */
  text-align: justify;          /* 关键：两端对齐 */
  text-justify: inter-word;     /* 优化英文对齐效果 */
  line-height: 1.6;">
  
<b>OpenCUA</b> is a comprehensive open-source framework for scaling CUA data and foundation models, consisting of: 
- <b>[AgentNet](https://huggingface.co/datasets/xlangai/AgentNet)</b>: the first large-scale computer-use task dataset spanning 3 operating systems and 200+ applications and websites; 
- **[AgentNetTool](https://agentnet-tool.xlang.ai/)**: an annotation infrastructure that seamlessly captures human computer-use demonstrations; 
- <b>[AgentNetBench](https://github.com/xlang-ai/OpenCUA/tree/main/AgentNetBench)</b>: an offline evaluator that benchmarks model-predicted low-level actions against ground-truth trajectories.
- **[OpenCUA Models](https://huggingface.co/collections/xlangai/opencua-open-foundations-for-computer-use-agents-6882014ebecdbbe46074a68d")**: end-to-end computer-use foundation models than can produce executable actions in the computer environments with great planning and grounding capabilities.


With the help of OpenCUA framework, our end-to-end agent models demonstrate strong performance across CUA benchmarks. In particular, <b>OpenCUA-72B</b> achieves an average success rate of **45.0%** on [OSWorld-Verified](https://os-world.github.io/), 
establishing a new state-of-the-art (SOTA) among open-source models. 

</div>


##  🚀 Quick Start of OpenCUA Models
<div style="border-left: 6px solid #f28c28; background: #fff8e6; padding: 12px 16px; margin: 16px 0;">
  <strong>⚠️ Important for Qwen-based Models (OpenCUA-7B, OpenCUA-32B, OpenCUA-72B):</strong>
  
  To align with our training infrastructure, we have modified the model in two places:
  <ul style="margin-top: 8px;">
    <li>1. Multimodal Rotary Position Embedding (M-RoPE) has been replaced with 1D RoPE</strong>.</li>
    <li>2. Using the same Tokenizer and ChatTemplate as Kimi-VL.</li>
    <li>Do not use the default transformers and vllm classes to load the model. Tokenizer and Chat Template should be aligned if training the models.</li>
  </ul>
</div>


### Installation & Download

First, install the required transformers dependencies:

```bash
conda create -n opencua python=3.10
conda activate opencua
pip install -r requirement.txt
```

Download the model weight from huggingface:
```bash
from huggingface_hub import snapshot_download
snapshot_download(
    repo_id="xlangai/OpenCUA-7B",
    local_dir="OpenCUA-7B",                
    local_dir_use_symlinks=False  
)
```

### 🚀 vLLM Serve

We recommend using vLLM for production deployment. Requires **vllm>=0.12.0** with `--trust-remote-code`.

```bash
# OpenCUA-7B (single GPU)
vllm serve xlangai/OpenCUA-7B \
  --trust-remote-code \
  --served-model-name opencua-7b \
  --host 0.0.0.0 \
  --port 8000

# OpenCUA-32B (4 GPUs, tensor parallel)
vllm serve xlangai/OpenCUA-32B \
  --trust-remote-code \
  --tensor-parallel-size 4 \
  --served-model-name opencua-32b \
  --host 0.0.0.0 \
  --port 8000

# OpenCUA-72B with data parallelism (tp=2, dp=4 for 4 instances on 8 GPUs)
vllm serve xlangai/OpenCUA-72B \
  --trust-remote-code \
  --tensor-parallel-size 2 \
  --data-parallel-size 4 \
  --gpu-memory-utilization 0.85 \
  --host 0.0.0.0 \
  --port 8000
```

Adjust `--tensor-parallel-size`, `--data-parallel-size`, and `--gpu-memory-utilization` based on your hardware configuration.

For more examples and inference code, see [model/inference/vllm_inference.py](./model/inference/vllm_inference.py).

### 🎯 GUI Grounding

First, start the vLLM server (using OpenCUA-7B as example):
```bash
vllm serve xlangai/OpenCUA-7B \
  --trust-remote-code \
  --served-model-name opencua-7b \
  --host 0.0.0.0 \
  --port 8000
```

Then run the grounding examples:
```
cd ./model/inference/
python vllm_inference.py
```

Or with HuggingFace Transformers (no server required):
```
python huggingface_inference.py
```

### 🖥️ Computer Use Agent
**[OpenCUAAgent](https://github.com/xlang-ai/OSWorld/blob/main/mm_agents/opencua_agent.py)** is developed in the [OSWorld](https://github.com/xlang-ai/OSWorld) environment based on OpenCUA models. It iteratively perceives the environment via screenshots, produces reflective long CoT as inner monologue, and predicts the next action to be executed. OpenCUAAgent uses 3 images in total and L2 CoT format in default.

Command for running OpenCUA-7B and OpenCUA-32B in OSWorld:
```
    python run_multienv_opencua.py \
        --headless \
        --observation_type screenshot \
        --model OpenCUA-32B \
        --result_dir ./results --test_all_meta_path evaluation_examples/test_all_no_gdrive.json \
        --max_steps 100 \
        --num_envs 30  \
        --coordinate_type qwen25
```

---

## Performance

### Online Agent Evaluation
OpenCUA models achieves strong performance on **[OSWorld-Verified](https://os-world.github.io/)**. 
OPENCUA-32B achieves the best performance among all open-source models with an average success rate of 34.8%, outperforming prior baselines by large margins. 
It also closes the gap to proprietary Claude models.
<div align="center">

| **Model**                        | **15 Steps** | **50 Steps** | **100 Steps** |
|-------------------------------|:--------:|:--------:|:---------:|
| **Proprietary**               |          |          |           |
| OpenAI CUA                    | 26.0     | 31.3     | 31.4      |
| Seed 1.5-VL                   | 27.9     | —        | 34.1      |
| Claude 3.7 Sonnet             | 27.1     | 35.8     | 35.9      |
| Claude 4 Sonnet               | 31.2     | 43.9     | 41.5      |
| **Open-Source**               |          |          |           |
| Qwen 2.5-VL-32B-Instruct      | 3.0      | —        | 3.9       |
| Qwen 2.5-VL-72B-Instruct      | 4.4      | —        | 5.0       |
| Kimi-VL-A3B                   | 9.7      | —        | 10.3      |
| UI-TARS-72B-DPO               | 24.0     | 25.8     | 27.1      |
| UI-TARS-1.5-7B                | 24.5     | 27.3     | 27.4      |
| OpenCUA-7B *(Ours)*           | 24.3     | 27.9     | 26.6      |
| OpenCUA-32B *(Ours)*          | **29.7** | **34.1** | 34.8      |
| **OpenCUA-72B*(Ours)***      | 39.0   | 44.9  | **45.0**  |
</div>

*OpenCUA scores are the mean of 3 independent runs.*

### GUI Grounding Performance
<div align="center">

| **Model** | **OSWorld-G** | **ScreenSpot-V2** | **ScreenSpot-Pro** | **UI-Vision** |
|-------|-----------|---------------|----------------| ---------- |
| Qwen2.5-VL-7B   | 31.4 | 88.8 | 27.6 |  0.85 |
| Qwen2.5-VL-32B  | 46.5 | 87.0 | 39.4 | - |
| UI-TARS-72B     | 57.1 | 90.3 | 38.1 | 25.5 |
| **OpenCUA-7B**  | 55.3 | 92.3 | 50.0 | 29.7 |
| **OpenCUA-32B** | **59.6** | **93.4** | 55.3 | 33.3 |
| **OpenCUA-72B** | 59.2 | 92.9 | **60.8** | **37.3** |
</div>


### AgentNetBench (Offline Evaluation)
<div align="center">

| **Model** | **Coordinate Actions** | **Content Actions** | **Function Actions** | **Average** |
|-------|-------------------|-----------------|------------------|---------|
| Qwen2.5-VL-7B | 50.7 | 40.8 | 3.1 | 48.0 |
| Qwen2.5-VL-32B | 66.6 | 47.2 | 41.5 | 64.8 |
| Qwen2.5-VL-72B | 67.2 | 52.6 | 50.5 | 67.0 |
| OpenAI CUA          | 71.7 | 57.3 | **80.0** | 73.1 |
| **OpenCUA-7B**  | 79.0 | 62.0 | 44.3 | 75.2 |
| **OpenCUA-32B** | **81.9** | 66.1 | 55.7 | **79.1** |
</div>

---

## AgentNet Dataset - Large-Scale Computer-Use Dataset

<div align="center">
  <img src="assets/images/domain_distribution.png" width="400" alt="AgentNet Dataset Domain Distribution">
</div>

AgentNet is the first large-scale desktop computer-use agent trajectory dataset, containing 22.6K human-annotated computer-use tasks across Windows, macOS, and Ubuntu systems. 

👉 **[AgentNet Huggingface Dataset](https://huggingface.co/datasets/xlangai/AgentNet)**

Download the dataset here：
```
pip install -U huggingface_hub
huggingface-cli download xlangai/AgentNet --repo-type dataset --local-dir ./AgentNet
```

Use the following command to unzip the file (For exmaple, Ubuntu data):
```
cd path_to_your_zip_files

# Merge all the zips
zip -s 0 images.zip --out images-full.zip

# Unzip
unzip images-full.zip -d path_to_your_target_dir
```

Collecting computer-use agent training data requires 3 steps:
- Demonstrate human computer-use task via [AgentNetTool](https://agentnet-tool.xlang.ai/);
- Preprocess the demonstration using [Action Reduction & State-Action Matching](./data/data-processor);
- For each step, [synthesize reflective long CoT](./data/cot-generator)


### 1 AgentNetTool – Annotation & Verification Tool
<div align="center">
  <img src="assets/images/agn_tool_fig.png" width="700" alt="AgentNet Tool">
</div>


Our **AgentNetTool** is a cross-platform GUI recorder that runs unobtrusively on annotators’ machines. It captures synchronized **screen video**, **mouse/keyboard events**, and **accessibility trees**, then provides an in-browser UI for reviewing, trimming, and submitting demonstrations. AgentNet Tool is available on Windows, macOS and Ubuntu. 

👉 **[AgentNetTool Document](https://agentnet-tool.xlang.ai/)**



### 2 DataProcessor – Action Reduction & State–Action Matching
Raw demonstrations can contain thousands of low-level events that are too dense for model training.  
The **DataProcessor** module (`./data/data-process/`) performs two key steps:

1. **Action Reduction** — merges granular signals into concise, semantically meaningful PyAutoGUI actions (e.g., collapsing mouse moves → click, coalescing scrolls, grouping key-press sequences into text or hotkeys).  
2. **State–Action Matching** — aligns every reduced action with the *last visually distinct frame* **before** the action begins, avoiding future-information leakage and yielding compact state–action pairs.

These processed trajectories underlie all downstream training and evaluation.

---

### 3 CoTGenerator – Synthesizing Reflective Long Chain-of-Thought Inner Monologue
To boost robustness and interpretability, we augment each trajectory with **reflective long Chain-of-Thought (CoT) reasoning**.  
The **CoTGenerator** pipeline (`./data/cot-generator/`) synthesizes step-level reflections that:

* reflect on the previous action,
* explain *why* an action is chosen given the current observation and history,  
* note potential alternative actions, and  
* forecast the expected next state.

Empirically, models trained with these rich CoTs scale better with data and generalize across unseen applications.


## AgentNetBench

<div align="center">
  <img src="assets/images/AgentNetBench.png" width="800" alt="AgentNetBench">
</div>


**AgentNetBench** (`./AgentNetBench/`) provides a realistic offline evaluator for OS agent trajectories. It compares model-predicted low-level actions (click, moveTo, write, press, scroll, terminate, etc.) against ground-truth human actions and reports detailed metrics.

👉 See **[AgentNetBench/README.md](./evaluation/agentnetbench/README.md)** for usage instructions.

## TODO
- [x] **vLLM Support** ✅
  - vLLM now fully supports OpenCUA-7B, OpenCUA-32B, and OpenCUA-72B.
  - See [vLLM Serve](#vllm-serve) section for usage instructions.
  - Thanks to the Meituan EvoCUA Team for their contributions!

- [ ] **Training Code**
  - OpenCUA models are developed based on the training infrastructure of Kimi Team.
  - Currently developing the training pipeline based on open-source infrastructure.

## Star History

[![Star History Chart](https://star-history.dera.page/svg?repos=xlang-ai/OpenCUA&type=date&legend=top-left)](https://star-history.dera.page/#xlang-ai/OpenCUA&type=date&legend=top-left)

## Acknowledge
<p>
We thank Yu Su, Caiming Xiong, and the anonymous reviewers for their insightful discussions and valuable feedback.
We are grateful to Moonshot AI for providing training infrastructure and annotated data.
We also sincerely appreciate Hao Yang, Zhengtao Wang, and Yanxu Chen from the Kimi Team for their strong infrastructure support and helpful guidance.
We thank Chong Peng, Taofeng Xue, and Qiumian Huang from the <a href="https://github.com/meituan/EvoCUA" target="_blank">Meituan EvoCUA Team</a> for their contributions to vLLM integration.
The development of our tool is based on the open-source projects-<a href="https://github.com/TheDuckAI/DuckTrack" target="_blank">DuckTrack</a> and <a href="https://github.com/OpenAdaptAI/OpenAdapt" target="_blank">OpenAdapt</a>.
We are very grateful to their commitment to the open source community. Finally, we extend our deepest thanks to all annotators for their tremendous effort and contributions to this project.
</p>

## Research and Commercial Use

OpenCUA (including the model, dataset, tools, and code) may be used for **research, educational, and commercial purposes** under the **MIT License** (see `LICENSE`).

### Citation and Acknowledgement
If you use **OpenCUA models** and/or the **AgentNet dataset** in any **report, technical report, publication, thesis, presentation, blog post, documentation, or other publicly shared material**, we **kindly ask** that you include an explicit acknowledgement in the main text and cite the OpenCUA paper.

### Prohibited Uses
- The model, dataset, tool, and code may **not** be used for any purpose or activity that violates applicable laws or regulations in any jurisdiction
- Use for illegal, unethical, or harmful activities is strictly prohibited

### Disclaimer
- The authors, contributors, and copyright holders are **not responsible** for any illegal, unethical, or harmful use of the Software, nor for any direct or indirect damages resulting from such use
- Use of the "OpenCUA" name, logo, or trademarks does **not** imply any endorsement or affiliation unless separate written permission is obtained
- Users are solely responsible for ensuring their use complies with applicable laws and regulations

## Citation

If you use OpenCUA in your research, please cite our work:

```bibtex
@misc{wang2025opencuaopenfoundationscomputeruse,
      title={OpenCUA: Open Foundations for Computer-Use Agents}, 
      author={Xinyuan Wang and Bowen Wang and Dunjie Lu and Junlin Yang and Tianbao Xie and Junli Wang and Jiaqi Deng and Xiaole Guo and Yiheng Xu and Chen Henry Wu and Zhennan Shen and Zhuokai Li and Ryan Li and Xiaochuan Li and Junda Chen and Boyuan Zheng and Peihang Li and Fangyu Lei and Ruisheng Cao and Yeqiao Fu and Dongchan Shin and Martin Shin and Jiarui Hu and Yuyan Wang and Jixuan Chen and Yuxiao Ye and Danyang Zhang and Dikang Du and Hao Hu and Huarong Chen and Zaida Zhou and Haotian Yao and Ziwei Chen and Qizheng Gu and Yipu Wang and Heng Wang and Diyi Yang and Victor Zhong and Flood Sung and Y. Charles and Zhilin Yang and Tao Yu},
      year={2025},
      eprint={2508.09123},
      archivePrefix={arXiv},
      primaryClass={cs.AI},
      url={https://arxiv.org/abs/2508.09123}, 
}
```


</div>
