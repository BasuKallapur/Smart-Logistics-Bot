"""
Firebase Integration module for Smart Logistics Bot.

This module provides a FirebaseConnector class to establish connection
with Firebase Realtime Database and update bot location and material counts.
"""

import os
import time
import json
from datetime import datetime
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

class FirebaseConnector:
    """
    A class to handle Firebase database operations for the logistics bot.
    
    Attributes:
        connected (bool): Status of Firebase connection
        service_account_path (str): Path to Firebase service account credentials
        database_url (str): Firebase Realtime Database URL
    """
    
    def __init__(self, service_account_path="serviceAccountKey.json"):
        """
        Initialize the Firebase connector with credentials.
        
        Args:
            service_account_path (str): Path to the service account key JSON file
        """
        self.connected = False
        self.service_account_path = service_account_path
        self.database_url = None
        
        try:
            # Attempt to initialize Firebase
            if os.path.exists(service_account_path):
                cred = credentials.Certificate(service_account_path)
                
                # Extract database URL from service account file
                with open(service_account_path, 'r') as f:
                    service_account = json.load(f)
                    project_id = service_account.get('project_id')
                    self.database_url = f"https://{project_id}-default-rtdb.firebaseio.com"
                
                # Initialize Firebase app
                firebase_admin.initialize_app(cred, {
                    'databaseURL': self.database_url
                })
                
                print(f"[{self._get_timestamp()}] Firebase connection successful!")
                self.connected = True
                
                # Initialize database structure if it doesn't exist
                self._initialize_database()
                
            else:
                print(f"[{self._get_timestamp()}] Error: Service account file not found at {service_account_path}")
                print(f"[{self._get_timestamp()}] Will log data locally instead.")
                
        except Exception as e:
            print(f"[{self._get_timestamp()}] Firebase connection error: {str(e)}")
            print(f"[{self._get_timestamp()}] Will log data locally instead.")
    
    def _get_timestamp(self):
        """Get current timestamp for logging."""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def _initialize_database(self):
        """Initialize database structure if it doesn't exist."""
        if self.connected:
            # Check if database structure exists, if not create it
            try:
                # Set initial values if they don't exist
                location_ref = db.reference('currentLocation')
                if location_ref.get() is None:
                    location_ref.set("Start")
                
                materials_ref = db.reference('detectedMaterials')
                if materials_ref.get() is None:
                    materials_ref.set({
                        "dispatchReady": 0,  # circles
                        "damaged": 0,        # squares
                        "eWaste": 0,         # triangles
                        "rawMaterials": 0    # X shapes
                    })
                
                # Set last update time
                db.reference('lastUpdate').set(int(time.time() * 1000))
            except Exception as e:
                print(f"[{self._get_timestamp()}] Error initializing database: {str(e)}")
                self.connected = False
    
    def update_location(self, location):
        """
        Update the bot's current location in Firebase.
        
        Args:
            location (str): Current location of the bot (e.g., "Start", "Building A")
            
        Returns:
            bool: True if update was successful, False otherwise
        """
        if not self.connected:
            self._log_local_data(f"Location: {location}")
            return False
        
        try:
            db.reference('currentLocation').set(location)
            db.reference('lastUpdate').set(int(time.time() * 1000))
            print(f"[{self._get_timestamp()}] Updated location to: {location}")
            return True
        except Exception as e:
            print(f"[{self._get_timestamp()}] Error updating location: {str(e)}")
            self._log_local_data(f"Location: {location}")
            return False
    
    def update_materials(self, materials_dict):
        """
        Update the detected materials count in Firebase.
        
        Args:
            materials_dict (dict): Dictionary containing the counts of different materials
                {
                    "dispatchReady": int,  # circles
                    "damaged": int,        # squares
                    "eWaste": int,         # triangles
                    "rawMaterials": int    # X shapes
                }
                
        Returns:
            bool: True if update was successful, False otherwise
        """
        if not self.connected:
            self._log_local_data(f"Materials: {materials_dict}")
            return False
        
        try:
            db.reference('detectedMaterials').set(materials_dict)
            db.reference('lastUpdate').set(int(time.time() * 1000))
            print(f"[{self._get_timestamp()}] Updated materials: {materials_dict}")
            return True
        except Exception as e:
            print(f"[{self._get_timestamp()}] Error updating materials: {str(e)}")
            self._log_local_data(f"Materials: {materials_dict}")
            return False
    
    def _log_local_data(self, data):
        """
        Log data locally if Firebase connection is unavailable.
        
        Args:
            data (str): Data to log
        """
        try:
            with open("material_logs.txt", "a") as f:
                f.write(f"[{self._get_timestamp()}] {data}\n")
            print(f"[{self._get_timestamp()}] Logged locally: {data}")
        except Exception as e:
            print(f"[{self._get_timestamp()}] Error logging locally: {str(e)}")

# For testing purposes
if __name__ == "__main__":
    firebase = FirebaseConnector()
    
    if firebase.connected:
        # Test location update
        firebase.update_location("Building A")
        
        # Test materials update
        firebase.update_materials({
            "dispatchReady": 3,  # circles
            "damaged": 1,        # squares
            "eWaste": 2,         # triangles
            "rawMaterials": 5    # X shapes
        })
    else:
        print("Firebase connection test failed. Check your credentials and internet connection.")

# Function to get a Firebase connector instance - for simpler imports
def get_firebase_connector(credentials_path="serviceAccountKey.json"):
    """Get a configured Firebase connector instance."""
    return FirebaseConnector(credentials_path) 