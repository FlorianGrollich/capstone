import os

from capstone.backend.ai.ball_tracker.train.model_trainer import ModelTrainer
from capstone.backend.ai.ball_tracker.train.utils.logger import setup_logging
from capstone.backend.ai.ball_tracker.train.dataset.data_loader import prepare_dataset


def main():

    dataset_dir = '../train/dataset/data'
    weights_dir = 'weights'
    batch_size = 8
    test_batch_size = 8
    learning_rate = 1e-4
    epochs = 1000
    patience = 5
    image_size = (720, 128)
    pos_weight = 100


    logger = setup_logging()


    os.makedirs(weights_dir, exist_ok=True)

    try:

        height, width = image_size


        train_loader, test_loader = prepare_dataset(
            dataset_dir=dataset_dir,
            batch_size=batch_size,
            test_batch_size=test_batch_size,
            target_size=(height, width),
            logger=logger
        )


        trainer = ModelTrainer(
            learning_rate=learning_rate,
            epochs=epochs,
            patience=patience,
            weights_dir=weights_dir,
            pos_weight=pos_weight,
            logger=logger
        )

        trainer.train_model(train_loader, test_loader)

    except Exception as e:
        logger.error(f"Training failed: {e}", exc_info=True)
        return 1

    return 0

if __name__ == "__main__":
    main()