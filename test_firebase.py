#!/usr/bin/env python3
"""
Test script for the Firebase integration module.
This script tests the connection to Firebase and basic data update operations.
"""

import os
import time
from firebase_integration import FirebaseConnector

def test_firebase_connection():
    """Test the basic Firebase connection and updates."""
    print("Testing Firebase connection...")
    
    # Check if credentials file exists
    if not os.path.exists("serviceAccountKey.json"):
        print("Error: serviceAccountKey.json not found in the current directory.")
        print("Please download your service account key from Firebase console.")
        print("Instructions:")
        print("1. Go to Firebase console > Project settings > Service accounts")
        print("2. Click 'Generate new private key'")
        print("3. Save the file as 'serviceAccountKey.json' in this directory")
        return False
    
    # Initialize Firebase connection
    firebase = FirebaseConnector()
    
    if not firebase.connected:
        print("Firebase connection failed.")
        print("Check your credentials file and internet connection.")
        return False
    
    print("Firebase connection successful!")
    
    # Test location update
    print("\nTesting location update...")
    result = firebase.update_location("Test Location")
    if result:
        print("✓ Location update successful")
    else:
        print("✗ Location update failed")
    
    # Test materials update
    print("\nTesting materials update...")
    materials = {
        "dispatchReady": 5,  # circles
        "damaged": 2,        # squares
        "eWaste": 3,         # triangles
        "rawMaterials": 10   # X shapes
    }
    
    result = firebase.update_materials(materials)
    if result:
        print("✓ Materials update successful")
    else:
        print("✗ Materials update failed")
    
    return True

def test_local_logging():
    """Test local logging when Firebase is unavailable."""
    print("\nTesting local logging fallback...")
    
    # Temporarily rename the credentials file to simulate connection failure
    if os.path.exists("serviceAccountKey.json"):
        os.rename("serviceAccountKey.json", "serviceAccountKey.json.backup")
        
        try:
            # Initialize Firebase without valid credentials
            firebase = FirebaseConnector()
            
            # Should log locally instead
            firebase.update_location("Offline Location")
            firebase.update_materials({
                "dispatchReady": 1,
                "damaged": 1,
                "eWaste": 1,
                "rawMaterials": 1
            })
            
            # Check if log file was created
            if os.path.exists("material_logs.txt"):
                print("✓ Local logging successful")
                print("Check material_logs.txt for the logged data")
            else:
                print("✗ Local logging failed")
                
        finally:
            # Restore the credentials file
            os.rename("serviceAccountKey.json.backup", "serviceAccountKey.json")
    else:
        print("Skipping local logging test (no credentials file found)")

if __name__ == "__main__":
    print("===== Firebase Integration Test =====")
    
    connection_success = test_firebase_connection()
    
    if connection_success:
        test_local_logging()
    
    print("\nTests completed!")
    print("If all tests passed, the Firebase integration is working correctly.") 