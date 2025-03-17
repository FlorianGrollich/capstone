import torch
import matplotlib.pyplot as plt
from torch.utils.data import DataLoader

from ball_tracking.loading_model import load_model
from model_training.dataset.track_net_dataset import TrackNetDataset

dataset = TrackNetDataset(root_dir='dataset',  target_size=(576, 1024))
dataloader = DataLoader(dataset, batch_size=8, shuffle=True)
model = load_model()

model.eval()
with torch.no_grad():
    sample_images, sample_heatmaps = next(iter(dataloader))
    pred_heatmaps = model(sample_images)

    # Plot frames
    for i in range(3):
        plt.figure(figsize=(8, 8))  # Larger figure size
        plt.imshow(sample_images[0, i * 3:(i + 1) * 3].mean(dim=0).cpu(), cmap='gray')
        plt.title(f'Frame {i + 1}')
        plt.show()

    # Plot heatmaps
    for i in range(3):
        plt.figure(figsize=(8, 8))
        plt.imshow(pred_heatmaps[0, i].cpu(), cmap='hot')
        plt.title(f'Heatmap {i + 1}')
        plt.show()