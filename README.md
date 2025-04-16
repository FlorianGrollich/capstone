# Field Hockey Video Analysis

## Overview

This is a Capstone project that analyzes field hockey videos to provide statistical insights. The application takes a video of a field hockey scene as input and outputs various statistics about the game.

## Features

### Ball Possession Tracking

- A player is considered in possession of the ball when their bounding box center is closest to the ball and the ball is within their bounding box or a small threshold
- Calculates possession percentage for each team
- Periods when no player possesses the ball are tracked separately

### Pass Analysis

- Passes are counted when ball possession changes between players of the same team


## Project Structure

### Frontend

- Typescript
- React
- Redux
- TailwindCSS


### Backend

- Python
- FastAPI
- ByteScale as thirdparty service to store video

### AI

- Python
- Pytorch
- YOLO
- ultralytics
- TrackNetV4

## Backend Setup

### Prerequisites

- Python 3.8+
- pip (Python package manager)
- Virtual environment tool
- conda (optional but recommended )

### Installation

1. Clone the repository
   ```bash
   git clone https://github.com/FlorianGrollich/capstone
   cd capstone
   ```

2. Set up a virtual environment
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

### Running the Backend

1.1 Start the FastAPI server in dev
   ```bash
   fastapi dev
   ```
1.2 Start the FastAPI server
   ```bash
   fastapi run
   ```
2. Access the API documentation
    - Swagger UI: http://localhost:8000/docs

## Frontend Setup

### Prerequisites

- Node.js and npm

### Installation

1. Navigate to the frontend directory
   ```bash
   cd frontend
   ```

2. Install dependencies
   ```bash
   npm install
   ```

### Running the Frontend in dev

```bash
npm run dev
```



## Train TrackNetV4 Model for ball

### Prerequisites
- if you have own dataset it is to be expected that labeling is YOLO format and datset folder contains two folders images and labels the image has to have same name as corresponding label.txt
- current implementation fetches dataset from bytescale
- setup enviroment with pytorch installed

1. navigate to ai/ball_tracker
2. run train script (it should automatically check for data and fetch it if its missing)
```bash
python train.py
```


## Train YOLO model for Player
### Prerequisites

- if you have own dataset it is to be expected 

