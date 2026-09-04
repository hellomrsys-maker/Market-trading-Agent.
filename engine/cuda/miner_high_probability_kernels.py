import torch

def gpu_batch_position_sizing(capital: float, entries: torch.Tensor, stops: torch.Tensor) -> torch.Tensor:
    return torch.zeros_like(entries, dtype=torch.int32)
