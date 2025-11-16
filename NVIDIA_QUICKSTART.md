# NVIDIA API Quick Start Guide

## ✅ Setup Checklist (5 minutes)

### Step 1: Get API Key
```bash
# This command opens the signup page
open https://build.nvidia.com/
```

1. Sign up / Login
2. Browse models → Find any model (e.g., "Nemotron Nano")
3. Click **"Get API Key"** (top right)
4. Copy the key (starts with `nvapi-...`)

---

### Step 2: Add Key to .env
```bash
# Edit .env file
nano .env

# Find line 18 and replace:
NVIDIA_API_KEY=nvapi-YOUR_ACTUAL_KEY_HERE

# Save: Ctrl+O, Enter, Ctrl+X
```

---

### Step 3: Test Connection
```bash
./venv/bin/python scripts/test_nemotron.py
```

**Expected output:**
```
✅ SUCCESS! Nemotron is working!
```

---

## 🚀 Usage Examples

### 1. Quick Test (Basic)
```bash
./venv/bin/python evolution/nemotron_scorer.py
```

### 2. Use Different Models
```python
from evolution.nemotron_scorer import NemotronScorer

# Fast model (cheapest, fastest)
scorer = NemotronScorer(model_preset='fast')

# Smart model (best reasoning)
scorer = NemotronScorer(model_preset='smart')

# Multilingual (119 languages)
scorer = NemotronScorer(model_preset='multilingual')

# Custom model
scorer = NemotronScorer('qwen/qwen3-coder-480b-a35b-instruct')
```

### 3. Classify Events
```python
# Auto-classify event type
result = scorer.classify_event_type(
    "China Minsheng Bank missed interest payment deadline"
)

print(result)
# Output: {
#   "type": "missed_payment",
#   "confidence": 0.92,
#   "reasoning": "Payment deadline was missed"
# }
```

### 4. Detect Causality
```python
# Check if event A caused event B
score, explanation = scorer.compute_causal_score(event1, event2)

print(f"Causality: {score:.2f}")
print(f"Because: {explanation}")
```

### 5. Assess Risk
```python
risk = scorer.assess_risk_level(event)

print(f"Severity: {risk['severity']}")
print(f"Systemic Risk: {risk['systemic_risk']:.2f}")
```

---

## 📊 Model Presets

| Preset | Model | Best For | Speed | Cost |
|--------|-------|----------|-------|------|
| **`fast`** | Nemotron Nano 9B | High-volume processing | ⚡⚡⚡⚡⚡ | $ |
| **`smart`** | DeepSeek V3.1 | Complex reasoning | ⚡⚡⚡ | $$ |
| **`multilingual`** | Qwen3 Next 80B | Non-English text | ⚡⚡⚡⚡ | $$ |
| **`structured`** | Qwen3 Coder 480B | JSON extraction | ⚡⚡⚡ | $$$ |

---

## 🛠️ Troubleshooting

### Problem: "NVIDIA_API_KEY not set"
**Solution:**
```bash
# Check if key is in .env
cat .env | grep NVIDIA_API_KEY

# Should show:
NVIDIA_API_KEY=nvapi-xxxxxxxxxxxxx

# If it shows "your_api_key_here", replace it with your real key
```

### Problem: "Invalid API key"
**Solution:**
1. Go to https://build.nvidia.com/
2. Click your profile → "API Keys"
3. Generate new key
4. Update `.env` file

### Problem: "Rate limit exceeded"
**Solution:**
- Free tier has limits (~50 requests/min)
- Wait 1 minute and retry
- Use `fast` model for high-volume tasks
- Consider upgrading to paid tier

### Problem: "Model not found"
**Solution:**
- Check model name at https://build.nvidia.com/explore/discover
- Models change over time
- Use one of our tested presets: `fast`, `smart`, `multilingual`, `structured`

---

## 💡 Best Practices

### 1. Choose Right Model for Task
```python
# Event classification (simple) → fast
scorer_fast = NemotronScorer('fast')

# Causal analysis (complex) → smart
scorer_smart = NemotronScorer('smart')

# Chinese news (language) → multilingual
scorer_multi = NemotronScorer('multilingual')
```

### 2. Cache Results
```python
import json

# Save LLM results to avoid re-calling
results = {}
for event in events:
    if event['id'] not in results:
        results[event['id']] = scorer.classify_event_type(event['description'])

# Save to file
with open('llm_cache.json', 'w') as f:
    json.dump(results, f)
```

### 3. Use Low Temperature
```python
# In nemotron_scorer.py, all API calls use:
temperature=0.1  # Deterministic
temperature=0.2  # Slightly more creative

# NEVER use >0.5 for financial analysis!
```

---

## 📝 Real-World Example

### Enhance Your Evolution Pipeline

```python
# Original evolution method (rule-based)
from evolution.methods import EventEvolutionScorer

basic_scorer = EventEvolutionScorer(events, entities)
score, components = basic_scorer.compute_evolution_score(evt1, evt2)

# Enhanced with LLM (intelligent)
from evolution.nemotron_scorer import NemotronScorer

llm_scorer = NemotronScorer(model_preset='smart')
causality, reason = llm_scorer.compute_causal_score(evt1, evt2)

# Combine both!
final_score = (
    0.7 * score +                    # Rule-based features
    0.3 * causality                   # LLM reasoning
)

print(f"Final score: {final_score:.2f}")
print(f"LLM reasoning: {reason}")
```

---

## 🔗 Resources

- **NVIDIA Build:** https://build.nvidia.com/
- **Model Catalog:** https://build.nvidia.com/explore/discover
- **API Docs:** https://docs.api.nvidia.com/
- **Pricing:** https://build.nvidia.com/pricing
- **Our Model Guide:** [NVIDIA_MODELS.md](evolution/NVIDIA_MODELS.md)

---

## 🎯 Next Steps

After testing works:

1. **Read:** [NVIDIA_MODELS.md](evolution/NVIDIA_MODELS.md) for detailed comparison
2. **Integrate:** Add LLM scoring to your evolution pipeline
3. **Optimize:** Use right model for each task (fast vs smart)
4. **Scale:** Cache results, batch requests
5. **Analyze:** Compare LLM vs rule-based results

---

**Last Updated:** 2025-01-13
**Status:** ✅ All model presets tested and working
