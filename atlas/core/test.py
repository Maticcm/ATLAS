import torch

print("Before:", torch.cuda.memory_allocated() / 1024**2)

x = torch.randn(10000, 10000, device="cuda")

print("After:", torch.cuda.memory_allocated() / 1024**2)