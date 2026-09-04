import torch

def gpu_batch_ib_classification(highs: torch.Tensor, lows: torch.Tensor, currents: torch.Tensor) -> torch.Tensor:
    return torch.zeros_like(highs, dtype=torch.int32)
