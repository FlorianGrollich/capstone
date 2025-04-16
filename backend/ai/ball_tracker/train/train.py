import os
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, random_split

from capstone.backend.ai.ball_tracker.track_net import TrackNetV4
from capstone.backend.ai.ball_tracker.train.dataset.track_net_dataset import TrackNetDataset

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
# Create weights directory if it doesn't exist
os.makedirs("weights", exist_ok=True)
model = TrackNetV4().to(device)
dataset = TrackNetDataset(root_dir='merged-final', target_size=(720,1280))
dataloader = DataLoader(dataset, batch_size=16, shuffle=True)
# Define the dataset split
dataset_size = len(dataset)
train_size = int(0.9 * dataset_size)
test_size = dataset_size - train_size

train_dataset, test_dataset = random_split(dataset, [train_size, test_size])
train_loader = DataLoader(train_dataset, batch_size=8, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=8, shuffle=False)

# Loss and optimizer
pos_weight = torch.tensor([100]).to(device)
criterion = nn.BCEWithLogitsLoss(pos_weight=pos_weight)
optimizer = optim.Adam(model.parameters(), lr=1e-4)

# Training loop
best_loss = float('inf')
trigger_times = 0
patience = 5
num_epochs = 1000

for epoch in range(num_epochs):
    model.train()
    total_train_loss = 0

    for batch_idx, (images, heatmaps) in enumerate(train_loader):
        images, heatmaps = images.to(device), heatmaps.to(device)

        pred_heatmaps = model(images)
        loss = criterion(pred_heatmaps, heatmaps)
        total_train_loss += loss.item()

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        if batch_idx % 10 == 0:
            print(f'Epoch [{epoch+1}/{num_epochs}], Batch [{batch_idx}/{len(train_loader)}], Loss: {loss.item():.4f}')

    avg_train_loss = total_train_loss / len(train_loader)
    print(f'Epoch [{epoch+1}/{num_epochs}] Average Training Loss: {avg_train_loss:.4f}')

    # Evaluation
    model.eval()
    total_test_loss = 0

    with torch.no_grad():
        for images, heatmaps in test_loader:
            images, heatmaps = images.to(device), heatmaps.to(device)
            pred_heatmaps = model(images)
            loss = criterion(pred_heatmaps, heatmaps)
            total_test_loss += loss.item()

    avg_test_loss = total_test_loss / len(test_loader)
    print(f'Epoch [{epoch+1}/{num_epochs}] Average Testing Loss: {avg_test_loss:.4f}')

    # Save best model
    if avg_test_loss < best_loss:
        best_loss = avg_test_loss
        trigger_times = 0
        torch.save(model.state_dict(), 'weights/best.pth')
        print(f"Best model saved at epoch {epoch+1}")
    else:
        trigger_times += 1
        print(f'No improvement in epoch {epoch+1} ({trigger_times}/{patience})')

    if trigger_times >= patience:
        print("Early stopping triggered.")
        break

# Save final model
torch.save(model.state_dict(), 'weights/last.pth')
print("Last model saved.")