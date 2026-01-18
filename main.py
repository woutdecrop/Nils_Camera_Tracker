import cv2
import mediapipe as mp
import numpy as np
import os
import math
# Initialize MediaPipe
mp_face_mesh = mp.solutions.face_mesh
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

def load_overlay_images():
    """Load all overlay images"""
    images = {}
    image_files = {
        'hand_behind_head_right': './images/hand_behind_head_on_right.jpg',
        'hand_under_chin': './images/hand_under_chin.jpg',
        'normal': './images/niels_normal.jpg',
        'perfect_sign': './images/perfect_sign.jpg',
        'mouth_open': './images/mouth_open.jpg',
        'hand_next_to_face_right': './images/hand_next_to_face_right.jpg',
        'hand_next_to_face_left': './images/hand_next_to_face_left.jpg'
    }
    
    for key, filename in image_files.items():
        if os.path.exists(filename):
            img = cv2.imread(filename)
            if img is not None:
                images[key] = img
                print(f"✓ Loaded: {filename}")
            else:
                print(f"✗ Failed to load: {filename}")
        else:
            print(f"✗ File not found: {filename}")
    
    return images

def finger_up(tip, pip):
    return tip.y < pip.y

def finger_down(tip, pip):
    return tip.y > pip.y

def distance(p1, p2):
    return math.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2)


def detect_gesture(hand_landmarks, face_landmarks, face_center_x, frame_width):
    """Detect specific hand and face gestures"""
    
    # --- 1. FACE MEASUREMENTS ---
    chin = face_landmarks.landmark[152]
    forehead = face_landmarks.landmark[10]
    u_lip = face_landmarks.landmark[13]
    l_lip = face_landmarks.landmark[14]
    
    # Ear landmarks for side-of-face gestures
    left_ear = face_landmarks.landmark[234]
    right_ear = face_landmarks.landmark[454]
    
    face_height = distance(forehead, chin)
    
    # Mouth detection
    mouth_opening = abs(u_lip.y - l_lip.y)
    if mouth_opening > (face_height * 0.12): 
        return 'mouth_open'

    if not hand_landmarks:
        return None

    # --- 2. HAND MEASUREMENTS ---
    wrist = hand_landmarks.landmark[0]
    thumb_tip = hand_landmarks.landmark[4]
    index_tip = hand_landmarks.landmark[8]
    index_mcp = hand_landmarks.landmark[5]
    
    wrist_px_x = wrist.x * frame_width
    
    # Gesture: Hand Behind Head (Right Side)
    # Triggered when wrist is above ear level and on the right side of the screen
    palm_size = distance(index_mcp, wrist)
    offset = 0.3 * palm_size
    if wrist.y + offset < right_ear.y and wrist_px_x > face_center_x:
        return 'hand_behind_head_right'

    # NEW Gesture: Hand Next to Face 
    # ---------------- Distance index → ear ----------------
    dist_right = distance(index_tip, right_ear)
    dist_left  = distance(index_tip, left_ear)
    # Use palm size to normalize

    touching_right = dist_right < 0.45 * palm_size
    touching_left  = dist_left < 0.45 * palm_size
    
    is_horizontal = abs(index_tip.y - index_mcp.y) < (0.5 * palm_size)
    
    # Check Right Side (Both proximity AND horizontal orientation)
    if touching_right and is_horizontal:
        return 'hand_next_to_face_right'
    
    # Check Left Side (Both proximity AND horizontal orientation)
    if touching_left and is_horizontal:
        return 'hand_next_to_face_left'
    # Gesture: Hand Under Chin
    dist_to_chin = distance(index_mcp, chin)


    if index_mcp.y > chin.y and dist_to_chin < (face_height * 0.35):
        return 'hand_under_chin'

    # Gesture: Perfect Sign 👌
    thumb_index_dist = distance(thumb_tip, index_tip)
    index_length = distance(index_tip, index_mcp)
    
    is_circle = thumb_index_dist < (0.45 * index_length)
    mid_up = finger_up(hand_landmarks.landmark[12], hand_landmarks.landmark[10])
    ring_up = finger_up(hand_landmarks.landmark[16], hand_landmarks.landmark[14])
    
    if is_circle and mid_up and ring_up:
        return 'perfect_sign'

    return None
def resize_image_to_fit(image, max_width=800, max_height=600):
    """Resize image to fit within max dimensions while maintaining aspect ratio"""
    height, width = image.shape[:2]
    
    # Calculate scaling factor
    scale_w = max_width / width
    scale_h = max_height / height
    scale = min(scale_w, scale_h)
    
    # Only resize if image is larger than max dimensions
    if scale < 1.0:
        new_width = int(width * scale)
        new_height = int(height * scale)
        return cv2.resize(image, (new_width, new_height))
    
    return image

def main():
    # Load overlay images
    overlay_images = load_overlay_images()
    
    if not overlay_images:
        print("\n🎥 Camera successfully started!")
        print("\n🖐️  Try these gestures:")

        print("  ✨ Normal Niels → No gesture detected (default state)")
        print("  🤚 Hand under chin → Rest your hand under your chin")
        print("  ✋ Hand behind head (right side) → Right hand behind head, elbow up")
        print("  👋 Hand next to face (right or left) → Hand gently next to your face")
        print("  👌 Perfect Sign → Thumb and index form a circle, other fingers up")
        print("  😮 Mouth open → Open your mouth noticeably")

        print("\nℹ️  Press 'q' at any time to quit the program\n")

        return
    
    if 'normal' not in overlay_images:
        print("\n⚠️  niels_normal.jpg not found! This is required for default display.")
        return
    
    # Initialize webcam
    cap = cv2.VideoCapture(0)
    
    # Track current gesture
    current_gesture = 'normal'
    
    # Window names
    webcam_window = 'Your Face'
    niels_window = 'Niels De Stadsbader'
    
    # Initialize MediaPipe models
    with mp_face_mesh.FaceMesh(
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    ) as face_mesh, mp_hands.Hands(
        max_num_hands=2,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    ) as hands:
        
        print("\n🎥 Camera successfully started!")
        print("\n🖐️  Try these gestures:")

        print("  ✨ Normal Niels → No gesture detected (default state)")
        print("  🤚 Hand under chin → Rest your hand under your chin")
        print("  ✋ Hand behind head (right side) → Right hand behind head, elbow up")
        print("  👋 Hand next to face (right or left) → Hand gently next to your face")
        print("  👌 Perfect Sign → Thumb and index form a circle, other fingers up")
        print("  😮 Mouth open → Open your mouth noticeably")

        print("\nℹ️  Press 'q' at any time to quit the program\n")

        
        # Display initial normal image
        niels_display = resize_image_to_fit(overlay_images['normal'])
        cv2.imshow(niels_window, niels_display)
        
        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                print("Failed to grab frame")
                break
            
            # Flip frame horizontally for selfie view
            frame = cv2.flip(frame, 1)
            h, w, _ = frame.shape
            
            # Convert to RGB for MediaPipe
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Process face and hands
            face_res = face_mesh.process(rgb_frame)
            hand_res = hands.process(rgb_frame)
            
            # Variables for face position
            face_center_x = w // 2
            face_x, face_y, face_w, face_h = 0, 0, 0, 0
            if face_res.multi_face_landmarks:
                face_lms = face_res.multi_face_landmarks[0]
                
                # Calculate face center for side detection
                face_x_coords = [lm.x * w for lm in face_lms.landmark]
                face_center_x = sum(face_x_coords) / len(face_x_coords)
                
                # Check for hand-based gestures
                if hand_res.multi_hand_landmarks:
                    hand_lms = hand_res.multi_hand_landmarks[0]
                    detected_gesture = detect_gesture(hand_lms, face_lms, face_center_x, w)
                    mp_drawing.draw_landmarks(frame, hand_lms, mp_hands.HAND_CONNECTIONS)
                else:
                    # Check for face-only gestures (like mouth open)
                    detected_gesture = detect_gesture(None, face_lms, face_center_x, w)

            # Detect face
            if face_res.multi_face_landmarks:
                face_landmarks = face_res.multi_face_landmarks[0]
                
                # Get face bounding box
                x_coords = [lm.x * w for lm in face_landmarks.landmark]
                y_coords = [lm.y * h for lm in face_landmarks.landmark]
                
                face_x = int(min(x_coords))
                face_y = int(min(y_coords))
                face_w = int(max(x_coords) - face_x)
                face_h = int(max(y_coords) - face_y)
                face_center_x = face_x + face_w // 2
                
                # Draw face rectangle
                cv2.rectangle(frame, (face_x, face_y), 
                            (face_x + face_w, face_y + face_h), 
                            (0, 255, 0), 2)
            
            
            # Determine which image to show
            if detected_gesture and detected_gesture in overlay_images:
                gesture_to_show = detected_gesture
            else:
                gesture_to_show = 'normal'
            
            # Update Niels window if gesture changed
            if gesture_to_show != current_gesture:
                current_gesture = gesture_to_show
                niels_display = resize_image_to_fit(overlay_images[gesture_to_show])
                cv2.imshow(niels_window, niels_display)
                
                # Display gesture name
                gesture_names = {
                    'perfect_sign': 'Perfect_Sign',
                    'hand_under_chin': 'Hand Under Chin',
                    'hand_behind_head_right': 'Hand Behind Head',
                    'normal': 'No Gesture - Normal',
                    'mouth_open': 'Mouth Open',
                    'hand_next_to_face_right': 'Hand Next to Face Right',
                    'hand_next_to_face_left': 'Hand Next to Face Left'
                }
                print(f"🎭 {gesture_names[gesture_to_show]}")
            
            # Display current gesture on webcam feed
            gesture_names = {
                'perfect_sign': 'Perfect_Sign',
                'hand_under_chin': 'Hand Under Chin',
                'hand_behind_head_right': 'Hand Behind Head',
                'normal': 'No Gesture - Normal',
                'mouth_open': 'Mouth Open',
                'hand_next_to_face_right': 'Hand Next to Face Right',
                'hand_next_to_face_left': 'Hand Next to Face Left'
            }
            
            gesture_text = gesture_names.get(current_gesture, 'Unknown')
            cv2.putText(frame, f'Gesture: {gesture_text}', 
                       (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            # Display instructions
            cv2.putText(frame, 'Press Q to Quit', 
                       (10, h - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            
            # Display the webcam frame
            cv2.imshow(webcam_window, frame)
            
            # Handle key presses
            key = cv2.waitKey(5) & 0xFF
            if key == ord('q'):
                break
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()