# Firebase Setup Guide

This guide explains how to set up your Firebase credentials to connect your Raspberry Pi bot to the web dashboard.

## Step 1: Access Firebase Service Account

1. Go to the [Firebase Console](https://console.firebase.google.com/)
2. Select your project "log-bot-df281"
3. Click on the gear icon (⚙️) in the left sidebar to access Project settings
4. Navigate to the "Service accounts" tab

## Step 2: Generate Service Account Key

1. In the "Service accounts" tab, you'll see the Firebase Admin SDK section
2. Click the "Generate new private key" button
3. Click "Generate key" in the confirmation dialog
4. A JSON file will be downloaded to your computer

## Step 3: Transfer to Raspberry Pi

1. Rename the downloaded JSON file to `serviceAccountKey.json`
2. Transfer this file to your Raspberry Pi in the same directory as your bot code
3. You can use SCP, USB drive, or any file transfer method:

   Using SCP from your computer:
   ```bash
   scp /path/to/serviceAccountKey.json pi@your_pi_ip:/path/to/project/
   ```

## Step 4: Test the Connection

1. Ensure you've installed the Firebase Admin SDK on your Pi:
   ```bash
   pip install firebase-admin
   ```

2. Run the test script to verify the connection:
   ```bash
   python test_firebase.py
   ```

3. If successful, you should see updates on your web dashboard

## Troubleshooting

If you encounter issues:

1. **Connection Error**: Ensure you have internet connectivity on your Pi
2. **Authentication Error**: Verify that your serviceAccountKey.json is correctly formatted and contains valid credentials
3. **Database URL Error**: Check that the databaseURL in the code matches your Firebase project
4. **Module Not Found**: Make sure the firebase-admin package is installed

## Security Note

Keep your serviceAccountKey.json secure as it provides admin access to your Firebase project. Never share it or commit it to public repositories. 