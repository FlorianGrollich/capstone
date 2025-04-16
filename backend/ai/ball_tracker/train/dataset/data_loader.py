import os
import cv2
import numpy as np
import albumentations as A
from pathlib import Path
from torch.utils.data import DataLoader, random_split
from tqdm import tqdm

from capstone.backend.ai.ball_tracker.train.dataset.track_net_dataset import TrackNetDataset
from capstone.backend.ai.utils.download_dataset import get_dataset
from capstone.backend.app.core.config import settings


def parse_yolo_labels(label_path):
    bboxes = []
    try:
        with open(label_path, 'r') as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) >= 5:
                    class_id, x_center, y_center, width, height = map(float, parts[:5])
                    bboxes.append([x_center, y_center, width, height, class_id])
    except Exception as e:
        print(f"Error parsing label file {label_path}: {e}")
    return bboxes


def write_yolo_labels(label_path, bboxes):
    with open(label_path, 'w') as f:
        for bbox in bboxes:
            x_center, y_center, width, height, class_id = bbox
            f.write(f"{int(class_id)} {x_center} {y_center} {width} {height}\n")


def get_transform():
    return A.ReplayCompose([
        A.HorizontalFlip(p=0.5),
        A.RandomBrightnessContrast(brightness_limit=0.2, contrast_limit=0.2, p=0.5),
        A.Rotate(limit=30, p=0.5),
        A.Affine(translate_percent=0.05, scale=(0.9, 1.1), rotate=0, p=0.5),
        A.RandomResizedCrop(size=(720, 1280), scale=(0.8, 1.0), p=0.3),
    ], bbox_params=A.BboxParams(format='yolo', min_visibility=0.0))


def augment_single_sample(sample_dir, output_dir, aug_idx, transform):
    frames = []
    bboxes_list = []

    for i in range(3):
        img_path = os.path.join(sample_dir, f'image-{i}', 'image.jpg')
        label_path = os.path.join(sample_dir, f'image-{i}', 'label.txt')

        if not os.path.exists(img_path):
            return False

        img = cv2.imread(img_path)
        if img is None:
            return False
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        bboxes = parse_yolo_labels(label_path) if os.path.exists(label_path) else []

        frames.append(img)
        bboxes_list.append(bboxes)

    try:

        augmented = transform(image=frames[0], bboxes=bboxes_list[0])
        replay = augmented['replay']
        aug_frames = [augmented['image']]
        aug_bboxes = [augmented['bboxes']]

        for i in range(1, 3):
            augmented = A.ReplayCompose.replay(replay, image=frames[i], bboxes=bboxes_list[i])
            aug_frames.append(augmented['image'])
            aug_bboxes.append(augmented['bboxes'])

        output_sample_dir = os.path.join(output_dir, f"{os.path.basename(sample_dir)}_aug{aug_idx}")
        os.makedirs(output_sample_dir, exist_ok=True)

        for i in range(3):
            frame_dir = os.path.join(output_sample_dir, f'image-{i}')
            os.makedirs(frame_dir, exist_ok=True)

            aug_img = cv2.cvtColor(aug_frames[i], cv2.COLOR_RGB2BGR)
            cv2.imwrite(os.path.join(frame_dir, 'image.jpg'), aug_img)

            if aug_bboxes[i]:
                write_yolo_labels(os.path.join(frame_dir, 'label.txt'), aug_bboxes[i])

        return True
    except Exception as e:
        print(f"Error augmenting sample {sample_dir}: {e}")
        return False


def preprocess_dataset(dataset_dir, num_augmentations=4, logger=None):
    dataset_path = Path(dataset_dir)
    transform = get_transform()

    if logger:
        logger.info(f"Applying data augmentation: {num_augmentations} variations per sample")

    # Get all sample directories first
    sample_dirs = [d for d in dataset_path.glob('frame*') if d.is_dir() and '_aug' not in d.name]
    total_samples = len(sample_dirs)

    if total_samples == 0:
        if logger:
            logger.warning(f"No frame directories found in {dataset_dir} for augmentation")
        return

    successful_augs = 0
    total_attempts = 0

    # Create progress bar for the augmentation process
    for sample_dir in tqdm(sample_dirs, desc="Augmenting dataset", unit="sample"):
        for aug_idx in range(num_augmentations):
            total_attempts += 1
            if augment_single_sample(sample_dir, dataset_path, aug_idx, transform):
                successful_augs += 1

    if logger:
        logger.info(f"Dataset augmentation completed: {successful_augs}/{total_attempts} successful")
        logger.info(f"Original samples: {total_samples}, Total samples after augmentation: {total_samples * (num_augmentations + 1)}")


def prepare_dataset(dataset_dir, batch_size, test_batch_size, target_size, logger):
    dataset_url = f'https://upcdn.io/{settings.bytescale_account_id}/raw/ball_dataset.zip'

    # Create base directory
    os.makedirs(dataset_dir, exist_ok=True)

    # Check if directory is empty or needs download
    if not any(path.startswith('frame') for path in os.listdir(dataset_dir)):
        logger.info(f"No frame directories found in '{dataset_dir}'. Downloading...")
        try:
            get_dataset(file_url=dataset_url, extract_to=dataset_dir)

            # Fix double-nested structure after extraction
            nested_dataset_dir = os.path.join(dataset_dir, 'dataset')
            if os.path.exists(nested_dataset_dir) and os.path.isdir(nested_dataset_dir):
                logger.info(f"Moving frame folders from '{nested_dataset_dir}' to '{dataset_dir}'")
                frame_dirs = [d for d in os.listdir(nested_dataset_dir) if d.startswith('frame')]

                for frame_dir in frame_dirs:
                    src_path = os.path.join(nested_dataset_dir, frame_dir)
                    dst_path = os.path.join(dataset_dir, frame_dir)
                    # Move the directory up one level
                    os.rename(src_path, dst_path)

                logger.info(f"Moved {len(frame_dirs)} frame directories one level up")
        except Exception as e:
            logger.error(f"Downloading or restructuring dataset failed: {e}")
            raise
    else:
        logger.info(f"Frame directories already exist in '{dataset_dir}'")

    # Apply data augmentation
    logger.info("Starting data augmentation...")
    preprocess_dataset(dataset_dir, num_augmentations=4, logger=logger)
    logger.info("Data augmentation completed.")

    # Create dataset
    dataset = TrackNetDataset(root_dir=dataset_dir, target_size=target_size)

    # Check if dataset is empty
    if len(dataset) == 0:
        logger.error(f"Dataset is empty! Please check contents of '{dataset_dir}'")
        files = os.listdir(dataset_dir)
        logger.error(f"Files in dataset directory: {files}")
        raise ValueError("Dataset contains 0 samples. Cannot create data loaders.")

    logger.info(f"Dataset contains {len(dataset)} valid samples")
    return create_data_loaders(dataset, batch_size, test_batch_size, logger)


def create_data_loaders(dataset, batch_size, test_batch_size, logger):
    dataset_size = len(dataset)
    train_size = int(0.9 * dataset_size)
    test_size = dataset_size - train_size

    train_dataset, test_dataset = random_split(dataset, [train_size, test_size])
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=test_batch_size, shuffle=False)

    logger.info(f"Dataset loaded: {dataset_size} samples ({train_size} train, {test_size} test)")
    return train_loader, test_loader
