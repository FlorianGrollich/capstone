import torch
import torch.nn as nn
import torch.nn.functional as F


class TrackNetV2Encoder(nn.Module):
    def __init__(self):
        super(TrackNetV2Encoder, self).__init__()
        # Encoder layers (VGG-16 inspired)
        self.conv1 = nn.Sequential(
            nn.Conv2d(9, 64, 3, padding=1),  # 3 frames * 3 channels = 9 input channels
            nn.ReLU(),
            nn.Conv2d(64, 64, 3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2, 2)  # Downsample to H/2, W/2
        )
        self.conv2 = nn.Sequential(
            nn.Conv2d(64, 128, 3, padding=1),
            nn.ReLU(),
            nn.Conv2d(128, 128, 3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2, 2)  # Downsample to H/4, W/4
        )
        self.conv3 = nn.Sequential(
            nn.Conv2d(128, 256, 3, padding=1),
            nn.ReLU(),
            nn.Conv2d(256, 256, 3, padding=1),
            nn.ReLU(),
            nn.Conv2d(256, 256, 3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2, 2)  # Downsample to H/8, W/8
        )
        self.conv4 = nn.Sequential(
            nn.Conv2d(256, 512, 3, padding=1),
            nn.ReLU(),
            nn.Conv2d(512, 512, 3, padding=1),
            nn.ReLU(),
            nn.Conv2d(512, 512, 3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2, 2)  # Downsample to H/16, W/16
        )

    def forward(self, x):
        # x: (batch, 9, H, W) - 3 frames stacked
        conv1_out = self.conv1(x)
        conv2_out = self.conv2(conv1_out)
        conv3_out = self.conv3(conv2_out)
        conv4_out = self.conv4(conv3_out)
        return conv4_out, [conv1_out, conv2_out, conv3_out]  # Return bottleneck and skip connections


class TrackNetV2Decoder(nn.Module):
    def __init__(self):
        super(TrackNetV2Decoder, self).__init__()
        # Decoder layers with upsampling and skip connections
        self.up4 = nn.Sequential(
            nn.ConvTranspose2d(512, 256, 4, stride=2, padding=1),
            nn.ReLU()
        )
        self.conv_up4 = nn.Sequential(
            nn.Conv2d(512, 256, 3, padding=1),  # 256 from up4 + 256 from conv3
            nn.ReLU()
        )
        self.up3 = nn.Sequential(
            nn.ConvTranspose2d(256, 128, 4, stride=2, padding=1),
            nn.ReLU()
        )
        self.conv_up3 = nn.Sequential(
            nn.Conv2d(256, 128, 3, padding=1),  # 128 from up3 + 128 from conv2
            nn.ReLU()
        )
        self.up2 = nn.Sequential(
            nn.ConvTranspose2d(128, 64, 4, stride=2, padding=1),
            nn.ReLU()
        )
        self.conv_up2 = nn.Sequential(
            nn.Conv2d(128, 64, 3, padding=1),  # 64 from up2 + 64 from conv1
            nn.ReLU()
        )
        self.final = nn.Sequential(
            nn.ConvTranspose2d(64, 32, 4, stride=2, padding=1),
            nn.ReLU(),
            nn.Conv2d(32, 3, 1)  # Output 3 heatmaps (one per frame)
        )

    def forward(self, x, skip_connections):
        # x: (batch, 512, H/16, W/16), skip_connections: [conv1, conv2, conv3]
        x = self.up4(x)
        x = torch.cat([x, skip_connections[2]], dim=1)  # Concat with conv3
        x = self.conv_up4(x)

        x = self.up3(x)
        x = torch.cat([x, skip_connections[1]], dim=1)  # Concat with conv2
        x = self.conv_up3(x)

        x = self.up2(x)
        x = torch.cat([x, skip_connections[0]], dim=1)  # Concat with conv1
        x = self.conv_up2(x)

        x = self.final(x)  # (batch, 3, H, W) - 3 heatmaps
        return x


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

        return fused_features