# NVIDIA API Models for FE-EKG

## Best Models for Financial Event Analysis

### 🏆 **Recommended Models**

#### 1. **DeepSeek V3.1** (Best Overall)
```python
model = "deepseek-ai/deepseek-v3.1"
```
**Strengths:**
- ✅ Hybrid reasoning (Think/Non-Think modes)
- ✅ Strong tool calling & agentic capabilities
- ✅ 128K context window
- ✅ Excellent for financial analysis

**Best for:** Causal analysis, risk assessment, complex reasoning

---

#### 2. **NVIDIA Nemotron Nano 9B v2** (Fastest)
```python
model = "nvidia/nvidia-nemotron-nano-9b-v2"
```
**Strengths:**
- ✅ Very fast inference
- ✅ Hybrid Transformer-Mamba architecture
- ✅ Good reasoning for its size
- ✅ Low cost per token

**Best for:** High-volume event classification, real-time analysis

---

#### 3. **Qwen3 Next 80B** (Multilingual)
```python
model = "qwen/qwen3-next-80b-a3b-instruct"
```
**Strengths:**
- ✅ Ultra-long context (supports very long documents)
- ✅ 119 languages supported
- ✅ MoE architecture (efficient)
- ✅ Strong reasoning

**Best for:** Multi-language financial news analysis, long documents

---

#### 4. **Qwen3 Coder 480B** (Code + Analysis)
```python
model = "qwen/qwen3-coder-480b-a35b-instruct"
```
**Strengths:**
- ✅ Excellent at structured output (JSON, code)
- ✅ 256K context window
- ✅ Strong agentic coding
- ✅ Best for precise data extraction

**Best for:** Parsing financial documents, extracting structured data

---

### 📊 **Model Comparison Table**

| Model | Size | Speed | Reasoning | Financial Analysis | Cost |
|-------|------|-------|-----------|-------------------|------|
| **DeepSeek V3.1** | Large | Medium | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | $$ |
| **Nemotron Nano 9B** | 9B | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | $ |
| **Qwen3 Next 80B** | 80B | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | $$ |
| **Qwen3 Coder 480B** | 480B | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | $$$ |
| **Meta Llama 3.1 70B** | 70B | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | $$ |

---

## 🎯 **Use Case Recommendations**

### Event Classification
**Best:** Nemotron Nano 9B v2 (fast, accurate enough)
```python
scorer = NemotronScorer()
scorer.model = "nvidia/nvidia-nemotron-nano-9b-v2"
result = scorer.classify_event_type(description)
```

### Causal Analysis
**Best:** DeepSeek V3.1 (reasoning specialist)
```python
scorer.model = "deepseek-ai/deepseek-v3.1"
score, reason = scorer.compute_causal_score(evt_a, evt_b)
```

### Risk Assessment
**Best:** DeepSeek V3.1 or Qwen3 Coder 480B
```python
scorer.model = "deepseek-ai/deepseek-v3.1"
risk = scorer.assess_risk_level(event)
```

### Multilingual News Analysis
**Best:** Qwen3 Next 80B (119 languages)
```python
scorer.model = "qwen/qwen3-next-80b-a3b-instruct"
# Works with Chinese Evergrande news!
```

### High-Volume Processing
**Best:** Nemotron Nano 9B (fastest, cheapest)
```python
scorer.model = "nvidia/nvidia-nemotron-nano-9b-v2"
# Process 1000s of events quickly
```

---

## 🔧 **How to Change Models**

### Option 1: In Code
```python
from evolution.nemotron_scorer import NemotronScorer

scorer = NemotronScorer()

# Change model
scorer.model = "deepseek-ai/deepseek-v3.1"

# Use it
result = scorer.classify_event_type("...")
```

### Option 2: Edit .env File
```bash
# Add to .env:
NVIDIA_DEFAULT_MODEL=deepseek-ai/deepseek-v3.1
```

Then update `nemotron_scorer.py`:
```python
self.model = os.getenv('NVIDIA_DEFAULT_MODEL', 'nvidia/nvidia-nemotron-nano-9b-v2')
```

---

## 💡 **Performance Tips**

### 1. **Use Temperature Wisely**
- Classification: `temperature=0.1` (deterministic)
- Creative analysis: `temperature=0.3-0.5`
- Never use >0.7 for financial analysis

### 2. **Optimize Token Usage**
- Use smaller models for simple tasks
- Use `max_tokens` to limit response length
- Cache frequent queries

### 3. **Batch Processing**
- Send multiple requests in parallel
- Use async if processing >100 events

---

## 🚨 **Rate Limits & Costs**

NVIDIA free tier limits:
- **Free credits:** Limited (check your dashboard)
- **Rate limit:** ~50 requests/minute
- **Token limit:** Varies by model

**Tip:** For production, consider:
- Hosting your own model (RTX GPU)
- Using NVIDIA NIM enterprise
- Caching LLM responses

---

## 📝 **Example: Multi-Model Strategy**

Use different models for different tasks:

```python
class MultiModelScorer:
    def __init__(self):
        self.fast_model = "nvidia/nvidia-nemotron-nano-9b-v2"
        self.smart_model = "deepseek-ai/deepseek-v3.1"

    def classify(self, text):
        # Use fast model for simple task
        scorer.model = self.fast_model
        return scorer.classify_event_type(text)

    def analyze_causality(self, evt_a, evt_b):
        # Use smart model for complex task
        scorer.model = self.smart_model
        return scorer.compute_causal_score(evt_a, evt_b)
```

---

## 🔗 **Resources**

- NVIDIA Build: https://build.nvidia.com/
- API Docs: https://docs.api.nvidia.com/
- Model Catalog: https://build.nvidia.com/explore/discover
- Pricing: https://build.nvidia.com/pricing

---

**Last Updated:** 2025-01-13
**Tested Models:** All models listed above confirmed working
