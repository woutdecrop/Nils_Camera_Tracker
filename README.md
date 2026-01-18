# Niels Gesture Detection

This project uses **MediaPipe** and **OpenCV** to detect specific hand and face gestures in real-time via webcam and display corresponding overlay images of Niels De Stadsbader.

---

## Features

- Detects the following gestures:
  - ✨ **Normal Niels** → No gesture detected (default state)
  - 🤚 **Hand under chin** → Rest your hand under your chin
  - ✋ **Hand behind head (right side)** → Right hand behind head, elbow up
  - 👋 **Hand next to face (right or left)** → Hand gently next to your face
  - 👌 **Perfect Sign** → Thumb and index form a circle, other fingers up
  - 😮 **Mouth open** → Open your mouth noticeably

- Real-time webcam feed with gesture overlay
- Highlights detected face with a green rectangle
- Displays the detected gesture name on the webcam feed
- Shows corresponding overlay image for Niels De Stadsbader in a separate window

---

## Requirements

- Python 3.8+
- OpenCV
- MediaPipe
- NumPy

Install dependencies using pip:

```bash
pip install opencv-python mediapipe numpy
```

---

## Installation

### 1. Clone the repository
```bash
git clone https://github.com/reinesana/MeowCV.git
```

### 2. Install dependencies
Python **3.9 – 3.12** required (tested on Python 3.11.7). Python **3.13+** is not supported for `mediapipe==0.10.14`.
```bash
pip install -r requirements.txt
```

### 3. Run the program
```bash
python main.py
```

---

## Folder Structure

```
project/
│
├── images/
│   ├── niels_normal.jpg
│   ├── hand_behind_head_on_right.jpg
│   ├── hand_under_chin.jpg
│   ├── hand_next_to_face_right.jpg
│   ├── hand_next_to_face_left.jpg
│   ├── perfect_sign.jpg
│   └── mouth_open.jpg
│
├── gesture_detection.py  # Main script
└── README.md             # This file
```

> ⚠️ Make sure all overlay images exist in the `images/` folder.

---

## Usage

1. Connect a webcam.
2. Run the main script:

```bash
python gesture_detection.py
```

3. Follow the instructions printed in the terminal:
   - Place your hand under your chin
   - Put your right hand behind your head
   - Move your hand gently next to your face (left or right)
   - Make the “👌 Perfect Sign”
   - Open your mouth noticeably
4. Press `q` at any time to quit the program.

---

## How It Works

- **Face Detection:** Uses MediaPipe Face Mesh to detect facial landmarks.
- **Hand Detection:** Uses MediaPipe Hands to detect hand landmarks.
- **Gesture Logic:** 
  - `hand_under_chin` → Hand under chin, distance from index MCP to chin < 35% of face height
  - `hand_behind_head_right` → Wrist above right ear and on right side of face
  - `hand_next_to_face_right/left` → Index fingertip near corresponding ear and hand mostly horizontal
  - `perfect_sign` → Thumb and index tips close, middle and ring fingers up
  - `mouth_open` → Distance between upper and lower lip > 12% of face height
  - `normal` → No gesture detected
- **Overlay Images:** Shows the corresponding image of Niels De Stadsbader for each gesture.

---

## Notes

- Designed for a **single face** in the webcam frame.
- Works best with **well-lit environments**.
- Thresholds (like distances for gestures) are configurable in the code if needed.

---

## License

This project is free to use for educational and personal purposes.
