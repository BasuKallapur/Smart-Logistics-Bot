# Smart Logistics Bot - Firebase Integration

This module provides integration between the Smart Logistics Bot and Firebase Realtime Database for tracking the bot's location and material counts.

![image](https://github.com/user-attachments/assets/22d4d346-caed-408b-8922-caa9bf26603c)


## Setup Instructions

### 1. Firebase Setup

1. Create a Firebase account at [firebase.google.com](https://firebase.google.com/)
2. Create a new Firebase project
3. Enable Realtime Database (Create Database > Start in test mode)
4. Go to Project Settings > Service Accounts
5. Click "Generate new private key"
6. Download the JSON file and save it as `serviceAccountKey.json` in the root directory of this project

### 2. Install Dependencies

```bash
pip install firebase-admin
```

## Files Overview

- `firebase_integration.py`: The main integration module that provides the FirebaseConnector class
- `test_firebase.py`: A test script to verify Firebase connection and data updates

## Usage

### Basic Usage

```python
from firebase_integration import get_firebase_connector

# Initialize Firebase connector
firebase = get_firebase_connector()

# Update bot location
firebase.update_location("Building A")

# Update material counts
firebase.update_materials({
    "dispatchReady": 3,  # circles
    "damaged": 1,        # squares
    "eWaste": 2,         # triangles
    "rawMaterials": 5    # X shapes
})
```

### Testing the Integration

Run the test script to verify that your Firebase integration is working correctly:

```bash
python test_firebase.py
```

This will run tests for:
- Firebase connection
- Location updates
- Material count updates
- Local logging fallback (when Firebase is unavailable)

## Firebase Database Structure

The Firebase Realtime Database will have the following structure:

```
|-- currentLocation: string (e.g., "Building A")
|-- detectedMaterials
|   |-- dispatchReady: number (circles)
|   |-- damaged: number (squares) 
|   |-- eWaste: number (triangles)
|   |-- rawMaterials: number (X shapes)
|-- lastUpdate: timestamp
```

## Troubleshooting

- If the bot can't connect to Firebase, it will log data locally to `material_logs.txt`
- Make sure `serviceAccountKey.json` is in the correct location
- Check your internet connection
- Verify that your Firebase project is properly set up with Realtime Database enabled

---

## 👥 Team Members

- Abhilash Dandu
- Basavaraj Kallapur
- Bhavana Yadav
- C Harsha

  ![6cf7dbbc-66d3-41ee-8e91-9fa3cfd6c397](https://github.com/user-attachments/assets/c0c8e6c4-8669-4ee8-87bc-5ca6bb368670)



