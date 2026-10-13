---
name: mlops
description: "MLOps — ML infrastructure: LLM evaluation (benchmarks), LLM serving (vLLM), and computer vision models (SAM). Unified entry point for model lifecycle tasks."
tags: [mlops, ml-infrastructure, llm-evaluation, llm-serving, computer-vision, benchmarking, deployment]
triggers:
  - "mlops"
  - "ml infrastructure"
  - "model deployment"
  - "llm serving"
  - "llm evaluation"
  - "benchmark model"
  - "segment anything"
  - "sam model"
  - "vllm"
  - "lm-eval"
---

# MLOps — ML Infrastructure

Unified entry point for machine learning operations: evaluating models, serving models at scale, and using computer vision models.

## When to use this skill

- **Benchmarking LLMs** → see [LLM Evaluation](#1-llm-evaluation)
- **Serving LLMs with high throughput** → see [LLM Serving](#2-llm-serving)
- **Image segmentation (SAM)** → see [Computer Vision Models](#3-computer-vision-models)

## 1. LLM Evaluation

Evaluate LLMs across 60+ academic benchmarks (MMLU, GSM8K, HumanEval, TruthfulQA, HellaSwag) using EleutherAI's lm-evaluation-harness.

**Quick start:**
```bash
pip install lm-eval
lm_eval --model hf --model_args pretrained=meta-llama/Llama-2-7b-hf --tasks mmlu,gsm8k --device cuda:0
```

**Key workflows:**
- Standard benchmark evaluation (MMLU, GSM8K, HumanEval)
- Track training progress (periodic evaluation at checkpoints)
- Compare multiple models side-by-side
- Evaluate with vLLM backend (5-10x faster)

**Detailed references:**
- `references/evaluation-benchmark-guide.md` — All 60+ tasks described
- `references/evaluation-api-evaluation.md` — Evaluating OpenAI/Anthropic API models
- `references/evaluation-distributed-eval.md` — Multi-GPU and tensor parallel evaluation
- `references/evaluation-custom-tasks.md` — Creating domain-specific evaluation tasks

**When to use vs alternatives:**
- Use lm-eval-harness for: academic benchmarking, standardized metrics, reproducible evaluation
- Use HELM for: broader evaluation (fairness, efficiency, calibration)
- Use AlpacaEval for: instruction-following with LLM judges
- Use MT-Bench for: conversational multi-turn evaluation

## 2. LLM Serving

Deploy production LLM APIs with vLLM — 24x higher throughput than standard transformers via PagedAttention and continuous batching.

**Quick start:**
```bash
pip install vllm
vllm serve meta-llama/Llama-3-8B-Instruct --port 8000
```

**Key workflows:**
- Production API deployment (OpenAI-compatible endpoints)
- Offline batch inference (large dataset processing)
- Quantized model serving (AWQ/GPTQ/FP8 for limited GPU memory)

**Detailed references:**
- `references/serving-server-deployment.md` — Docker, Kubernetes, load balancing
- `references/serving-optimization.md` — PagedAttention tuning, continuous batching, benchmarks
- `references/serving-quantization.md` — AWQ/GPTQ/FP8 setup and accuracy comparisons
- `references/serving-troubleshooting.md` — Error messages, debugging, performance diagnostics

**When to use vs alternatives:**
- Use vLLM for: production APIs (100+ req/sec), OpenAI-compatible endpoints, multi-user apps
- Use llama.cpp for: CPU/edge inference, single-user
- Use HuggingFace transformers for: research, prototyping, one-off generation
- Use TensorRT-LLM for: NVIDIA-only, absolute maximum performance

## 3. Computer Vision Models

Use Meta AI's Segment Anything Model (SAM) for zero-shot image segmentation — segment any object without task-specific training.

**Quick start:**
```bash
pip install git+https://github.com/facebookresearch/segment-anything.git
```

```python
from segment_anything import sam_model_registry, SamPredictor
sam = sam_model_registry["vit_h"](checkpoint="sam_vit_h_4b8939.pth")
sam.to(device="cuda")
predictor = SamPredictor(sam)
```

**Key workflows:**
- Interactive segmentation (point/box prompts)
- Automatic mask generation (all objects in image)
- Object extraction with transparent background
- ONNX deployment for browsers and edge devices

**Detailed references:**
- `references/cv-advanced-usage.md` — Batching, fine-tuning, integration patterns
- `references/cv-troubleshooting.md` — Common issues and solutions

**When to use vs alternatives:**
- Use SAM for: zero-shot segmentation, annotation tools, training data generation
- Use YOLO/Detectron2 for: real-time object detection with classes
- Use Mask2Former for: semantic/panoptic segmentation with categories
- Use GroundingDINO + SAM for: text-prompted segmentation
- Use SAM 2 for: video segmentation tasks

## Model variants (SAM)

| Model | Checkpoint | Size | Speed | Accuracy |
|-------|------------|------|-------|----------|
| ViT-H | `vit_h` | 2.4 GB | Slowest | Best |
| ViT-L | `vit_l` | 1.2 GB | Medium | Good |
| ViT-B | `vit_b` | 375 MB | Fastest | Good |

## Hardware requirements

| Task | Minimum GPU | Recommended |
|------|-------------|-------------|
| LLM eval (7B) | 16GB VRAM (bf16) or 8GB (8-bit) | A100 40GB |
| LLM serving (7B) | 1x A10 (24GB) | A100 40GB |
| LLM serving (70B) | 4x A100 (40GB) with AWQ | 2x A100 80GB |
| SAM (ViT-H) | 16GB VRAM | A100 40GB |

## Resources

- lm-eval-harness: https://github.com/EleutherAI/lm-evaluation-harness
- vLLM: https://github.com/vllm-project/vllm
- SAM: https://github.com/facebookresearch/segment-anything
- HuggingFace Open LLM Leaderboard: https://huggingface.co/spaces/HuggingFaceH4/open_llm_leaderboard
