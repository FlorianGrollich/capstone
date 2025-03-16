import numpy as np

def generate_heatmap(center_x, center_y, h, w, sigma=5):
    x, y = np.meshgrid(np.arange(w), np.arange(h))
    heatmap = np.exp(-((x - center_x) ** 2 + (y - center_y) ** 2) / (2 * sigma ** 2))
    return heatmap / heatmap.max()