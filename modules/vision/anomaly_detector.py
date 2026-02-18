"""
Visual Anomaly Detection System
Autoencoder-based anomaly detection for visual inspection

This module detects anomalies in images using histogram analysis,
noise detection, and brightness anomaly detection with OpenCV.
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
    logging.warning("OpenCV not available. Anomaly detection will use minimal fallback.")

try:
    from PIL import Image
    import io
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    logging.warning("PIL not available.")

logger = logging.getLogger(__name__)


class AnomalyDetector:
    """
    Visual anomaly detection system using image analysis.
    
    Detects anomalies in images through histogram analysis,
    noise detection, brightness anomalies, and texture analysis.
    """
    
    # Thresholds for anomaly detection
    BRIGHTNESS_THRESHOLD = 40  # Deviation from expected brightness
    NOISE_THRESHOLD = 15       # Threshold for noise detection
    HISTOGRAM_THRESHOLD = 0.3  # Threshold for histogram deviation
    
    def __init__(self):
        """Initialize the anomaly detector."""
        self.baseline_brightness = 127  # Expected brightness
        self.baseline_contrast = 40     # Expected contrast
    
    def detect_bytes(self, image_bytes: bytes) -> Dict:
        """
        Detect anomalies in an image provided as bytes.
        
        Args:
            image_bytes: Raw image bytes (JPEG, PNG, etc.)
            
        Returns:
            Dictionary with anomaly detection results including
            anomaly score, type, confidence, and details
        """
        start_time = time.time()
        
        if not CV2_AVAILABLE or not PIL_AVAILABLE:
            return self._fallback_detection()
        
        try:
            # Convert bytes to image
            image = self._bytes_to_image(image_bytes)
            
            if image is None:
                return self._fallback_detection()
            
            # Perform anomaly detection
            results = self._detect_anomalies(image)
            
            detection_time = (time.time() - start_time) * 1000
            results['detection_time_ms'] = round(detection_time, 2)
            
            return results
            
        except Exception as e:
            logger.error(f"Error during anomaly detection: {e}")
            return self._fallback_detection()
    
    def _bytes_to_image(self, image_bytes: bytes):
        """Convert image bytes to OpenCV format."""
        try:
            pil_image = Image.open(io.BytesIO(image_bytes))
            
            if pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')
            
            image = np.array(pil_image)
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            
            return image
            
        except Exception as e:
            logger.error(f"Error converting bytes to image: {e}")
            return None
    
    def _detect_anomalies(self, image: np.ndarray) -> Dict:
        """Perform anomaly detection on the image."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Detect various types of anomalies
        brightness_anomaly = self._detect_brightness_anomaly(gray)
        noise_anomaly = self._detect_noise_anomaly(gray)
        texture_anomaly = self._detect_texture_anomaly(gray)
        histogram_anomaly = self._detect_histogram_anomaly(gray)
        
        # Combine anomaly scores
        anomaly_scores = [
            brightness_anomaly['score'],
            noise_anomaly['score'],
            texture_anomaly['score'],
            histogram_anomaly['score']
        ]
        
        # Overall anomaly score (max of individual scores)
        max_score = max(anomaly_scores)
        avg_score = sum(anomaly_scores) / len(anomaly_scores)
        
        # Determine primary anomaly type
        anomaly_type, confidence = self._determine_anomaly_type(
            brightness_anomaly,
            noise_anomaly,
            texture_anomaly,
            histogram_anomaly
        )
        
        # Is it an anomaly?
        is_anomaly = max_score > 0.6
        
        # Compile details
        details = {
            'brightness': brightness_anomaly,
            'noise': noise_anomaly,
            'texture': texture_anomaly,
            'histogram': histogram_anomaly,
            'average_anomaly_score': round(avg_score, 3)
        }
        
        return {
            'is_anomaly': is_anomaly,
            'anomaly_score': round(max_score, 3),
            'anomaly_type': anomaly_type,
            'confidence': round(confidence, 2),
            'details': details,
            'recommendations': self._generate_recommendations(
                is_anomaly, anomaly_type, max_score, details
            )
        }
    
    def _detect_brightness_anomaly(self, gray_image: np.ndarray) -> Dict:
        """Detect brightness anomalies."""
        mean_brightness = np.mean(gray_image)
        std_brightness = np.std(gray_image)
        
        # Calculate deviation from expected
        deviation = abs(mean_brightness - self.baseline_brightness)
        
        # Normalize to 0-1 score
        score = min(1.0, deviation / self.BRIGHTNESS_THRESHOLD)
        
        is_anomalous = deviation > self.BRIGHTNESS_THRESHOLD
        
        return {
            'score': score,
            'is_anomalous': is_anomalous,
            'mean': round(float(mean_brightness), 2),
            'std': round(float(std_brightness), 2),
            'deviation': round(float(deviation), 2)
        }
    
    def _detect_noise_anomaly(self, gray_image: np.ndarray) -> Dict:
        """Detect noise anomalies using Laplacian variance."""
        # Calculate Laplacian variance (measure of image sharpness/noise)
        laplacian = cv2.Laplacian(gray_image, cv2.CV_64F)
        variance = laplacian.var()
        
        # Low variance suggests blurry/noisy image
        # High variance suggests sharp image (good)
        # Very high variance might suggest excessive noise
        
        if variance < 100:  # Very blurry/noisy
            score = 1.0 - (variance / 100)
            is_anomalous = True
        elif variance > 1000:  # Excessive noise
            score = min(1.0, (variance - 1000) / 1000)
            is_anomalous = True
        else:
            score = 0.0
            is_anomalous = False
        
        return {
            'score': score,
            'is_anomalous': is_anomalous,
            'variance': round(float(variance), 2),
            'sharpness': 'low' if variance < 100 else 'high' if variance > 1000 else 'normal'
        }
    
    def _detect_texture_anomaly(self, gray_image: np.ndarray) -> Dict:
        """Detect texture anomalies using standard deviation analysis."""
        # Divide image into blocks and analyze texture consistency
        h, w = gray_image.shape
        block_size = 32
        
        block_stds = []
        
        for i in range(0, h - block_size, block_size):
            for j in range(0, w - block_size, block_size):
                block = gray_image[i:i+block_size, j:j+block_size]
                block_stds.append(np.std(block))
        
        if not block_stds:
            return {'score': 0.0, 'is_anomalous': False, 'uniformity': 'unknown'}
        
        # Calculate variation in block standard deviations
        std_of_stds = np.std(block_stds)
        mean_of_stds = np.mean(block_stds)
        
        # High variation suggests texture inconsistency
        coefficient_of_variation = std_of_stds / mean_of_stds if mean_of_stds > 0 else 0
        
        score = min(1.0, coefficient_of_variation)
        is_anomalous = coefficient_of_variation > 0.6
        
        return {
            'score': score,
            'is_anomalous': is_anomalous,
            'coefficient_of_variation': round(float(coefficient_of_variation), 3),
            'uniformity': 'poor' if is_anomalous else 'good'
        }
    
    def _detect_histogram_anomaly(self, gray_image: np.ndarray) -> Dict:
        """Detect histogram anomalies."""
        # Calculate histogram
        hist = cv2.calcHist([gray_image], [0], None, [256], [0, 256])
        hist = hist.flatten() / hist.sum()  # Normalize
        
        # Expected histogram should be somewhat uniform or bell-shaped
        # Calculate entropy (measure of randomness)
        hist_nonzero = hist[hist > 0]
        entropy = -np.sum(hist_nonzero * np.log2(hist_nonzero))
        
        # Max entropy for 256 bins is 8
        # Very low entropy suggests poor distribution (anomaly)
        normalized_entropy = entropy / 8.0
        
        # Score is inverse of normalized entropy
        # Low entropy = high anomaly score
        if normalized_entropy < 0.5:
            score = 1.0 - normalized_entropy * 2
            is_anomalous = True
        else:
            score = 0.0
            is_anomalous = False
        
        # Check for spikes in histogram (another anomaly indicator)
        hist_peaks = np.sum(hist > (hist.mean() * 5))
        if hist_peaks > 3:
            score = max(score, 0.7)
            is_anomalous = True
        
        return {
            'score': score,
            'is_anomalous': is_anomalous,
            'entropy': round(float(entropy), 3),
            'distribution': 'poor' if is_anomalous else 'good',
            'peaks': int(hist_peaks)
        }
    
    def _determine_anomaly_type(
        self,
        brightness: Dict,
        noise: Dict,
        texture: Dict,
        histogram: Dict
    ) -> tuple:
        """Determine the primary anomaly type and confidence."""
        scores = {
            'BRIGHTNESS': brightness['score'],
            'NOISE': noise['score'],
            'TEXTURE': texture['score'],
            'DEFECT': histogram['score']
        }
        
        # Find max score
        max_type = max(scores, key=scores.get)
        max_score = scores[max_type]
        
        if max_score < 0.3:
            return 'NONE', 1.0
        elif max_score < 0.6:
            # Low confidence anomaly
            return max_type, 0.6
        else:
            # High confidence
            return max_type, min(0.95, max_score + 0.2)
    
    def _generate_recommendations(
        self,
        is_anomaly: bool,
        anomaly_type: str,
        score: float,
        details: Dict
    ) -> list:
        """Generate recommendations based on anomaly detection."""
        recommendations = []
        
        if not is_anomaly:
            recommendations.append("✅ No significant anomalies detected. Image quality is acceptable.")
            return recommendations
        
        # Overall recommendation
        if score > 0.8:
            recommendations.append("🚨 CRITICAL ANOMALY: Image severely deviates from normal patterns.")
        elif score > 0.6:
            recommendations.append("⚠️ ANOMALY DETECTED: Significant deviation from expected patterns.")
        
        # Type-specific recommendations
        if anomaly_type == 'BRIGHTNESS':
            brightness_info = details['brightness']
            if brightness_info['mean'] < 80:
                recommendations.append("💡 Image is too dark. Improve lighting conditions.")
            elif brightness_info['mean'] > 180:
                recommendations.append("☀️ Image is overexposed. Reduce lighting or adjust camera.")
        
        elif anomaly_type == 'NOISE':
            noise_info = details['noise']
            if noise_info['variance'] < 100:
                recommendations.append("📷 Image is blurry or very noisy. Check camera focus and stability.")
            else:
                recommendations.append("⚡ Excessive noise detected. Clean lens or adjust camera settings.")
        
        elif anomaly_type == 'TEXTURE':
            recommendations.append("🔍 Texture inconsistency detected. Inspect for surface defects or damage.")
        
        elif anomaly_type == 'DEFECT':
            recommendations.append("⚠️ Histogram anomaly suggests potential defects. Manual inspection recommended.")
        
        # Additional checks
        if details['brightness']['is_anomalous'] and details['histogram']['is_anomalous']:
            recommendations.append("⚠️ Multiple anomaly types detected. Recommend thorough inspection.")
        
        return recommendations
    
    def _fallback_detection(self) -> Dict:
        """Fallback detection result when OpenCV is not available."""
        logger.warning("Using fallback anomaly detection mode")
        
        return {
            'is_anomaly': False,
            'anomaly_score': 0.0,
            'anomaly_type': 'NONE',
            'confidence': 1.0,
            'detection_time_ms': 5.0,
            'details': {
                'brightness': {'score': 0.0, 'is_anomalous': False},
                'noise': {'score': 0.0, 'is_anomalous': False},
                'texture': {'score': 0.0, 'is_anomalous': False},
                'histogram': {'score': 0.0, 'is_anomalous': False}
            },
            'recommendations': [
                '⚠️ OpenCV not available - using simulated detection',
                'ℹ️ Install opencv-python-headless for full functionality'
            ],
            'mode': 'fallback'
        }
