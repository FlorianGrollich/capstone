import torch
import torch.nn as nn

from model.decoder import TrackNetV2Decoder
from model.encoder import TrackNetV2Encoder


class TrackNetV4(nn.Module):
    def __init__(self, theta_init=0.5):
        super(TrackNetV4, self).__init__()
        self.encoder = TrackNetV2Encoder()
        self.decoder = TrackNetV2Decoder()
        # Learnable parameter for power normalization
        self.theta = nn.Parameter(torch.tensor(theta_init, dtype=torch.float32))

    def generate_motion_attention_maps(self, frames):
        # frames: (batch, 9, H, W) -> split into 3 frames: (batch, 3, H, W) each
        batch_size, _, h, w = frames.shape
        frame1 = frames[:, 0:3, :, :]
        frame2 = frames[:, 3:6, :, :]
        frame3 = frames[:, 6:9, :, :]

        # Convert to grayscale (mean across channels)
        gray1 = frame1.mean(dim=1, keepdim=True)  # (batch, 1, H, W)
        gray2 = frame2.mean(dim=1, keepdim=True)
        gray3 = frame3.mean(dim=1, keepdim=True)

        # Compute absolute frame differences
        diff1 = torch.abs(gray2 - gray1)  # (batch, 1, H, W)
        diff2 = torch.abs(gray3 - gray2)

        # Power normalization with learnable theta
        motion_maps = torch.cat([diff1, diff2], dim=1)  # (batch, 2, H, W)
        motion_maps = torch.pow(motion_maps, self.theta)
        motion_maps = (motion_maps - motion_maps.min()) / (motion_maps.max() - motion_maps.min() + 1e-6)

        return motion_maps  # (batch, 2, H, W) - 2 motion maps

    def forward(self, x):
        # x: (batch, 9, H, W) - 3 frames stacked
        # Step 1: Generate motion attention maps
        motion_maps = self.generate_motion_attention_maps(x)  # (batch, 2, H, W)

        # Step 2: Encoder-Decoder to get visual features
        bottleneck, skip_connections = self.encoder(x)
        visual_features = self.decoder(bottleneck, skip_connections)  # (batch, 3, H, W)

        # Step 3: Motion-aware fusion
        fused_features = torch.zeros_like(visual_features)
        fused_features[:, 0, :, :] = visual_features[:, 0, :, :]  # First frame unchanged
        fused_features[:, 1, :, :] = visual_features[:, 1, :, :] * motion_maps[:, 0, :, :]  # Second frame
        fused_features[:, 2, :, :] = visual_features[:, 2, :, :] * motion_maps[:, 1, :, :]  # Third frame

        # Step 4: Apply Sigmoid to get heatmaps
        heatmaps = torch.sigmoid(fused_features)  # (batch, 3, H, W)
        return heatmaps