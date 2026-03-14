---
base_model: codellama/CodeLlama-7b-Instruct-hf
library_name: peft
pipeline_tag: text-generation
tags:
- base_model:adapter:codellama/CodeLlama-7b-Instruct-hf
- lora
- sft
- transformers
- trl
- code
- coding-assistant
- savage
---

# 🔥 SavageAI — Local Offline Coding Assistant

A savage, unfiltered coding AI built on CodeLlama-7B-Instruct.
Runs 100% locally on your machine. No cloud. No subscription. No BS.

It roasts your bad code, swears freely, makes dark jokes — but is extremely
smart and always gives you the correct answer. Like a genius senior dev with
absolutely zero filter.

---

## Model Details

### Model Description

SavageAI is a LoRA fine-tuned version of CodeLlama-7B-Instruct trained for
two purposes:

1. **Coding ability** — fine-tuned on 3000 examples covering Python, C, C++,
   Java, JavaScript and general algorithms
2. **Savage personality** — fine-tuned on custom conversation data that gives
   the model an unfiltered, sarcastic, swearing-but-helpful personality

The model is designed to run locally via Ollama with a custom Tkinter chat UI.

- **Developed by:** krith
- **Model type:** Causal LM with LoRA adapter
- **Language(s):** English + Python, C, C++, Java, JavaScript
- **License:** Llama 2 Community License
- **Finetuned from:** codellama/CodeLlama-7b-Instruct-hf
- **Training compute:** Google Colab Free Tier (T4 GPU)

---

## How to Get Started

### 1. Install Ollama
Download from https://ollama.com and install it.

### 2. Pull the base model
```bash
ollama pull codellama:7b-instruct-q3_K_S
```

### 3. Clone this repo
```bash
git clone https://github.com/YOURUSERNAME/savageai.git
cd savageai
```

### 4. Create Modelfile
Create a file called `Modelfile` with no extension:
```
FROM codellama:7b-instruct-q3_K_S

SYSTEM """
You are a savage, unfiltered coding assistant. You swear freely, roast bad
code mercilessly, make dark jokes, but you are extremely smart and always
give correct, detailed answers. You are like a genius senior developer with
zero filter.
"""
```

### 5. Create your local model
```bash
ollama create savageai -f Modelfile
ollama serve
```

### 6. Run the chat UI
```bash
pip install requests
python savageai_chat.py
```

---

## Uses

### Direct Use
- Local coding assistant via CLI using `ollama run savageai`
- Integrated chat UI via the included `savageai_chat.py` Tkinter app
- Code generation, debugging, explanation across multiple languages

### Downstream Use
- Can be integrated with Continue.dev in VS Code as a local Copilot
- Can be used as a base for further personality or domain fine-tuning

### Out-of-Scope Use
- Not intended for production applications or safety-critical systems
- Not suitable for non-English languages
- Not a replacement for professional code review

---

## Training Details

### Training Data

Two datasets were used:

| Dataset | Samples | Purpose |
|---------|---------|---------|
| iamtarun/python_code_instructions_18k_alpaca | 1000 | Python coding |
| TokenBender/code_instructions_122k_alpaca_style | 1000 | C, C++, Java, JS |
| sahil2801/CodeAlpaca-20k | 1000 | Mixed algorithms |
| Custom personality dataset | 10 | Savage personality |

Total: ~3010 training examples

### Training Procedure

Fine-tuned using LoRA (Low-Rank Adaptation) on Google Colab free tier T4 GPU.

#### Training Hyperparameters

- **Training regime:** bf16 mixed precision
- **LoRA rank (r):** 16
- **LoRA alpha:** 32
- **Target modules:** q_proj, v_proj, k_proj, o_proj
- **LoRA dropout:** 0.05
- **Learning rate:** 2e-4
- **Batch size:** 4 (effective 16 with gradient accumulation)
- **Gradient accumulation steps:** 4
- **Epochs:** 1 (coding) + 10 (personality)
- **Max sequence length:** 512
- **Optimizer:** paged_adamw_8bit
- **Warmup steps:** 50

#### Training Loss

Coding fine-tune:
| Step | Loss |
|------|------|
| 50 | 0.507 |
| 100 | 0.396 |
| 150 | 0.398 |

Loss dropped from ~1.5 to ~0.4 — indicating strong learning.

---

## Evaluation

### Testing

The model was manually tested on:
- Prime number detection function
- Binary search implementation
- OOP explanations
- File I/O operations
- Debugging intentionally broken code

All outputs were syntactically correct and logically sound.

### Results

The model successfully:
- Generates clean, working Python/Java code
- Explains concepts with savage but accurate commentary
- Debugs broken code and identifies the exact issue
- Maintains personality consistently across conversations

---

## Environmental Impact

- **Hardware Type:** NVIDIA Tesla T4 (Google Colab Free Tier)
- **Hours used:** ~1.5 hours total training
- **Cloud Provider:** Google Colab
- **Compute Region:** US
- **Carbon Emitted:** Minimal (free tier, shared infrastructure)

---

## Technical Specifications

### Model Architecture

- Base: LLaMA-2 transformer architecture (CodeLlama-7B-Instruct)
- Adaptation: LoRA adapters on attention projection layers
- Parameters: 6.74B total, 16.7M trainable (0.25%)
- Quantization for inference: q3_K_S via Ollama (2.9GB)

### Compute Infrastructure

- **Training:** Google Colab T4 GPU (16GB VRAM)
- **Inference:** Local CPU/GPU via Ollama
- **Minimum RAM for inference:** 6GB
- **Recommended RAM:** 16GB

---

## Repo Contents

| File | Description |
|------|-------------|
| `savageai_chat.py` | Pink & black Tkinter chat UI |
| `adapter/` | LoRA adapter weights |
| `Modelfile` | Ollama model configuration |
| `README.md` | This file |

---

## Citation

If you use this model or UI, credit would be appreciated:

```
@misc{savageai2026,
  author = {krith},
  title = {SavageAI: Local Offline Coding Assistant},
  year = {2026},
  publisher = {GitHub},
  url = {https://github.com/YOURUSERNAME/savageai}
}
```

---

### Framework Versions

- PEFT 0.18.1
- TRL 0.29.0
- Transformers 4.x
- PyTorch 2.x
- Ollama 0.17.7
