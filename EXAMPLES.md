# Example Usage

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Test Your System

```bash
python test_system.py
```

### 3. Generate Your First Video

#### Option A: Command Line (CLI)

```bash
python generate_video.py \
  --prompt "Ocean waves crashing on a beach at golden hour" \
  --duration 10 \
  --resolution 1080p \
  --style cinematic
```

#### Option B: Web Interface (Recommended)

```bash
python app.py
```

Then open http://localhost:7860 in your browser.

---

## 📋 Example Prompts

### Nature & Landscapes

```bash
# Beautiful sunset over ocean
python generate_video.py \
  --prompt "Spectacular sunset over ocean with vibrant orange and purple clouds reflecting on calm water"

# Mountain time-lapse
python generate_video.py \
  --prompt "Time-lapse of clouds flowing over mountain peaks at dawn" \
  --style cinematic
```

### Science & Technology

```bash
# DNA visualization
python generate_video.py \
  --prompt "DNA double helix rotating in 3D space with glowing protein molecules" \
  --style photorealistic

# Cell division
python generate_video.py \
  --prompt "Microscopic view of a cell dividing mitosis with chromosomes visible" \
  --duration 15
```

### Urban & Architecture

```bash
# Futuristic city
python generate_video.py \
  --prompt "Futuristic city at night with flying cars neon lights and holographic advertisements" \
  --style cinematic \
  --fps 30

# City street
python generate_video.py \
  --prompt "Busy city street in Tokyo at night with neon signs and people walking" \
  --resolution 1080p
```

### Abstract & Artistic

```bash
# Abstract patterns
python generate_video.py \
  --prompt "Abstract flowing liquid gold and silver mixing in slow motion" \
  --style artistic

# Particles
python generate_video.py \
  --prompt "Glowing particles forming and dissolving in space creating beautiful patterns" \
  --duration 20
```

---

## ⚙️ CLI Options

### Basic Options

- `--prompt`: Text description (required)
- `--output`: Output file path
- `--duration`: Length in seconds (1-60, default: 10)
- `--fps`: Frames per second (24/30/60, default: 30)
- `--resolution`: Output size (720p/1080p/4k, default: 1080p)

### Style Options

- `--style`: Visual style (cinematic/documentary/animated/artistic/photorealistic)

### Advanced Options

- `--keyframes`: Number of keyframes (default: 5)
- `--seed`: Random seed for reproducibility
- `--no-upscale`: Skip upscaling step
- `--no-color-grade`: Skip color grading
- `--model-dir`: Model cache directory

### Performance Options

- `--log-level`: Logging verbosity (DEBUG/INFO/WARNING/ERROR)

---

## 🎨 Pro Tips

### Getting Better Results

1. **Be Specific**:
   - Bad: "a city"
   - Good: "a futuristic city at sunset with flying cars and glowing skyscrapers"

2. **Add Details About Lighting**:
   - "during golden hour"
   - "with dramatic studio lighting"
   - "at night with moonlight"

3. **Specify Camera Movement**:
   - "camera slowly zooming in"
   - "static shot"
   - "slow pan across the scene"

4. **Mention Style Explicitly**:
   - "cinematic film quality"
   - "photorealistic"
   - "like a nature documentary"

### Resolution Strategy

- **Testing**: Start with 720p for fast iterations
- **Preview**: Use 1080p for quality check
- **Final**: Generate 4K if your hardware supports it

### Duration Guidelines

- **Short Tests**: 5-10 seconds (fast generation)
- **Standard**: 15-30 seconds (good balance)
- **Long Form**: 45-60 seconds (requires patience)

### Seed Usage

```bash
# Generate reproducible videos
python generate_video.py --prompt "sunset" --seed 42

# Use same seed for variations
python generate_video.py --prompt "sunset in summer" --seed 42
python generate_video.py --prompt "sunset in winter" --seed 42
```

---

## 🐛 Troubleshooting

### Out of Memory

```bash
# Use lower resolution
python generate_video.py --prompt "..." --resolution 720p

# Reduce keyframes
python generate_video.py --prompt "..." --keyframes 3
```

### Slow Generation

- First run downloads models (one-time, 10-30 min)
- Subsequent runs use cached models
- CPU-only mode is 5-10× slower than GPU

### Poor Quality

- Increase keyframes: `--keyframes 7`
- Use better prompt engineering
- Ensure color grading is enabled (default)

---

## 📊 Expected Performance

| Hardware | Resolution | Duration | Time    |
| -------- | ---------- | -------- | ------- |
| RTX 4090 | 1080p      | 10s      | ~3 min  |
| RTX 3060 | 1080p      | 10s      | ~8 min  |
| M1 Mac   | 1080p      | 10s      | ~15 min |
| CPU Only | 1080p      | 10s      | ~45 min |
| Colab T4 | 1080p      | 10s      | ~10 min |

_Times are approximate and vary based on prompt complexity_

---

## 🔄 Batch Generation

Generate multiple videos:

```bash
#!/bin/bash

# Create batch_generate.sh

prompts=(
  "Ocean waves at sunset"
  "Mountain landscape with fog"
  "City street at night"
)

for i in "${!prompts[@]}"; do
  python generate_video.py \
    --prompt "${prompts[$i]}" \
    --output "outputs/video_$i.mp4" \
    --duration 10
done
```

---

## 📦 Output Files

Videos are saved to `outputs/` directory:

- Format: MP4 (H.264)
- Quality: CRF 18 (near-lossless)
- No watermarks
- Compatible with all video players

Check file size:

```bash
ls -lh outputs/
```

---

Happy creating! 🎬✨
