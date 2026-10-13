---
name: llm-inference
description: "Local LLM inference: llama.cpp (CPU/edge GGUF serving + HF Hub discovery) and vLLM (high-throughput GPU serving with OpenAI API)."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [llama.cpp, vllm, inference, GGUF, quantization, serving, OpenAI API, local LLM]
---

# LLM Inference — Local Model Serving

Two complementary skills for running LLMs locally: llama.cpp for CPU/edge and vLLM for high-throughput GPU serving.

## When to use

- User wants to run a local LLM on CPU, Apple Silicon, or edge hardware
- User wants to serve a production LLM API with high throughput
- User needs help choosing quantization (Q4/Q5/Q6/IQ) for their RAM/VRAM
- User wants to find the right GGUF file on Hugging Face for llama.cpp
- User needs OpenAI-compatible endpoints from a local model

## Skill Selection

| Need | Skill | Best For |
|------|-------|----------|
| CPU/edge inference, single-user, Apple Silicon | **llama-cpp** | Local dev, personal use, resource-constrained hardware |
| High-throughput GPU serving, multi-user API | **serving-llms-vllm** | Production deployment, 100+ req/sec, tensor parallelism |

## llama-cpp — Local GGUF Inference + HF Hub Discovery

### Model Discovery Workflow (URL-first)
1. Search Hub: `https://huggingface.co/models?apps=llama.cpp&sort=trending`
2. Open repo with local-app view: `https://huggingface.co/<repo>?local-app=llama.cpp`
3. Copy the exact `llama-server` or `llama-cli` command from the local-app snippet
4. Query tree API to confirm GGUF files exist: `https://huggingface.co/api/models/<repo>/tree/main?recursive=true`

### Quick Start
```bash
brew install llama.cpp                    # Install
llama-server -hf bartowski/Llama-3.2-3B-Instruct-GGUF:Q8_0  # Run from Hub
curl http://localhost:8080/v1/chat/completions ...            # OpenAI API
```

### Quant Selection
- General chat: `Q4_K_M`
- Code/technical: `Q5_K_M` or `Q6_K`
- Tight RAM: `Q3_K_M` or `IQ` variants
- Always prefer the exact quant HF marks as compatible

### Multimodal (Audio)
```bash
llama-mtmd-cli -m model.gguf --mmproj mmproj.gguf --jinja --n-gpu-layers 0 -p "Transcribe" --audio input.wav
```
**Pitfall:** `--jinja` flag required for Gemma 4. Use English prompts for transcription.

### References
- `references/hub-discovery.md` — URL-only HF workflows
- `references/quantization.md` — quant quality tradeoffs
- `references/server.md` — server launch, Docker, load balancing
- `references/optimization.md` — CPU threading, GPU offload, benchmarks
- `references/troubleshooting.md` — install/inference/server issues

## serving-llms-vllm — High-Performance GPU Serving

### Quick Start
```bash
pip install vllm
vllm serve meta-llama/Llama-3-8B-Instruct    # OpenAI-compatible server
```

### Key Features
- **PagedAttention:** 24x higher throughput than standard transformers
- **Continuous batching:** Mixes prefill/decode requests
- **Quantization:** AWQ, GPTQ, FP8 support
- **Tensor parallelism:** Multi-GPU serving

### Production Deployment
```bash
vllm serve meta-llama/Llama-3-8B-Instruct \
  --gpu-memory-utilization 0.9 \
  --enable-prefix-caching \
  --enable-metrics --metrics-port 9090 \
  --port 8000 --host 0.0.0.0
```

### When to use vLLM vs llama.cpp
- **vLLM:** Production APIs (100+ req/sec), multi-user, GPU servers
- **llama.cpp:** CPU/edge, single-user, Apple Silicon, resource-constrained

### References
- `references/server-deployment.md` — Docker, Kubernetes, load balancing
- `references/optimization.md` — PagedAttention tuning, benchmarks
- `references/quantization.md` — AWQ/GPTQ/FP8 setup
- `references/troubleshooting.md` — error messages, debugging
