import torch.nn.functional as F

def weighted_bce_loss(pred, target, pos_weight=100):
    bce = F.binary_cross_entropy(pred, target, reduction='none')
    weights = target * pos_weight + (1 - target)
    return (bce * weights).mean()