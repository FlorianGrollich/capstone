import torch
import torch.nn as nn

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