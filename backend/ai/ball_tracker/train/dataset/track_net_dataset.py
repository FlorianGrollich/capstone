import os
import torch
from torch.utils.data import Dataset, DataLoader
import numpy as np
import torchvision.transforms as transforms
from PIL import Image


def generate_heatmap(center_x, center_y, h, w, sigma=5):
    x, y = np.meshgrid(np.arange(w), np.arange(h))
    heatmap = np.exp(-((x - center_x) ** 2 + (y - center_y) ** 2) / (2 * sigma ** 2))
    return heatmap / heatmap.max()

class TrackNetDataset(Dataset):
    def __init__(self, root_dir, target_size=(288, 512), transform=None):

        self.root_dir = root_dir
        self.target_size = target_size
        self.transform = transform
        self.frame_folders = sorted([f for f in os.listdir(root_dir) if f.startswith('frame')])

        # Define the transform with the target size if none provided
        if self.transform is None:
            self.transform = transforms.Compose([
                transforms.Resize(self.target_size),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
            ])

    def __len__(self):
        return len(self.frame_folders)

    def __getitem__(self, idx):
        frame_folder = os.path.join(self.root_dir, self.frame_folders[idx])
        images = []
        heatmaps = []
        h, w = self.target_size  # Use the target size for heatmaps

        for i in range(3):  # Load 3 consecutive frames (image-0 to image-2)
            subfolder = os.path.join(frame_folder, f'image-{i}')
            img_path = os.path.join(subfolder, 'image.jpg')
            label_path = os.path.join(subfolder, 'label.txt')

            # Load image with fallback for missing files
            try:
                img = Image.open(img_path).convert('RGB')
            except FileNotFoundError:
                print(f"Image file {img_path} not found, using blank image")
                img = Image.fromarray(np.zeros((h, w, 3), dtype=np.uint8))  # Blank RGB image with target size
            if self.transform:
                img = self.transform(img)
            images.append(img)

            # Load and process label
            if os.path.exists(label_path):
                with open(label_path, 'r') as f:
                    label = f.readline().strip().split()
                    if not label:  # Empty file or only whitespace
                        heatmap = np.zeros((h, w))
                    elif len(label) >= 3:  # Valid YOLO format
                        try:
                            x_center = float(label[1]) * w  # Denormalize to target width
                            y_center = float(label[2]) * h  # Denormalize to target height
                            heatmap = generate_heatmap(x_center, y_center, h, w)
                        except (ValueError, IndexError) as e:
                            print(f"Error parsing label file {label_path}: {label}, Error: {e}")
                            heatmap = np.zeros((h, w))
                    else:
                        heatmap = np.zeros((h, w))
            else:
                heatmap = np.zeros((h, w))
            heatmaps.append(torch.tensor(heatmap, dtype=torch.float32))

        images = torch.cat(images, dim=0)  # (9, H, W), where H, W are from target_size
        heatmaps = torch.stack(heatmaps, dim=0)  # (3, H, W)
        return images, heatmaps