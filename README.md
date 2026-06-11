# RaccoonBot OpenVLA Assignment

## Overview
This project extends the RaccoonBot OpenVLA pipeline with new objects, tasks, and language instructions for a recycling robot scenario.

**Student ID:** 2021741036  
**GitHub:** https://github.com/daniellim713-byte/raccoonbot-openvla-assignment

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
- "grab the blue can and put it on the blue pad"
- "collect the yellow bottle and move it to the yellow area"
- "sort the green box into the green zone"
- "clean up the red box by placing it on the red pad"

### Dataset Stats
- Total episodes: 400 (100 per color)
- Train: 360 / Val: 40
- Steps per episode: 57 (pick-and-place trajectory)
- Object spawn range: x(-0.10~0.10), y(0.16~0.20)

---

## 2. Code Improvement

### 2-1. Pick-and-Place Action Plan
Added `make_pick_and_place_plan()` to extend grasp-only trajectory from 3 steps to 7 steps.

**Before (grasp only):** Move above → Move down → Close gripper

**After (pick-and-place):** Move above → Move down → Close gripper → Lift → Move to pad → Lower → Open gripper

### 2-2. Diverse Language Instructions (`diverse_instructions.py`)
Extended from single template to 6 randomized templates per color/object type.

**Before:** `"grasp the {color} cylinder"`  
**After:** 6 templates including grab, collect, sort, clean up, place

### 2-3. Gripper Control Logic (`openvla_multicolor_client.py`)
VLA model gripper output was unstable. Added position-based auto-close logic.

**Grasp condition:** `dx < 3cm AND ee_y >= obj_y - 1cm AND ee_z <= 2.5cm`  
**After grasp:** Automatically lift (z-axis up) while keeping gripper closed  
**Result:** Successful pick-and-place in MuJoCo simulation ✓

### 2-4. Object Spawn Range Fix (`openvla_multicolor_client.py`)
Training data used y_range(0.16~0.20) but inference used y_range(0.16~0.25), causing model to fail finding objects.

**Fix:** Set `DEFAULT_OBJECT_Y_RANGE = (0.16, 0.20)` to match training distribution

---

## How to Run

### Server Side (A100)
```bash
cd Raccoonbot_Openvla/openvla
pip install .

cd Mujoco
python raccoon_recycling_dataset.py

cd raccoon_dataset
python convert_raw_to_openvla_rlds_intermediate.py \
  --raw_root ../raccoon_recycling_colored \
  --out_root recycling_rlds_intermediate \
  --val_ratio 0.1

cd ../rlds_dataset_builder/raccoon_recycling
tfds build --overwrite

cd ../../openvla
WANDB_MODE=disabled CUDA_VISIBLE_DEVICES=0 \
torchrun --standalone --nnodes 1 --nproc-per-node 1 vla-scripts/finetune.py \
  --vla_path openvla/openvla-7b \
  --data_root_dir /root/Raccoonbot_Openvla/tensorflow_datasets \
  --dataset_name raccoon_recycling \
  --run_root_dir /root/Raccoonbot_Openvla/openvla/openvla-runs \
  --lora_rank 32 --batch_size 8 --max_steps 30000 --save_steps 30000 \
  --run_id_note raccoon-recycling-v1

python openvla_server.py \
  --model_path openvla-runs/[checkpoint] \
  --default-unnorm-key raccoon_recycling \
  --host 0.0.0.0 --port 8000 --device cuda
```

### Client Side (Local)
```bash
ssh -L 8000:localhost:8000 -p [PORT] root@[SERVER]

python openvla_multicolor_client.py \
  --server_url http://localhost:8000 \
  --xml_path Raccoon_recycling.xml \
  --target_color red \
  --unnorm_key raccoon_recycling \
  --instruction_template "pick up the {color} trash and place it on the {color} pad" \
  --use_viewer \
  --max_steps 150
```

---

## Results

### Dataset Generation
- 400 episodes successfully generated / Success rate: ~90%

### Fine-tuning
- Base model: openvla/openvla-7b / LoRA rank: 32 / Steps: 30,000 / ~12 hours on A100 80GB

### MuJoCo Inference
- Successfully picks up red object and places it on red pad ✓
