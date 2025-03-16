import torch

import torch.nn.functional as F
from torch.utils.data import DataLoader

from model.track_net_v4 import TrackNetV4
from model_training.dataset.track_net_dataset import TrackNetDataset


def weighted_bce_loss(pred, target, pos_weight=100):
    bce = F.binary_cross_entropy(pred, target, reduction='none')
    weights = target * pos_weight + (1 - target)
    return (bce * weights).mean()


device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = TrackNetV4().to(device)
dataset = TrackNetDataset(root_dir='dataset', target_size=(576, 1024))
dataloader = DataLoader(dataset, batch_size=8, shuffle=True)

optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
num_epochs = 50

for epoch in range(num_epochs):
    model.train()
    total_loss = 0
    for batch_idx, (images, heatmaps) in enumerate(dataloader):
        images, heatmaps = images.to(device), heatmaps.to(device)  # (batch, 9, H, W), (batch, 3, H, W)

        pred_heatmaps = model(images)  # (batch, 3, H, W)

        loss = weighted_bce_loss(pred_heatmaps, heatmaps)
        total_loss += loss.item()

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        if batch_idx % 10 == 0:
            print(f'Epoch [{epoch + 1}/{num_epochs}], Batch [{batch_idx}/{len(dataloader)}], Loss: {loss.item():.4f}')

    avg_loss = total_loss / len(dataloader)
    print(f'Epoch [{epoch + 1}/{num_epochs}] Average Loss: {avg_loss:.4f}')

torch.save(model.state_dict(), 'tracknetv4.pth')
