# 🌐 API-Based Generation Guide

## ⚡ Quick Start (NO GPU NEEDED!)

### The Fastest Way to Generate Videos

Instead of downloading models and using local GPU, use **FREE** cloud APIs:

```bash
# 1. Get FREE HuggingFace token (30 seconds)
#    Visit: https://huggingface.co/settings/tokens
#    Click "New token" → Copy token

# 2. Set environment variable
export HF_TOKEN=your_token_here

# 3. Generate video!
python generate_api.py --prompt "Ocean waves at sunset"
```

**That's it!** No model downloads, no GPU needed.

---

## 🆚 API vs Local Comparison

| Feature              | API (HuggingFace)        | Local Generation      |
| -------------------- | ------------------------ | --------------------- |
| **GPU Required**     | ❌ No                    | ✅ Yes (or very slow) |
| **Setup Time**       | 1 minute                 | 30-60 minutes         |
| **Generation Speed** | Fast (cloud GPUs)        | Depends on your GPU   |
| **Cost**             | FREE                     | FREE                  |
| **Privacy**          | Prompts sent to HF       | 100% private          |
| **Rate Limits**      | Some limits on free tier | Unlimited             |
| **Quality**          | Excellent (Wan-2.1)      | Excellent (SVD)       |

---

## 📋 Available Methods

### 1. HuggingFace API (FREE, Recommended)

**Best for**: Quick results without GPU

```bash
python generate_api.py \
  --prompt "Futuristic city at night" \
  --method hf \
  --duration 10
```

**Models used**:

- Wan-2.1 T2V (Sora-level quality)
- Open-Sora 2.0
- CogVideoX-1.5

**Limits**: Generous free tier, may queue during peak times

### 2. Replicate API ($10 Free Credits)

**Best for**: When HF is busy, need faster processing

```bash
# Get $10 free credits at: https://replicate.com
export REPLICATE_API_TOKEN=your_token

python generate_api.py \
  --prompt "Mountain landscape with clouds" \
  --method replicate \
  --duration 10
```

**Cost after free credits**: ~$0.002-0.004 per second of video

- 10s video = ~$0.02-0.04
- $10 gets you ~250-500 videos

### 3. Local Generation (No API)

**Best for**: Unlimited generations, privacy, offline use

```bash
python generate_api.py \
  --prompt "DNA helix rotating" \
  --method local \
  --duration 10
```

This uses the local models (same as `generate_video.py`)

### 4. Auto (Smart Fallback)

**Best for**: Just works™

```bash
python generate_api.py \
  --prompt "Sunset over ocean" \
  --method auto
```

**Order**: Tries HuggingFace → Replicate → Local

---

## 🔑 Getting API Tokens

### HuggingFace (100% FREE)

1. Go to: https://huggingface.co/join
2. Sign up (free account)
3. Go to: https://huggingface.co/settings/tokens
4. Click "New token"
5. Name it "sora-video"
6. Copy token
7. Set: `export HF_TOKEN=hf_xxx...`

**Permanent setup**:

```bash
# Add to ~/.zshrc or ~/.bashrc
echo 'export HF_TOKEN=your_token_here' >> ~/.zshrc
source ~/.zshrc
```

### Replicate ($10 Free Credits)

1. Go to: https://replicate.com
2. Sign up
3. Get $10 free credits automatically
4. Go to: https://replicate.com/account/api-tokens
5. Copy token
6. Set: `export REPLICATE_API_TOKEN=r8_xxx...`

---

## 💡 Usage Examples

### Quick Test (10 seconds)

```bash
python generate_api.py --prompt "Beautiful sunset"
```

### Longer Video (30 seconds)

```bash
python generate_api.py \
  --prompt "City street at night with people walking" \
  --duration 30
```

### Force Specific Method

```bash
# Use only HuggingFace
python generate_api.py --prompt "Mountain" --method hf

# Use only Replicate (costs credits)
python generate_api.py --prompt "Ocean" --method replicate

# Use only local models
python generate_api.py --prompt "Space" --method local
```

### Save to Specific Location

```bash
python generate_api.py \
  --prompt "Flower blooming" \
  --output ~/Desktop/my_video.mp4
```

---

## 🚀 Recommended Workflow

### For Beginners (No GPU)

```bash
# Use API - instant start, no setup
python generate_api.py --prompt "your idea"
```

### For Privacy-Conscious Users

```bash
# Use local generation
python generate_video.py --prompt "your idea"
```

### For Power Users

```bash
# Use hybrid: API for speed, local for batch
python generate_api.py --prompt "quick test" --method hf
python generate_video.py --prompt "final output" --resolution 4k
```

---

## 📊 Expected Results

### HuggingFace API

- **Speed**: 30 seconds - 3 minutes
- **Quality**: Excellent (Wan-2.1 is Sora-level)
- **Resolution**: 1080p
- **FPS**: 24-30
- **Duration**: 10-14s clips (stitched for longer)

### Replicate API

- **Speed**: 1-2 minutes
- **Quality**: Excellent
- **Resolution**: 1080p
- **FPS**: 30
- **Duration**: Up to 60s

### Local Generation

- **Speed**: 5-45 minutes (depends on GPU)
- **Quality**: Excellent
- **Resolution**: Up to 4K
- **FPS**: 24/30/60
- **Duration**: Up to 60s

---

## 🐛 Troubleshooting

### "No HF_TOKEN found"

```bash
# Make sure token is set
echo $HF_TOKEN

# If empty, set it:
export HF_TOKEN=hf_your_token_here
```

### "API rate limit exceeded"

- Wait a few minutes
- Try Replicate instead: `--method replicate`
- Use local: `--method local`

### "Generation takes a long time"

- APIs can queue during peak hours
- Try different time of day
- Use local generation for guaranteed speed

### "Video quality is low"

- Improve your prompt (be specific)
- Try different model/method
- Use local with higher settings

---

## 🎯 Which Method Should I Use?

**Choose HuggingFace if**:

- ✅ You want FREE unlimited (with limits)
- ✅ You don't have a GPU
- ✅ You want instant setup
- ✅ You don't mind prompts being sent to API

**Choose Replicate if**:

- ✅ HuggingFace is slow/busy
- ✅ You need guaranteed speed
- ✅ $10 gets 200+ videos (affordable)
- ✅ You want best quality APIs

**Choose Local if**:

- ✅ You have a decent GPU
- ✅ You want unlimited generations
- ✅ You care about privacy
- ✅ You want offline capability
- ✅ You want full control

---

## 💰 Cost Breakdown

### HuggingFace

- **Free tier**: Generous
- **Paid tiers**: Available but not needed for most users
- **Cost per video**: $0 (free)

### Replicate

- **Free credits**: $10 on signup
- **Cost per 10s video**: ~$0.02-0.04
- **$10 gets you**: 250-500 videos
- **After credits**: Pay as you go

### Local

- **Electricity**: ~$0.01-0.05 per video (GPU usage)
- **Hardware**: One-time investment (GPU)
- **Marginal cost**: Nearly $0 per video

---

**Bottom Line**: Start with HuggingFace API for instant results, then switch to local for unlimited generation! 🚀
