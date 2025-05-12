"""
Sample code for Raspberry Pi to integrate with the logistics bot dashboard.
This demonstrates how to update the Firebase database when:
1. The bot reaches a checkpoint (location update)
2. The camera detects materials (using OpenCV)
"""

import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import time
import cv2
import numpy as np
import os
from firebase_integration import FirebaseConnector
import RPi.GPIO as GPIO
from time import sleep
from picamera2 import Picamera2

# ===== CONFIGURATION =====
# Replace with your Firebase project details
FIREBASE_CRED_PATH = "path/to/serviceAccountKey.json"
FIREBASE_DB_URL = "https://YOUR_PROJECT_ID-default-rtdb.firebaseio.com"

# Checkpoint locations (these should match the dashboard's expected values)
LOCATIONS = ["Start", "Building A", "Building B", "Building C"]

# OpenCV detection parameters
# These are example thresholds - you'll need to adjust for your specific setup
HSV_RANGES = {
    "dispatchReady": [(35, 50, 50), (85, 255, 255)],  # Green
    "damaged": [(0, 50, 50), (10, 255, 255)],         # Red
    "eWaste": [(120, 50, 50), (140, 255, 255)],       # Purple
    "rawMaterials": [(100, 50, 50), (120, 255, 255)]  # Blue
}

# Minimum contour area to consider a detection valid
MIN_CONTOUR_AREA = 1000

# ===== FIREBASE SETUP =====
def initialize_firebase():
    """Initialize Firebase connection"""
    try:
        # Check if the credential file exists
        if not os.path.exists(FIREBASE_CRED_PATH):
            print(f"Error: Firebase credentials file not found at {FIREBASE_CRED_PATH}")
            return False
            
        cred = credentials.Certificate(FIREBASE_CRED_PATH)
        firebase_admin.initialize_app(cred, {
            'databaseURL': FIREBASE_DB_URL
        })
        print("Firebase initialized successfully")
        return True
    except Exception as e:
        print(f"Error initializing Firebase: {e}")
        return False

# ===== FIREBASE UPDATE FUNCTIONS =====
def update_location(location):
    """Update the bot's current location in Firebase"""
    if location not in LOCATIONS:
        print(f"Warning: {location} is not a valid location. Valid locations: {LOCATIONS}")
        return False
        
    try:
        db.reference('currentLocation').set(location)
        db.reference('lastUpdate').set(int(time.time() * 1000))  # Current time in milliseconds
        print(f"Location updated to: {location}")
        return True
    except Exception as e:
        print(f"Error updating location: {e}")
        return False

def update_materials(materials_dict):
    """Update the detected materials counts in Firebase"""
    try:
        # Get current values
        current_data = db.reference('detectedMaterials').get() or {
            "dispatchReady": 0,
            "damaged": 0,
            "eWaste": 0,
            "rawMaterials": 0
        }
        
        # Update with new values
        for key, value in materials_dict.items():
            if key in current_data:
                current_data[key] += value
        
        # Set the updated values
        db.reference('detectedMaterials').set(current_data)
        db.reference('lastUpdate').set(int(time.time() * 1000))
        print(f"Materials updated: {materials_dict}")
        return True
    except Exception as e:
        print(f"Error updating materials: {e}")
        return False

# ===== CHECKPOINT DETECTION =====
def detect_checkpoint(frame, checkpoint_markers):
    """
    Detect if the bot is at a checkpoint using computer vision
    
    Args:
        frame: Camera frame
        checkpoint_markers: Dictionary mapping marker IDs to locations
        
    Returns:
        Location name if detected, None otherwise
    """
    # This is a simplified example - you would replace with actual marker detection
    # For example, you could use ArUco markers, QR codes, or color markers
    
    # Example using ArUco markers (you'd need to add actual implementation):
    # aruco_dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_50)
    # aruco_params = cv2.aruco.DetectorParameters_create()
    # corners, ids, rejected = cv2.aruco.detectMarkers(frame, aruco_dict, parameters=aruco_params)
    
    # if ids is not None:
    #     for i, marker_id in enumerate(ids.flatten()):
    #         if marker_id in checkpoint_markers:
    #             return checkpoint_markers[marker_id]
    
    # Placeholder - In actual implementation, return the location name when detected
    return None

# ===== MATERIAL DETECTION =====
def detect_materials(frame):
    """
    Detect materials using color thresholding
    
    Args:
        frame: Camera frame
        
    Returns:
        Dictionary with counts of each material type detected
    """
    # Initialize results
    results = {
        "dispatchReady": 0,
        "damaged": 0,
        "eWaste": 0,
        "rawMaterials": 0
    }
    
    # Convert to HSV for better color detection
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # Detect each material type by color
    for material, (lower, upper) in HSV_RANGES.items():
        # Convert HSV ranges to numpy arrays
        lower_bound = np.array(lower)
        upper_bound = np.array(upper)
        
        # Create mask for this color
        mask = cv2.inRange(hsv, lower_bound, upper_bound)
        
        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Count valid detections
        count = 0
        for contour in contours:
            if cv2.contourArea(contour) > MIN_CONTOUR_AREA:
                count += 1
                
        results[material] = count
    
    return results

# ===== MAIN FUNCTION =====
def main():
    """Main function to run the bot's detection and update loop"""
    # Initialize Firebase
    if not initialize_firebase():
        print("Failed to initialize Firebase. Exiting.")
        return
    
    # Initialize camera
    print("Initializing camera...")
    cap = cv2.VideoCapture(0)  # Use 0 for default camera
    
    if not cap.isOpened():
        print("Error: Could not open camera")
        return
    
    # Define checkpoint markers (marker ID -> location)
    # In your actual implementation, you'd use QR codes or ArUco markers
    checkpoint_markers = {
        1: "Start",
        2: "Building A",
        3: "Building B",
        4: "Building C"
    }
    
    # Set initial location
    current_location = "Start"
    update_location(current_location)
    
    print("Bot monitoring started. Press 'q' to quit.")
    
    try:
        last_materials_update = time.time()
        materials_update_interval = 5  # Update materials every 5 seconds
        
        while True:
            # Capture frame
            ret, frame = cap.read()
            if not ret:
                print("Error: Failed to capture frame")
                break
            
            # Detect checkpoint (if location has changed)
            location = detect_checkpoint(frame, checkpoint_markers)
            if location and location != current_location:
                current_location = location
                update_location(current_location)
            
            # Periodically detect and update materials
            current_time = time.time()
            if current_time - last_materials_update > materials_update_interval:
                materials = detect_materials(frame)
                if any(materials.values()):  # Only update if something was detected
                    update_materials(materials)
                last_materials_update = current_time
            
            # Display frame (remove in production)
            cv2.imshow('Camera Feed', frame)
            
            # Check for exit key
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    except KeyboardInterrupt:
        print("Monitoring interrupted by user")
    finally:
        # Clean up
        cap.release()
        cv2.destroyAllWindows()
        print("Bot monitoring stopped")

if __name__ == "__main__":
    main() 