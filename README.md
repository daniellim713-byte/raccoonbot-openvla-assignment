# RaccoonBot OpenVLA Assignment

## Overview
This project extends the RaccoonBot OpenVLA pipeline with new objects, tasks, and language instructions.

Student ID: 2021741036

---

## 1. Dataset Extension

### What Changed
- **Original**: cylinder only, grasp only, single instruction template
- **Extended**: 3 object types + pick-and-place task + diverse instructions

### New Objects
| Object | MuJoCo Type | Color |
|--------|------------|-------|
| Box (박스) | `box` | Red, Green |
| Can (캔) | `cylinder` | Blue |
| Bottle (페트병) | `capsule` | Yellow |

### New Task: Pick-and-Place
Robot picks up trash and places it on the matching colored pad.

**Language Instructions:**
- "pick up the red trash and place it on the red pad"
- "pick up the blue trash and place it on the blue pad"
- "pick up the yellow trash and place it on the yellow pad"
- "pick up the green trash and place it on the green pad"

### Dataset Stats
- Total episodes: 400 (100 per color)
- Train: 360 / Val: 40
- Steps per episode: 57 (pick-and-place trajectory)

---

## 2. Code Improvement

### 2-1. Pick-and-Place Action Plan
Added `make_pick_and_place_plan()` to extend grasp-only trajectory:

**Before (grasp only):**
**After (pick-and-place):**
### 2-2. Multi-Object Type Support
- Added 3 different object shapes (box, cylinder, capsule)
- Each color mapped to a specific object type and pad position
- More diverse visual observations for VLA training

---

## How to Run

### Server Side (A100)
```bash
# Install dependencies
cd Raccoonbot_Openvla/openvla
pip install .

# Generate dataset
cd Mujoco
python raccoon_recycling_dataset.py

# RLDS conversion
cd raccoon_dataset
python convert_raw_to_openvla_rlds_intermediate.py \
  --raw_root ../raccoon_recycling_colored \
  --out_root recycling_rlds_intermediate \
  --val_ratio 0.1

# Fine-tuning
cd ../../openvla
WANDB_MODE=disabled CUDA_VISIBLE_DEVICES=0 \
torchrun --standalone --nnodes 1 --nproc-per-node 1 vla-scripts/finetune.py \
  --vla_path openvla/openvla-7b \
  --data_root_dir /root/Raccoonbot_Openvla/tensorflow_datasets \
  --dataset_name raccoon_recycling \
  --run_root_dir /root/Raccoonbot_Openvla/openvla/openvla-runs \
  --lora_rank 32 \
  --batch_size 8 \
  --max_steps 30000 \
  --save_steps 30000 \
  --run_id_note raccoon-recycling-v1

# Run inference server
python openvla_server.py \
  --model_path openvla-runs/[checkpoint] \
  --default-unnorm-key raccoon_recycling \
  --host 0.0.0.0 --port 8000 --device cuda
```

### Client Side (Local)
```bash
# SSH tunnel
ssh -L 8000:localhost:8000 -p [PORT] root@[SERVER]

# Run MuJoCo client
python openvla_multicolor_client.py \
  --server_url http://localhost:8000 \
  --xml_path Raccoon_recycling.xml \
  --target_color red \
  --unnorm_key raccoon_recycling \
  --instruction_template "pick up the {color} trash and place it on the {color} pad" \
  --use_viewer
```

---

## Results

### Dataset Generation
- 400 episodes successfully generated
- Success rate: ~90%

### Fine-tuning
- Base model: openvla/openvla-7b
- LoRA rank: 32
- Steps: 30,000
- Training time: ~12 hours on A100 80GB

### MuJoCo Inference
- Model successfully receives language instruction
- Robot executes pick-and-place motion in simulation
