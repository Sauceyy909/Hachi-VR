#!/usr/bin/env python3
"""
Real Working Finger Tracking for Vive Cosmos
Uses OpenCV to detect hands and fingers from camera feed
"""

import cv2
import numpy as np
import threading
import time
from pathlib import Path
import json

class FingerTracker:
    def __init__(self):
        self.enabled = False
        self.running = False
        self.thread = None
        
        # Hand detection parameters
        self.sensitivity = 0.7
        self.min_area = 5000  # Minimum hand area
        self.max_area = 100000  # Maximum hand area
        
        # Camera
        self.camera = None
        self.camera_index = 0
        
        # Hand tracking data
        self.left_hand = {
            "detected": False,
            "fingers": 0,
            "position": (0, 0),
            "confidence": 0.0
        }
        self.right_hand = {
            "detected": False,
            "fingers": 0,
            "position": (0, 0),
            "confidence": 0.0
        }
        
        # Skin color range (HSV) - calibrated for various skin tones
        self.lower_skin = np.array([0, 20, 70], dtype=np.uint8)
        self.upper_skin = np.array([20, 255, 255], dtype=np.uint8)
        
        # Config
        self.config_dir = Path.home() / ".local" / "share" / "hachi"
        self.config_file = self.config_dir / "finger_tracking.json"
        self.load_config()
        
        # Performance tracking
        self.fps = 0
        self.frame_count = 0
        self.last_fps_time = time.time()
    
    def load_config(self):
        """Load tracking configuration"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.sensitivity = config.get("sensitivity", 0.7)
                    self.camera_index = config.get("camera_index", 0)
                    
                    # Load custom skin color range if calibrated
                    if "lower_skin" in config:
                        self.lower_skin = np.array(config["lower_skin"], dtype=np.uint8)
                    if "upper_skin" in config:
                        self.upper_skin = np.array(config["upper_skin"], dtype=np.uint8)
            except Exception as e:
                print(f"Failed to load config: {e}")
    
    def save_config(self):
        """Save tracking configuration"""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        config = {
            "sensitivity": self.sensitivity,
            "camera_index": self.camera_index,
            "lower_skin": self.lower_skin.tolist(),
            "upper_skin": self.upper_skin.tolist()
        }
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Failed to save config: {e}")
    
    def start(self):
        """Start finger tracking"""
        if self.running:
            return True
        
        # Try to open camera
        self.camera = cv2.VideoCapture(self.camera_index)
        if not self.camera.isOpened():
            print(f"Failed to open camera {self.camera_index}")
            return False
        
        # Set camera properties for better performance
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.camera.set(cv2.CAP_PROP_FPS, 30)
        
        self.running = True
        self.enabled = True
        
        # Start tracking thread
        self.thread = threading.Thread(target=self._tracking_loop, daemon=True)
        self.thread.start()
        
        return True
    
    def stop(self):
        """Stop finger tracking"""
        self.running = False
        self.enabled = False
        
        if self.thread:
            self.thread.join(timeout=2.0)
        
        if self.camera:
            self.camera.release()
            self.camera = None
    
    def _tracking_loop(self):
        """Main tracking loop"""
        while self.running:
            try:
                # Read frame
                ret, frame = self.camera.read()
                if not ret:
                    time.sleep(0.1)
                    continue
                
                # Mirror the frame for more intuitive interaction
                frame = cv2.flip(frame, 1)
                
                # Detect hands
                hands = self._detect_hands(frame)
                
                # Update hand data
                if len(hands) == 0:
                    self.left_hand["detected"] = False
                    self.right_hand["detected"] = False
                elif len(hands) == 1:
                    # Single hand - determine if left or right based on position
                    hand = hands[0]
                    if hand["position"][0] < frame.shape[1] // 2:
                        self.left_hand = hand
                        self.right_hand["detected"] = False
                    else:
                        self.right_hand = hand
                        self.left_hand["detected"] = False
                else:
                    # Two hands - left is the one on the left side
                    if hands[0]["position"][0] < hands[1]["position"][0]:
                        self.left_hand = hands[0]
                        self.right_hand = hands[1]
                    else:
                        self.left_hand = hands[1]
                        self.right_hand = hands[0]
                
                # Update FPS
                self.frame_count += 1
                current_time = time.time()
                if current_time - self.last_fps_time >= 1.0:
                    self.fps = self.frame_count
                    self.frame_count = 0
                    self.last_fps_time = current_time
                
                # Small delay to prevent CPU overload
                time.sleep(0.01)
                
            except Exception as e:
                print(f"Tracking error: {e}")
                time.sleep(0.1)
    
    def _detect_hands(self, frame):
        """Detect hands and count fingers"""
        hands = []
        
        # Convert to HSV
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Create mask for skin color
        mask = cv2.inRange(hsv, self.lower_skin, self.upper_skin)
        
        # Morphological operations to remove noise
        kernel = np.ones((3, 3), np.uint8)
        mask = cv2.erode(mask, kernel, iterations=2)
        mask = cv2.dilate(mask, kernel, iterations=2)
        mask = cv2.GaussianBlur(mask, (5, 5), 100)
        
        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        # Process each contour
        for contour in contours:
            area = cv2.contourArea(contour)
            
            # Filter by area
            if area < self.min_area or area > self.max_area:
                continue
            
            # Get convex hull
            hull = cv2.convexHull(contour, returnPoints=False)
            
            # Get defects
            if len(hull) > 3 and len(contour) > 3:
                try:
                    defects = cv2.convexityDefects(contour, hull)
                    
                    if defects is None:
                        continue
                    
                    # Count fingers
                    finger_count = 0
                    
                    for i in range(defects.shape[0]):
                        s, e, f, d = defects[i, 0]
                        start = tuple(contour[s][0])
                        end = tuple(contour[e][0])
                        far = tuple(contour[f][0])
                        
                        # Calculate angle between points
                        a = np.sqrt((end[0] - start[0])**2 + (end[1] - start[1])**2)
                        b = np.sqrt((far[0] - start[0])**2 + (far[1] - start[1])**2)
                        c = np.sqrt((end[0] - far[0])**2 + (end[1] - far[1])**2)
                        
                        # Apply cosine rule
                        angle = np.arccos((b**2 + c**2 - a**2) / (2*b*c))
                        
                        # If angle is less than 90 degrees, it's a finger gap
                        if angle <= np.pi/2:
                            finger_count += 1
                    
                    # Add one for the thumb
                    finger_count += 1
                    
                    # Clamp to valid range (0-5)
                    finger_count = max(0, min(5, finger_count))
                    
                    # Get hand center
                    M = cv2.moments(contour)
                    if M["m00"] != 0:
                        cx = int(M["m10"] / M["m00"])
                        cy = int(M["m01"] / M["m00"])
                    else:
                        cx, cy = 0, 0
                    
                    # Calculate confidence based on area
                    confidence = min(1.0, area / self.max_area)
                    
                    # Store hand data
                    hand_data = {
                        "detected": True,
                        "fingers": finger_count,
                        "position": (cx, cy),
                        "confidence": confidence * self.sensitivity
                    }
                    
                    hands.append(hand_data)
                    
                except Exception as e:
                    # Skip this contour if processing fails
                    continue
        
        return hands
    
    def get_hand_data(self):
        """Get current hand tracking data"""
        return {
            "left": self.left_hand.copy(),
            "right": self.right_hand.copy(),
            "enabled": self.enabled,
            "fps": self.fps
        }
    
    def calibrate(self, duration=5):
        """Calibrate hand tracking by sampling skin colors"""
        if not self.camera or not self.camera.isOpened():
            return False
        
        print("Calibration: Place your hand in the center of the frame...")
        print(f"Sampling for {duration} seconds...")
        
        samples = []
        start_time = time.time()
        
        while time.time() - start_time < duration:
            ret, frame = self.camera.read()
            if not ret:
                continue
            
            # Get center region
            h, w = frame.shape[:2]
            center_x, center_y = w // 2, h // 2
            region_size = 50
            
            roi = frame[
                center_y - region_size:center_y + region_size,
                center_x - region_size:center_x + region_size
            ]
            
            # Convert to HSV and sample
            hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
            samples.append(hsv_roi.reshape(-1, 3))
            
            time.sleep(0.1)
        
        # Calculate new thresholds
        if samples:
            all_samples = np.vstack(samples)
            self.lower_skin = np.percentile(all_samples, 5, axis=0).astype(np.uint8)
            self.upper_skin = np.percentile(all_samples, 95, axis=0).astype(np.uint8)
            
            # Add some margin
            self.lower_skin[0] = max(0, self.lower_skin[0] - 5)
            self.upper_skin[0] = min(180, self.upper_skin[0] + 5)
            
            self.save_config()
            print("Calibration complete!")
            return True
        
        return False
    
    def test_detection(self, show_window=False):
        """Test hand detection with optional visualization"""
        if not self.running:
            return None
        
        if show_window and self.camera:
            ret, frame = self.camera.read()
            if ret:
                frame = cv2.flip(frame, 1)
                
                # Draw hand positions
                for hand_name, hand_data in [("Left", self.left_hand), ("Right", self.right_hand)]:
                    if hand_data["detected"]:
                        pos = hand_data["position"]
                        cv2.circle(frame, pos, 10, (0, 255, 0), -1)
                        cv2.putText(
                            frame,
                            f"{hand_name}: {hand_data['fingers']} fingers",
                            (pos[0] - 50, pos[1] - 20),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.5,
                            (0, 255, 0),
                            2
                        )
                
                # Show FPS
                cv2.putText(
                    frame,
                    f"FPS: {self.fps}",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 255, 0),
                    2
                )
                
                cv2.imshow("Finger Tracking Test", frame)
                cv2.waitKey(1)
        
        return self.get_hand_data()

# Global tracker instance
_tracker = None

def get_tracker():
    """Get global tracker instance"""
    global _tracker
    if _tracker is None:
        _tracker = FingerTracker()
    return _tracker

# Test if run directly
if __name__ == "__main__":
    print("Testing finger tracking...")
    tracker = get_tracker()
    
    if tracker.start():
        print("Tracking started. Press Ctrl+C to stop.")
        try:
            while True:
                data = tracker.test_detection(show_window=True)
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\nStopping...")
        finally:
            tracker.stop()
            cv2.destroyAllWindows()
    else:
        print("Failed to start tracking!")
