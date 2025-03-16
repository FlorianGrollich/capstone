import torch.nn as nn

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
        return conv4_out, [conv1_out, conv2_out, conv3_out]