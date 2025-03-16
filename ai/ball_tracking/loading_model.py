from model.track_net_v4 import TrackNetV4
import torch

def load_model():
    model = TrackNetV4()
    state_dict  = torch.load("tracknetv4.pth", weights_only=True)
    model.load_state_dict(state_dict)

    return model