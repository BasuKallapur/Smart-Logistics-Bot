"""
Smart Logistics Bot with Firebase Integration
- Moves between buildings in a rectangular path
- Captures images and detects symbols
- Updates Firebase with location and material counts
- Connects to web dashboard
"""
import RPi.GPIO as GPIO
from time import sleep
import cv2
import numpy as np
from picamera2 import Picamera2
import time
import os

# Import Firebase connector
from firebase_integration import FirebaseConnector

# --- Create directories for saving images ---
os.makedirs("captured_images", exist_ok=True)

# --- Location Tracking ---
locations = ["Start", "Building A", "Building B", "Building C"]
current_location_index = 0

# --- GPIO Motor Setup ---
GPIO.setwarnings(False)
# Right Motor
in1 = 17
in2 = 27
en_a = 4
# Left Motor
in3 = 5
in4 = 6
en_b = 13

GPIO.setmode(GPIO.BCM)
for pin in [in1, in2, en_a, in3, in4, en_b]:
    GPIO.setup(pin, GPIO.OUT)

# Initialize PWM with moderate speed
pwm_a = GPIO.PWM(en_a, 100)
pwm_b = GPIO.PWM(en_b, 100)
pwm_a.start(75)
pwm_b.start(75)

# --- Initialize Firebase ---
print("Initializing Firebase connection...")
firebase = FirebaseConnector()
if firebase.connected:
    firebase.initialize_data()
    print("Firebase connected and initialized")
else:
    print("Firebase connection failed. Will log data locally only.")

# --- Motor Control Functions ---
def stop_car():
    """Stop the car by setting all motor control pins to LOW."""
    GPIO.output(in1, GPIO.LOW)
    GPIO.output(in2, GPIO.LOW)
    GPIO.output(in3, GPIO.LOW)
    GPIO.output(in4, GPIO.LOW)
    print("Car stopped")
    # Short pause to ensure the bot is completely stopped
    sleep(0.3)

def move_car(duration=3):
    """Move forward for a set duration then stop."""
    # Forward motion configuration
    GPIO.output(in1, GPIO.HIGH)  # Right motor forward
    GPIO.output(in2, GPIO.LOW)
    GPIO.output(in4, GPIO.HIGH)  # Left motor forward
    GPIO.output(in3, GPIO.LOW)
    
    print("Moving forward...")
    sleep(duration)
    stop_car()

def turn_right(duration=1.5):
    """
    Turn right by activating only one set of wheels.
    Based on the provided snippet.
    """
    # First come to a complete stop
    stop_car()
    
    # Right turn configuration from your snippet
    GPIO.output(in1, GPIO.LOW)   # Right motor backward
    GPIO.output(in2, GPIO.HIGH)
    GPIO.output(in3, GPIO.LOW)   # Left motor stopped
    GPIO.output(in4, GPIO.LOW)
    
    print("Turning right...")
    sleep(duration)
    
    # Return to stop state
    stop_car()

# --- Initialize Camera ---
print("Initializing camera...")
picam2 = Picamera2()
picam2.preview_configuration.main.size = (640, 480)
picam2.preview_configuration.main.format = "RGB888"
picam2.configure("preview")
picam2.start()
time.sleep(2)  # Camera warm-up time
print("Camera initialized")

# --- Image Processing Functions ---
def capture_and_process_image():
    """Capture a single image and process it to detect symbols."""
    global current_location_index
    location = locations[current_location_index]
    
    print(f"\nProcessing image at {location}...")
    
    # Capture a single frame
    frame = picam2.capture_array()
    
    # Save original image
    timestamp = int(time.time())
    filename = f"captured_images/{location.replace(' ', '_')}_{timestamp}.jpg"
    cv2.imwrite(filename, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
    print(f"Image saved as {filename}")
    
    # Define ROI - adjust these values as needed
    roi_x, roi_y, roi_w, roi_h = 100, 100, 440, 280
    
    # Draw the ROI rectangle on the full frame
    cv2.rectangle(frame, (roi_x, roi_y), (roi_x + roi_w, roi_y + roi_h), (0, 255, 0), 2)
    
    # Extract the ROI for symbol detection
    roi = frame[roi_y:roi_y + roi_h, roi_x:roi_x + roi_w]
    
    # Convert ROI to HSV color space to segment red symbols
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    
    # Define two red ranges in HSV (red wraps around the hue boundaries)
    lower_red1 = np.array([0, 100, 100])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([160, 100, 100])
    upper_red2 = np.array([179, 255, 255])
    
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    red_mask = cv2.bitwise_or(mask1, mask2)
    
    # Use morphological operations to reduce noise
    kernel = np.ones((5, 5), np.uint8)
    red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_OPEN, kernel)
    
    # Find contours on the masked image
    contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Map symbols to material categories
    symbol_counts = {
        "Circle": 0,  # dispatchReady
        "Triangle": 0,  # eWaste
        "Square": 0,  # damaged
        "X": 0        # rawMaterials
    }
    
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < 300:  # Filter out small noise
            continue
        
        # Calculate perimeter and approximate the contour shape
        peri = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.04 * peri, True)
        shape_name = None

        # Shape classification using contour approximation
        if len(approx) == 3:
            shape_name = "Triangle"
        elif len(approx) == 4:
            # Determine if the quadrilateral is a square (check aspect ratio)
            x, y, w, h = cv2.boundingRect(approx)
            ratio = float(w) / h
            if 0.9 <= ratio <= 1.1:
                shape_name = "Square"
            else:
                shape_name = "Square"  # For this prototype, treat all quadrilaterals as squares
        elif len(approx) > 4:
            # Use circularity measure
            circularity = 4 * np.pi * area / (peri * peri)
            if circularity > 0.75:
                shape_name = "Circle"
            else:
                # Try to detect "X" by checking for crossing lines
                x, y, w, h = cv2.boundingRect(cnt)
                symbol_roi = red_mask[y:y+h, x:x+w]
                
                # Edge detection on the symbol ROI
                edges = cv2.Canny(symbol_roi, 50, 150)
                lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=20, 
                                       minLineLength=0.5 * min(w, h), maxLineGap=10)
                if lines is not None and len(lines) >= 2:
                    # Calculate angles of detected lines (in degrees)
                    angles = []
                    for line in lines:
                        x1, y1, x2, y2 = line[0]
                        angle = np.degrees(np.arctan2(y2 - y1, x2 - x1))
                        angles.append(angle)
                    # Look for two lines with a significant angle difference
                    found_x = False
                    for i in range(len(angles)):
                        for j in range(i + 1, len(angles)):
                            diff = abs(angles[i] - angles[j])
                            if 40 < diff < 140:
                                found_x = True
                                break
                        if found_x:
                            break
                    if found_x:
                        shape_name = "X"
                    else:
                        shape_name = "Circle"  # Fallback classification
                else:
                    shape_name = "Circle"
        
        # Update the count if the shape is classified
        if shape_name:
            symbol_counts[shape_name] += 1
            # Draw the contour and label on the ROI for visualization
            cv2.drawContours(roi, [approx], -1, (0, 255, 0), 2)
            # Get the centroid for better label positioning
            M = cv2.moments(cnt)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                # Position the label near the centroid
                cv2.putText(roi, shape_name, (cx - 30, cy), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

    # Display the counts on the frame
    y0, dy = 30, 30
    for i, (shape, count) in enumerate(symbol_counts.items()):
        text = f"{shape}: {count}"
        cv2.putText(frame, text, (10, y0 + i * dy), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    
    # Add location text to the image
    cv2.putText(frame, f"Location: {location}", (10, 150), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
    
    # Save the annotated image
    annotated_filename = f"captured_images/{location.replace(' ', '_')}_{timestamp}_annotated.jpg"
    cv2.imwrite(annotated_filename, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
    
    # Display the image with a 3-second pause
    cv2.imshow("Material Detection", frame)
    cv2.waitKey(3000)
    cv2.destroyAllWindows()
    
    # Convert symbol counts to material categories for Firebase integration
    material_counts = {
        "dispatchReady": symbol_counts["Circle"],
        "damaged": symbol_counts["Square"],
        "eWaste": symbol_counts["Triangle"],
        "rawMaterials": symbol_counts["X"]
    }
    
    # Log the results
    print(f"\nDetection Results at {location}:")
    print(f"  - Dispatch Ready (Circles): {material_counts['dispatchReady']}")
    print(f"  - Damaged Items (Squares): {material_counts['damaged']}")
    print(f"  - eWaste (Triangles): {material_counts['eWaste']}")
    print(f"  - Raw Materials (X): {material_counts['rawMaterials']}")
    
    # Update Firebase with material counts
    update_firebase_data(location, material_counts)
    
    return material_counts

def update_firebase_data(location, material_counts):
    """Update Firebase with location and material data."""
    if not firebase.connected:
        # Log locally if Firebase connection failed
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"{timestamp} - {location}: {material_counts}\n"
        with open("material_logs.txt", "a") as log_file:
            log_file.write(log_entry)
        print("Data logged locally only (Firebase not connected)")
        return
    
    # Update Firebase
    firebase.update_location(location)
    firebase.update_materials(material_counts)
    print("Data sent to Firebase dashboard")

def navigate_to_next_checkpoint():
    """
    Navigate from current location to the next, following the rectangular path in the diagram.
    Path: Start → Building A → Building B → Building C → Start
    """
    global current_location_index
    
    # Get current location and determine next location
    current = locations[current_location_index]
    next_index = (current_location_index + 1) % len(locations)
    next_location = locations[next_index]
    
    print(f"\nNavigating from {current} to {next_location}...")
    
    # Following the rectangular path shown in the diagram
    if current == "Start" and next_location == "Building A":
        # Start → Building A: Move forward
        print("Path: Start → Building A (moving forward)")
        move_car(3)
    
    elif current == "Building A" and next_location == "Building B":
        # Building A → Building B: Move right
        print("Path: Building A → Building B (turning right, then moving forward)")
        turn_right(1.5)  # Using your turning logic
        move_car(3)
    
    elif current == "Building B" and next_location == "Building C":
        # Building B → Building C: Move down
        print("Path: Building B → Building C (turning right, then moving forward)")
        turn_right(1.5)  # Using your turning logic
        move_car(3)
    
    elif current == "Building C" and next_location == "Start":
        # Building C → Start: Move left
        print("Path: Building C → Start (turning right, then moving forward)")
        turn_right(1.5)  # Using your turning logic
        move_car(3)
    
    # Update the current location
    current_location_index = next_index
    print(f"Arrived at {next_location}")
    
    # Update Firebase with new location immediately
    if firebase.connected:
        firebase.update_location(next_location)
    
    sleep(1)  # Pause briefly at the new location

# --- Main Execution Logic ---
try:
    print("\n==== Smart Logistics Bot with Firebase Integration Started ====")
    print(f"Current location: {locations[current_location_index]}")
    
    # Update Firebase with initial location
    if firebase.connected:
        firebase.update_location(locations[current_location_index])
    
    print("Press Ctrl+C to stop the program at any time")
    
    # Ask user to confirm before starting movement
    input("Press Enter to begin the route...")
    
    # Navigate through the full rectangular path
    # We need 4 moves to complete the full circuit: Start→A→B→C→Start
    for i in range(4):  # 4 segments in the rectangular path
        current = locations[current_location_index]
        
        # Process at each location except Start
        if current != "Start":
            capture_and_process_image()
        else:
            print("\nAt Start location - no processing needed")
        
        # Optional: Uncomment to require user confirmation between movements
        # input(f"Press Enter to move from {current} to next location...")
        
        # Move to next location (skip after completing the full circuit)
        if i < 3:  # Stop after returning to Start
            navigate_to_next_checkpoint()
    
    print("\n==== Full route completed! ====")
    print("The bot has returned to the Start position")

except KeyboardInterrupt:
    print("\n\nProgram interrupted by user")

except Exception as e:
    print(f"\nError encountered: {e}")

finally:
    # Clean up
    stop_car()
    GPIO.cleanup()
    cv2.destroyAllWindows()
    print("\n==== Resources cleaned up, program exited ====") 