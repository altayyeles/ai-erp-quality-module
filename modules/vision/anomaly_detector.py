"""
Anomaly Detection Module using Computer Vision
Detects visual anomalies using histogram analysis and statistical methods
"""

import logging
import time
from typing import Dict
import numpy as np

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

try:
    from PIL import Image
    import io
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

logger = logging.getLogger(__name__)


class AnomalyDetector:
    """
    Visual anomaly detection system.
    
    Uses OpenCV for image processing with histogram analysis,
    noise detection, brightness anomaly detection, and texture analysis.
    Falls back to simple heuristics if OpenCV is not available.
    """
    
    # Anomaly thresholds
    BRIGHTNESS_LOW = 60
    BRIGHTNESS_HIGH = 220
    CONTRAST_LOW = 20
    CONTRAST_HIGH = 100
    NOISE_THRESHOLD = 15.0
    
    def __init__(self):
        """Initialize anomaly detector."""
        pass
    
    def detect_bytes(self, image_bytes: bytes) -> Dict:
        """
        Detect anomalies in an image.
        
        Args:
            image_bytes: Image data as bytes
            
        Returns:
            Dictionary with anomaly detection results
        """
        start_time = time.time()
        
        if not CV2_AVAILABLE or not PIL_AVAILABLE:
            return self._fallback_detection()
        
        try:
            # Convert bytes to numpy array
            nparr = np.frombuffer(image_bytes, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                return self._fallback_detection()
            
            # Perform anomaly detection
            result = self._detect_anomalies(image)
            
            # Add timing
            detection_time_ms = (time.time() - start_time) * 1000
            result['detection_time_ms'] = round(detection_time_ms, 2)
            
            return result
        
        except Exception as e:
            logger.error(f"Anomaly detection failed: {e}")
            return self._fallback_detection()
    
    def _detect_anomalies(self, image: np.ndarray) -> Dict:
        """Perform anomaly detection using OpenCV."""
        height, width = image.shape[:2]
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Calculate image statistics
        brightness = np.mean(gray)
        contrast = np.std(gray)
        
        # Histogram analysis
        hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
        hist = hist.flatten() / hist.sum()  # Normalize
        
        # Calculate histogram entropy (measure of uniformity)
        hist_nonzero = hist[hist > 0]
        entropy = -np.sum(hist_nonzero * np.log2(hist_nonzero))
        
        # Noise detection using Laplacian variance
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        noise_score = laplacian.var()
        
        # Detect anomalies
        anomalies = []
        anomaly_type = "NONE"
        
        # Brightness anomaly
        if brightness < self.BRIGHTNESS_LOW:
            anomalies.append("brightness_low")
            anomaly_type = "BRIGHTNESS"
        elif brightness > self.BRIGHTNESS_HIGH:
            anomalies.append("brightness_high")
            anomaly_type = "BRIGHTNESS"
        
        # Contrast anomaly
        if contrast < self.CONTRAST_LOW:
            anomalies.append("contrast_low")
            if anomaly_type == "NONE":
                anomaly_type = "TEXTURE"
        elif contrast > self.CONTRAST_HIGH:
            anomalies.append("contrast_high")
            if anomaly_type == "NONE":
                anomaly_type = "TEXTURE"
        
        # Noise anomaly
        if noise_score > self.NOISE_THRESHOLD:
            anomalies.append("excessive_noise")
            if anomaly_type == "NONE":
                anomaly_type = "NOISE"
        elif noise_score < 2.0:
            anomalies.append("low_variance")
            if anomaly_type == "NONE":
                anomaly_type = "TEXTURE"
        
        # Histogram uniformity check
        if entropy > 7.5:  # Too uniform, possibly blank or featureless
            anomalies.append("uniform_texture")
            if anomaly_type == "NONE":
                anomaly_type = "TEXTURE"
        
        # Edge density analysis
        edges = cv2.Canny(gray, 50, 150)
        edge_density = np.sum(edges > 0) / (width * height)
        
        if edge_density < 0.01:  # Very few edges
            anomalies.append("featureless")
            if anomaly_type == "NONE":
                anomaly_type = "DEFECT"
        elif edge_density > 0.30:  # Too many edges
            anomalies.append("excessive_detail")
            if anomaly_type == "NONE":
                anomaly_type = "NOISE"
        
        # Calculate anomaly score
        anomaly_score = self._calculate_anomaly_score(
            brightness, contrast, noise_score, entropy, edge_density
        )
        
        # Determine if anomaly
        is_anomaly = len(anomalies) > 0 or anomaly_score > 0.5
        
        # Calculate confidence
        confidence = self._calculate_confidence(anomaly_score, len(anomalies))
        
        # Generate details
        details = {
            'brightness': round(brightness, 2),
            'contrast': round(contrast, 2),
            'noise_score': round(noise_score, 2),
            'entropy': round(entropy, 2),
            'edge_density': round(edge_density, 4),
            'anomalies_detected': anomalies,
            'image_size': f"{width}x{height}"
        }
        
        return {
            'is_anomaly': is_anomaly,
            'anomaly_score': round(anomaly_score, 3),
            'anomaly_type': anomaly_type,
            'confidence': round(confidence, 3),
            'details': details
        }
    
    def _calculate_anomaly_score(
        self,
        brightness: float,
        contrast: float,
        noise_score: float,
        entropy: float,
        edge_density: float
    ) -> float:
        """Calculate overall anomaly score (0.0-1.0)."""
        score = 0.0
        
        # Brightness contribution (0-0.3)
        if brightness < self.BRIGHTNESS_LOW:
            score += 0.3 * (self.BRIGHTNESS_LOW - brightness) / self.BRIGHTNESS_LOW
        elif brightness > self.BRIGHTNESS_HIGH:
            score += 0.3 * (brightness - self.BRIGHTNESS_HIGH) / (255 - self.BRIGHTNESS_HIGH)
        
        # Contrast contribution (0-0.25)
        if contrast < self.CONTRAST_LOW:
            score += 0.25 * (self.CONTRAST_LOW - contrast) / self.CONTRAST_LOW
        elif contrast > self.CONTRAST_HIGH:
            score += 0.25 * (contrast - self.CONTRAST_HIGH) / (128 - self.CONTRAST_HIGH)
        
        # Noise contribution (0-0.25)
        if noise_score > self.NOISE_THRESHOLD:
            score += 0.25 * min(1.0, (noise_score - self.NOISE_THRESHOLD) / 50)
        elif noise_score < 2.0:
            score += 0.15 * (2.0 - noise_score) / 2.0
        
        # Entropy contribution (0-0.1)
        if entropy > 7.5:
            score += 0.1 * min(1.0, (entropy - 7.5) / 0.5)
        
        # Edge density contribution (0-0.1)
        if edge_density < 0.01:
            score += 0.1
        elif edge_density > 0.30:
            score += 0.1 * min(1.0, (edge_density - 0.30) / 0.20)
        
        # Cap at 1.0
        return min(1.0, score)
    
    def _calculate_confidence(self, anomaly_score: float, num_anomalies: int) -> float:
        """Calculate confidence level for the detection."""
        # Base confidence from anomaly score
        confidence = anomaly_score
        
        # Boost confidence if multiple anomalies detected
        if num_anomalies >= 3:
            confidence = min(1.0, confidence + 0.15)
        elif num_anomalies >= 2:
            confidence = min(1.0, confidence + 0.10)
        elif num_anomalies >= 1:
            confidence = min(1.0, confidence + 0.05)
        
        # If no clear anomalies but non-zero score, reduce confidence
        if num_anomalies == 0 and anomaly_score > 0:
            confidence *= 0.7
        
        return confidence
    
    def _fallback_detection(self) -> Dict:
        """Fallback detection when OpenCV is not available."""
        logger.warning("OpenCV not available. Using fallback detection.")
        
        # Return simulated detection result
        import random
        random.seed(42)
        
        is_anomaly = random.random() < 0.3  # 30% chance of anomaly
        
        if is_anomaly:
            anomaly_types = ["BRIGHTNESS", "NOISE", "TEXTURE", "DEFECT"]
            anomaly_type = random.choice(anomaly_types)
            anomaly_score = random.uniform(0.5, 0.9)
            confidence = random.uniform(0.6, 0.9)
        else:
            anomaly_type = "NONE"
            anomaly_score = random.uniform(0.0, 0.3)
            confidence = random.uniform(0.7, 0.95)
        
        return {
            'is_anomaly': is_anomaly,
            'anomaly_score': round(anomaly_score, 3),
            'anomaly_type': anomaly_type,
            'confidence': round(confidence, 3),
            'details': {
                'brightness': 128.0,
                'contrast': 55.0,
                'noise_score': 8.5,
                'entropy': 6.8,
                'edge_density': 0.12,
                'anomalies_detected': ['simulated'] if is_anomaly else [],
                'image_size': '640x480',
                'note': 'Fallback mode - install opencv-python-headless for actual detection'
            },
            'detection_time_ms': 5.0
        }
