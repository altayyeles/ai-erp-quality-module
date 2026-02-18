"""
Visual Anomaly Detection Module

This module implements OpenCV-based anomaly detection for visual inspection,
identifying unusual patterns in images.

Key Features:
- Histogram analysis for brightness anomalies
- Noise detection
- Texture analysis
- Anomaly scoring (0.0-1.0)
- Anomaly type classification
- Confidence scoring
"""

import cv2
import numpy as np
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class AnomalyDetector:
    """
    OpenCV-based visual anomaly detection system.
    
    Detects anomalies in images using histogram analysis, noise detection,
    and texture analysis techniques.
    """
    
    def __init__(self):
        """Initialize the anomaly detector."""
        logger.info("AnomalyDetector initialized")
    
    def detect_bytes(self, image_bytes: bytes) -> Dict:
        """
        Detect visual anomalies in an image from raw bytes.
        
        Args:
            image_bytes: Raw image data as bytes
            
        Returns:
            Dictionary with detection results including:
                - is_anomaly: Boolean indicating if anomaly detected
                - anomaly_score: Severity score (0.0-1.0)
                - anomaly_type: Type of anomaly (NONE/BRIGHTNESS/NOISE/TEXTURE/DEFECT)
                - confidence: Confidence in detection (0.0-1.0)
                - details: Additional analysis details
                
        Raises:
            ValueError: If image data is invalid
        """
        try:
            # Convert bytes to numpy array
            nparr = np.frombuffer(image_bytes, np.uint8)
            
            # Decode image
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                raise ValueError("Failed to decode image. Invalid image format.")
            
            logger.info(f"Analyzing image for anomalies: {image.shape}")
            
            # Perform anomaly detection
            result = self._detect_anomalies(image)
            
            logger.info(f"✓ Analysis complete: {result['anomaly_type']} (score: {result['anomaly_score']:.3f})")
            
            return result
            
        except Exception as e:
            logger.error(f"Error during anomaly detection: {e}")
            raise ValueError(f"Anomaly detection failed: {str(e)}")
    
    def _detect_anomalies(self, image: np.ndarray) -> Dict:
        """
        Detect anomalies in the image using multiple techniques.
        
        Args:
            image: OpenCV image (BGR format)
            
        Returns:
            Dictionary with detection results
        """
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Run multiple anomaly detection techniques
        brightness_anomaly = self._detect_brightness_anomaly(gray)
        noise_anomaly = self._detect_noise_anomaly(gray)
        texture_anomaly = self._detect_texture_anomaly(gray)
        defect_anomaly = self._detect_defect_anomaly(gray)
        
        # Aggregate results
        anomalies = {
            'BRIGHTNESS': brightness_anomaly,
            'NOISE': noise_anomaly,
            'TEXTURE': texture_anomaly,
            'DEFECT': defect_anomaly
        }
        
        # Find the most severe anomaly
        max_anomaly_type = max(anomalies, key=lambda k: anomalies[k]['score'])
        max_score = anomalies[max_anomaly_type]['score']
        
        # Determine if it's an anomaly (threshold: 0.5)
        is_anomaly = max_score >= 0.5
        
        # Set anomaly type
        if not is_anomaly:
            anomaly_type = "NONE"
            confidence = 1.0 - max_score  # High confidence in "no anomaly"
        else:
            anomaly_type = max_anomaly_type
            confidence = max_score
        
        # Compile details
        details = {
            'brightness_score': round(brightness_anomaly['score'], 3),
            'noise_score': round(noise_anomaly['score'], 3),
            'texture_score': round(texture_anomaly['score'], 3),
            'defect_score': round(defect_anomaly['score'], 3),
            'brightness_mean': round(float(np.mean(gray)), 2),
            'brightness_std': round(float(np.std(gray)), 2),
        }
        
        return {
            'is_anomaly': is_anomaly,
            'anomaly_score': round(max_score, 3),
            'anomaly_type': anomaly_type,
            'confidence': round(confidence, 3),
            'details': details
        }
    
    def _detect_brightness_anomaly(self, gray: np.ndarray) -> Dict:
        """
        Detect brightness-related anomalies.
        
        Args:
            gray: Grayscale image
            
        Returns:
            Dictionary with score and details
        """
        # Calculate histogram
        hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
        hist = hist.flatten() / hist.sum()  # Normalize
        
        # Calculate mean brightness
        mean_brightness = np.mean(gray)
        
        # Ideal brightness is around 127.5
        brightness_deviation = abs(mean_brightness - 127.5) / 127.5
        
        # Check for extreme brightness values
        too_dark = mean_brightness < 60
        too_bright = mean_brightness > 195
        
        # Calculate anomaly score
        if too_dark or too_bright:
            score = min(1.0, brightness_deviation * 2)
        else:
            score = brightness_deviation * 0.5
        
        return {
            'score': score,
            'mean': mean_brightness,
            'deviation': brightness_deviation
        }
    
    def _detect_noise_anomaly(self, gray: np.ndarray) -> Dict:
        """
        Detect noise-related anomalies.
        
        Args:
            gray: Grayscale image
            
        Returns:
            Dictionary with score and details
        """
        # Apply median blur to get "denoised" version
        denoised = cv2.medianBlur(gray, 5)
        
        # Calculate difference (noise estimate)
        noise = cv2.absdiff(gray, denoised)
        noise_level = np.mean(noise)
        
        # High noise level indicates anomaly
        # Typical noise level: 0-10 (low), 10-20 (medium), >20 (high)
        if noise_level > 20:
            score = min(1.0, noise_level / 30)
        else:
            score = noise_level / 40
        
        return {
            'score': score,
            'noise_level': noise_level
        }
    
    def _detect_texture_anomaly(self, gray: np.ndarray) -> Dict:
        """
        Detect texture-related anomalies using Laplacian variance.
        
        Args:
            gray: Grayscale image
            
        Returns:
            Dictionary with score and details
        """
        # Calculate Laplacian (edge detection)
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        variance = laplacian.var()
        
        # Low variance indicates blurry/texture issues
        # High variance is generally good (sharp image)
        # Typical variance: <100 (blurry), 100-500 (normal), >500 (sharp/noisy)
        
        if variance < 50:
            # Very blurry - anomaly
            score = 0.8
        elif variance < 100:
            # Slightly blurry
            score = 0.4
        elif variance > 1000:
            # Too much texture/noise
            score = 0.6
        else:
            # Normal texture
            score = 0.1
        
        return {
            'score': score,
            'variance': variance
        }
    
    def _detect_defect_anomaly(self, gray: np.ndarray) -> Dict:
        """
        Detect defect-like anomalies using contour analysis.
        
        Args:
            gray: Grayscale image
            
        Returns:
            Dictionary with score and details
        """
        # Apply threshold to find anomalous regions
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Adaptive threshold to find local anomalies
        thresh = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV, 11, 2
        )
        
        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Count significant contours
        significant_contours = [c for c in contours if cv2.contourArea(c) > 50]
        defect_count = len(significant_contours)
        
        # Calculate total defect area
        total_area = sum(cv2.contourArea(c) for c in significant_contours)
        image_area = gray.shape[0] * gray.shape[1]
        defect_ratio = total_area / image_area
        
        # Score based on defect count and area
        score = min(1.0, defect_count / 20 + defect_ratio * 10)
        
        return {
            'score': score,
            'defect_count': defect_count,
            'defect_ratio': defect_ratio
        }


def create_demo_detector() -> AnomalyDetector:
    """
    Create a demo anomaly detector.
    
    Returns:
        Initialized AnomalyDetector
    """
    return AnomalyDetector()
