import numpy as np


def color_removal(i):
    b, g, r = i[..., 0], i[..., 1], i[..., 2]

    # Define masks
    mask1 = (b < g) & (r < g)  # Regions to set to black
    mask2 = (g < r) | (b > g)  # Regions to set to white

    # Initialize binary image as white (255)
    binary_image = np.full(b.shape, 255, dtype=np.uint8)

    # Apply masks
    binary_image[mask1] = 0  # Set mask1 regions to black
    binary_image[mask2] = 255  # Set mask2 regions to white (already white, but explicit)

    # Optional: Force remaining pixels (if any) to white/black
    remaining = ~(mask1 | mask2)
    binary_image[remaining] = 255  # Uncomment to set remaining pixels to white

    return binary_image
