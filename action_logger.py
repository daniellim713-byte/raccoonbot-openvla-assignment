import csv
import time
import os
from datetime import datetime

class ActionLogger:
    """
    Records timing and action logs for each inference step.
    Saves to CSV for before/after analysis.
    """
    def __init__(self, output_dir="logs"):
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.filepath = os.path.join(output_dir, f"action_log_{timestamp}.csv")
        self.start_time = None
        self.step_times = []
        
        with open(self.filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'step', 'timestamp', 'inference_time_ms',
                'dx', 'dy', 'dz', 'gripper',
                'target_x', 'target_y', 'target_z',
                'success'
            ])
        print(f"[LOGGER] Action log started: {self.filepath}")

    def log_step(self, step, action, target, inference_time_ms, success=None):
        with open(self.filepath, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                step,
                datetime.now().strftime("%H:%M:%S.%f"),
                f"{inference_time_ms:.1f}",
                f"{action[0]:.4f}",
                f"{action[1]:.4f}",
                f"{action[2]:.4f}",
                f"{action[6]:.4f}",
                f"{target[0]:.4f}",
                f"{target[1]:.4f}",
                f"{target[2]:.4f}",
                success
            ])

    def summary(self, total_steps, success):
        if self.step_times:
            avg_ms = sum(self.step_times) / len(self.step_times)
            print(f"[LOGGER] Summary: {total_steps} steps | avg inference: {avg_ms:.1f}ms | success: {success}")
            print(f"[LOGGER] Log saved: {self.filepath}")
