from ultralytics import YOLO


MODEL_VARIANT = 'yolo12m.pt'

DATA_YAML_PATH = "dataset/data/data.yaml"


NUM_EPOCHS = 1000
IMAGE_SIZE = 640
BATCH_SIZE = 4


model = YOLO(MODEL_VARIANT)

# --- Start Training ---
print("Starting training...")
results = model.train(
    data=DATA_YAML_PATH,
    epochs=NUM_EPOCHS,
    imgsz=IMAGE_SIZE,
    batch=BATCH_SIZE,
    patience=10,
)

print("Training finished.")
print(f"Results saved to: {results.save_dir}")