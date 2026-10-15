
#!/usr/bin/env python3
"""
Hikvision CCTV → AWS S3 Migration Script
Motion detection + Auto-backup to S3 + Glacier archiving
Author: Sathish's Cloud Setup
"""

import cv2
import boto3 # type: ignore
import numpy as np
from datetime import datetime
import time
import os
import sys
import threading
from pathlib import Path

# ============ CONFIGURATION ============
# UPDATE THESE VALUES FOR YOUR SETUP

# Hikvision Camera Details
CAMERA_IP = "192.168.1.50"  # Change to your camera IP
CAMERA_USERNAME = "admin"
CAMERA_PASSWORD = "12345"  # Change if you changed camera password
CAMERA_PORT = 554

# AWS Configuration
AWS_REGION = "ap-south-1"  # Mumbai region (cheapest for India)
S3_BUCKET = "sathish-cctv-motion-alerts"  # Change to your bucket name

# Motion Detection Settings
MOTION_THRESHOLD = 2000  # Pixels that changed (lower = more sensitive)
SENSITIVITY_LEVEL = "medium"  # "low", "medium", "high"
SAVE_INTERVAL = 15  # Save clips every 15 seconds
CLIP_DURATION = 30  # Each clip is 30 seconds

# Local Storage (temporary before upload)
TEMP_FOLDER = "./cctv_temp"
LOG_FILE = "./cctv_motion.log"

# ======================================

class HikvisionCCTVUploader:
    def __init__(self):
        self.s3 = boto3.client('s3', region_name=AWS_REGION)
        self.bucket = S3_BUCKET
        self.rtsp_url = None
        self.setup_rtsp_url()
        self.motion_detected = False
        self.frame_count = 0
        self.prev_frame = None
        
        # Create temp folder
        Path(TEMP_FOLDER).mkdir(exist_ok=True)
        
        # Setup logging
        self.log(f"🎥 Hikvision CCTV → AWS S3 Setup Started")
        self.log(f"Camera: {CAMERA_IP}:{CAMERA_PORT}")
        self.log(f"S3 Bucket: {self.bucket}")
        self.log(f"Region: {AWS_REGION}")
    
    def setup_rtsp_url(self):
        """Build RTSP URL for Hikvision camera"""
        # Try different RTSP paths for Hikvision
        self.rtsp_urls = [
            f"rtsp://{CAMERA_USERNAME}:{CAMERA_PASSWORD}@{CAMERA_IP}:{CAMERA_PORT}/stream",
            f"rtsp://{CAMERA_USERNAME}:{CAMERA_PASSWORD}@{CAMERA_IP}:{CAMERA_PORT}/h264/ch1/main/av_stream",
            f"rtsp://{CAMERA_USERNAME}:{CAMERA_PASSWORD}@{CAMERA_IP}:{CAMERA_PORT}/h264/ch1/sub/av_stream",
            f"rtsp://{CAMERA_IP}:{CAMERA_PORT}/stream",
        ]
        self.rtsp_url = self.rtsp_urls[0]  # Default
    
    def log(self, message):
        """Log to console and file"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"[{timestamp}] {message}"
        print(log_msg)
        
        with open(LOG_FILE, 'a') as f:
            f.write(log_msg + "\n")
    
    def test_camera_connection(self):
        """Test if RTSP connection works"""
        self.log("🔍 Testing camera connection...")
        
        for url in self.rtsp_urls:
            self.log(f"   Trying: {url.split('@')[-1]}")  # Hide password in log
            cap = cv2.VideoCapture(url)
            ret, frame = cap.read()
            cap.release()
            
            if ret:
                self.rtsp_url = url
                self.log(f"✅ Camera connected! Using RTSP path")
                return True
        
        self.log("❌ FAILED: Cannot connect to camera")
        self.log("   Check:")
        self.log(f"   1. Camera IP: {CAMERA_IP} (is it correct?)")
        self.log(f"   2. Username/Password: {CAMERA_USERNAME}")
        self.log(f"   3. Network: Is camera on same WiFi/network?")
        self.log(f"   4. Port: {CAMERA_PORT}")
        return False
    
    def test_s3_bucket(self):
        """Test if S3 bucket exists and is accessible"""
        self.log("🔍 Testing S3 bucket access...")
        try:
            self.s3.head_bucket(Bucket=self.bucket)
            self.log(f"✅ S3 Bucket accessible: {self.bucket}")
            return True
        except Exception as e:
            self.log(f"❌ S3 Error: {e}")
            self.log("   Check:")
            self.log("   1. AWS credentials configured (aws configure)")
            self.log(f"   2. Bucket exists: {self.bucket}")
            self.log("   3. Permissions: AmazonS3FullAccess")
            return False
    
    def detect_motion(self, frame1, frame2):
        """Detect motion between consecutive frames"""
        if frame1 is None:
            return False, 0
        
        # Resize for faster processing
        h, w = frame1.shape[:2]
        frame1_small = cv2.resize(frame1, (w//4, h//4))
        frame2_small = cv2.resize(frame2, (w//4, h//4))
        
        # Convert to grayscale
        gray1 = cv2.cvtColor(frame1_small, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(frame2_small, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur to reduce noise
        gray1 = cv2.GaussianBlur(gray1, (21, 21), 0)
        gray2 = cv2.GaussianBlur(gray2, (21, 21), 0)
        
        # Compute absolute difference
        diff = cv2.absdiff(gray1, gray2)
        _, thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)
        
        # Count white pixels (motion)
        motion_pixels = np.sum(thresh > 0)
        
        # Adjust threshold based on sensitivity
        thresholds = {
            "low": 5000,
            "medium": 2000,
            "high": 500
        }
        threshold = thresholds.get(SENSITIVITY_LEVEL, MOTION_THRESHOLD)
        
        return motion_pixels > threshold, motion_pixels
    
    def upload_to_s3(self, file_path, s3_key):
        """Upload file to S3"""
        try:
            self.log(f"📤 Uploading: {os.path.basename(file_path)}")
            self.s3.upload_file(
                file_path,
                self.bucket,
                s3_key,
                ExtraArgs={'ContentType': 'video/mp4'}
            )
            self.log(f"✅ Upload successful: s3://{self.bucket}/{s3_key}")
            
            # Delete local file after successful upload
            os.remove(file_path)
            return True
        except Exception as e:
            self.log(f"❌ Upload failed: {e}")
            return False
    
    def run(self):
        """Main loop: capture, detect motion, upload"""
        self.log("=" * 50)
        self.log("Starting CCTV Stream Processing...")
        self.log("=" * 50)
        
        # Test connections
        if not self.test_camera_connection():
            return
        
        if not self.test_s3_bucket():
            return
        
        self.log("")
        self.log("🟢 All checks passed! Starting stream...")
        self.log("Press Ctrl+C to stop\n")
        
        cap = cv2.VideoCapture(self.rtsp_url)
        
        if not cap.isOpened():
            self.log("❌ Cannot open RTSP stream")
            return
        
        # Get camera properties
        fps = int(cap.get(cv2.CAP_PROP_FPS)) or 25
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        self.log(f"📹 Resolution: {width}x{height} @ {fps}fps")
        
        # Video writer setup
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        temp_video_path = os.path.join(TEMP_FOLDER, 'temp_motion_clip.mp4')
        out = cv2.VideoWriter(temp_video_path, fourcc, fps, (width, height))
        
        self.prev_frame = None
        self.motion_detected = False
        self.frame_count = 0
        reconnect_attempts = 0
        
        try:
            while True:
                ret, frame = cap.read()
                
                if not ret:
                    self.log("⚠️ Connection lost, attempting reconnect...")
                    reconnect_attempts += 1
                    if reconnect_attempts > 3:
                        self.log("❌ Failed to reconnect after 3 attempts")
                        break
                    time.sleep(5)
                    cap = cv2.VideoCapture(self.rtsp_url)
                    continue
                
                reconnect_attempts = 0
                self.frame_count += 1
                
                # Detect motion
                if self.prev_frame is not None:
                    is_motion, pixels = self.detect_motion(self.prev_frame, frame)
                    
                    if is_motion:
                        self.motion_detected = True
                        if self.frame_count % 10 == 0:
                            self.log(f"🔴 MOTION: {pixels} pixels changed")
                
                # Write frame to video
                out.write(frame)
                
                # Save and upload clip periodically
                if self.frame_count % (fps * SAVE_INTERVAL) == 0:
                    if self.motion_detected:
                        out.release()
                        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
                        s3_key = f'motion_alerts/hikvision_{timestamp}.mp4'
                        
                        # Upload in background
                        upload_thread = threading.Thread(
                            target=self.upload_to_s3,
                            args=(temp_video_path, s3_key)
                        )
                        upload_thread.daemon = True
                        upload_thread.start()
                        
                        # Start new video
                        out = cv2.VideoWriter(temp_video_path, fourcc, fps, (width, height))
                        self.motion_detected = False
                    else:
                        self.log(f"⏳ No motion | {datetime.now().strftime('%H:%M:%S')}")
                
                self.prev_frame = frame.copy()
        
        except KeyboardInterrupt:
            self.log("\n✋ Stopping CCTV stream...")
        except Exception as e:
            self.log(f"❌ Error: {e}")
        finally:
            cap.release()
            out.release()
            self.log("✅ CCTV stopped")


def main():
    print("""
    ╔════════════════════════════════════════╗
    ║  Hikvision 2MP → AWS S3 Uploader       ║
    ║  Motion Detection + Auto Backup        ║
    ╚════════════════════════════════════════╝
    """)
    
    # Check configuration
    if CAMERA_IP == "192.168.1.50":
        print("⚠️  WARNING: Using default camera IP (192.168.1.50)")
        print("    Please update CAMERA_IP in the script if different\n")
    
    if S3_BUCKET == "sathish-cctv-motion-alerts":
        print("⚠️  WARNING: Using default S3 bucket name")
        print("    Change S3_BUCKET if you created a different bucket\n")
    
    input("Press Enter to continue...")
    
    uploader = HikvisionCCTVUploader()
    uploader.run()


if __name__ == '__main__':
    main()



