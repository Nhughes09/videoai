# 🚀 Deploy to HuggingFace Spaces (FREE GPU!)

## Why HuggingFace Spaces?

- **FREE GPU** - They provide the compute!
- **No downloads** - Models cached on their servers
- **Public URL** - Share with anyone
- **Always on** - Runs 24/7

---

## Quick Deploy (5 minutes)

### Step 1: Create HuggingFace Account

1. Go to https://huggingface.co/join
2. Create free account
3. Verify email

### Step 2: Create New Space

1. Go to https://huggingface.co/new-space
2. Enter name: `video-generator`
3. Select **Gradio** as SDK
4. Select **GPU** hardware (free tier has T4 GPU!)
5. Click "Create Space"

### Step 3: Upload Files

Upload these files to your Space:

- `app_spaces.py` (rename to `app.py`)
- `requirements.txt`

Or use git:

```bash
# Clone your Space
git clone https://huggingface.co/spaces/YOUR_USERNAME/video-generator
cd video-generator

# Copy files
cp /path/to/sora/app_spaces.py app.py
cp /path/to/sora/requirements.txt .

# Create README.md with this content:
cat > README.md << 'EOF'
---
title: AI Video Generator
emoji: 🎬
colorFrom: purple
colorTo: blue
sdk: gradio
sdk_version: 4.44.0
app_file: app.py
pinned: false
license: mit
---
EOF

# Push
git add .
git commit -m "Initial deploy"
git push
```

### Step 4: Wait for Build

- Space builds automatically (~5 minutes)
- Model downloads on first request (~3 minutes)
- Then it's FAST!

---

## Your Public URL

After deploy, your app will be at:

```
https://huggingface.co/spaces/YOUR_USERNAME/video-generator
```

**Share this URL with anyone!**

---

## Upgrade Options

| Tier     | GPU       | Cost     |
| -------- | --------- | -------- |
| Free     | CPU only  | $0       |
| T4 Small | T4 16GB   | $0.40/hr |
| A10G     | A10G 24GB | $1.05/hr |

The T4 is plenty for video generation!
