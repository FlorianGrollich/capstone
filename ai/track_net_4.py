import torch
import torch.nn as nn
import torch.nn.functional as F


class TrackNetV4(nn.Module):
    def __init__(self, in_channels=3, num_classes=1):
        super(TrackNetV4, self).__init__()
        # Encoder
        self.enc1 = nn.Sequential(
            nn.Conv2d(in_channels, 64, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.BatchNorm2d(64),
            nn.Conv2d(64, 64, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.BatchNorm2d(64),
        )

        self.enc2 = nn.Sequential(
            nn.MaxPool2d(2, 2),
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.BatchNorm2d(128),
        )

        self.enc3 = nn.Sequential(
            nn.MaxPool2d(2, 2),
            nn.Conv2d(128, 256, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.BatchNorm2d(256),
        )

        self.enc5 = nn.Sequential(
            nn.MaxPool2d(2, 2),
            nn.Upsample(scale_factor=2, mode="bilinear")
        )

        self.enc6 = nn.Sequential(
            nn.Conv2d(512, 256, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.BatchNorm2d(256),
            nn.Upsample(scale_factor=2, mode="billinear"),

        )
        self.enc7 = nn.Sequential(
            nn.Conv2d(192, 64, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.BatchNorm2d(64),
            nn.Conv2d(64, 3, kernel_size=1)
        )

    def forward(self, x):
        e1 = self.enc1(x)
        e2 = self.enc2(e1)
        e3 = self.enc3(e2)
        e4 = self.enc4(e3)

        # Decoder path with skip connections
        u4 = self.up4(b)
        d4 = self.dec4(torch.cat([u4, e4], dim=1))

        u3 = self.up3(d4)
        d3 = self.dec3(torch.cat([u3, e3], dim=1))

        u2 = self.up2(d3)
        d2 = self.dec2(torch.cat([u2, e2], dim=1))

        u1 = self.up1(d2)
        d1 = self.dec1(torch.cat([u1, e1], dim=1))

        out = self.out_conv(d1)
        # Depending on the task, you might apply an activation (sigmoid/softmax) to the output
        return out


# For testing the network
if __name__ == '__main__':
    model = TrackNetV4(in_channels=3, num_classes=1)
    x = torch.randn(1, 3, 256, 256)  # Example input (batch size, channels, height, width)
    output = model(x)
    print("Output shape:", output.shape)

