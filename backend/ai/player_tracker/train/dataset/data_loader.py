import os
import logging

from capstone.backend.ai.utils.download_dataset import get_dataset


def setup_logging():
    """Set up logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    return logging.getLogger('PlayerDetector')

def prepare_player_dataset(dataset_dir='./data'):
    """Download and prepare the player detection dataset."""
    logger = setup_logging()

    # Create base directory
    os.makedirs(dataset_dir, exist_ok=True)

    dataset_url = 'https://upcdn.io/W23MT6f/raw/hockey-player.zip'

    # Check if directory already has data
    if os.path.exists(os.path.join(dataset_dir, 'train')) or \
       os.path.exists(os.path.join(dataset_dir, 'valid')):
        logger.info(f"Dataset already exists in '{dataset_dir}'")
    else:
        logger.info(f"Downloading player dataset to '{dataset_dir}'")
        try:
            # Download and extract the dataset using get_dataset
            get_dataset(file_url=dataset_url, extract_to=dataset_dir)
            logger.info("Dataset download and extraction complete")
        except Exception as e:
            logger.error(f"Dataset preparation failed: {e}")
            raise

    return dataset_dir

if __name__ == "__main__":
    dataset_path = prepare_player_dataset()
    print(f"Dataset prepared at: {dataset_path}")