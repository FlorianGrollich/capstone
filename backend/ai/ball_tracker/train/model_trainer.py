import os
import torch
import torch.nn as nn
import torch.optim as optim

from capstone.backend.ai.ball_tracker.track_net import TrackNetV4


class ModelTrainer:
    def __init__(self, learning_rate, epochs, patience, weights_dir, pos_weight, logger):
        self.learning_rate = learning_rate
        self.epochs = epochs
        self.patience = patience
        self.weights_dir = weights_dir
        self.logger = logger

        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = TrackNetV4().to(self.device)
        self.pos_weight = torch.tensor([pos_weight]).to(self.device)
        self.criterion = nn.BCEWithLogitsLoss(pos_weight=self.pos_weight)
        self.optimizer = optim.Adam(self.model.parameters(), lr=learning_rate)

        self.logger.info(f"Using device: {self.device}")

    def train_epoch(self, train_loader, epoch):
        """Train for a single epoch."""
        self.model.train()
        total_train_loss = 0

        for batch_idx, (images, heatmaps) in enumerate(train_loader):
            images, heatmaps = images.to(self.device), heatmaps.to(self.device)

            pred_heatmaps = self.model(images)
            loss = self.criterion(pred_heatmaps, heatmaps)
            total_train_loss += loss.item()

            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()

            if batch_idx % 10 == 0:
                self.logger.info(
                    f'Epoch [{epoch + 1}/{self.epochs}], Batch [{batch_idx}/{len(train_loader)}], Loss: {loss.item():.4f}')

        avg_loss = total_train_loss / len(train_loader)
        self.logger.info(f'Epoch [{epoch + 1}/{self.epochs}] Average Training Loss: {avg_loss:.4f}')
        return avg_loss

    def evaluate(self, test_loader, epoch):
        """Evaluate the model on test data."""
        self.model.eval()
        total_test_loss = 0

        with torch.no_grad():
            for images, heatmaps in test_loader:
                images, heatmaps = images.to(self.device), heatmaps.to(self.device)
                pred_heatmaps = self.model(images)
                loss = self.criterion(pred_heatmaps, heatmaps)
                total_test_loss += loss.item()

        avg_loss = total_test_loss / len(test_loader)
        self.logger.info(f'Epoch [{epoch + 1}/{self.epochs}] Average Testing Loss: {avg_loss:.4f}')
        return avg_loss

    def save_model(self, path):
        """Save model to the specified path."""
        torch.save(self.model.state_dict(), path)

    def train_model(self, train_loader, test_loader):
        """Train the model with early stopping."""
        best_loss = float('inf')
        trigger_times = 0

        for epoch in range(self.epochs):
            # Training phase
            self.train_epoch(train_loader, epoch)

            # Evaluation phase
            avg_test_loss = self.evaluate(test_loader, epoch)

            # Model saving and early stopping
            if avg_test_loss < best_loss:
                best_loss = avg_test_loss
                trigger_times = 0
                self.save_model(os.path.join(self.weights_dir, 'best.pth'))
                self.logger.info(f"Best model saved at epoch {epoch + 1}")
            else:
                trigger_times += 1
                self.logger.info(f'No improvement in epoch {epoch + 1} ({trigger_times}/{self.patience})')

            if trigger_times >= self.patience:
                self.logger.info("Early stopping triggered.")
                break

        # Save final model
        self.save_model(os.path.join(self.weights_dir, 'last.pth'))
        self.logger.info("Last model saved.")
        return self.model