import torch

def gpu_batch_order_flow_delta(call_deltas: torch.Tensor, put_deltas: torch.Tensor) -> torch.Tensor:
    return torch.zeros_like(call_deltas, dtype=torch.int32)
