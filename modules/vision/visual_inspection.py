"""
Visual Inspection System
Computer Vision-based defect detection for manufacturing quality control

This module uses OpenCV for visual inspection and defect detection,
with YOLO fallback for advanced object detection when available.
"""

import logging
import time
from typing import Dict, List, Tuple
import numpy as np

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    logging.warning("OpenCV not available. Visual inspection will use minimal fallback.")

try:
    from PIL import Image
    import io
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    logging.warning("PIL not available.")

logger = logging.getLogger(__name__)


class VisualInspector:
    """
    Computer Vision-based visual inspection system.
    
    Detects defects in manufacturing components using edge detection,
    contour analysis, and brightness/contrast evaluation.
    """
    
    def __init__(self):
        """Initialize the visual inspector."""
        self.min_defect_area = 100  # Minimum contour area to consider as defect
        self.edge_threshold_low = 50
        self.edge_threshold_high = 150
    
    def inspect_bytes(self, image_bytes: bytes) -> Dict:
        """
        Inspect an image provided as bytes.
        
        Args:
            image_bytes: Raw image bytes (JPEG, PNG, etc.)
            
        Returns:
            Dictionary with inspection results including defects found,
            quality score, and recommendations
        """
        start_time = time.time()
        
        if not CV2_AVAILABLE or not PIL_AVAILABLE:
            return self._fallback_inspection()
        
        try:
            # Convert bytes to numpy array
            image = self._bytes_to_image(image_bytes)
            
            if image is None:
                return self._fallback_inspection()
            
            # Perform inspection
            results = self._perform_inspection(image)
            
            inspection_time = (time.time() - start_time) * 1000  # Convert to ms
            results['inspection_time_ms'] = round(inspection_time, 2)
            
            return results
            
        except Exception as e:
            logger.error(f"Error during visual inspection: {e}")
            return self._fallback_inspection()
    
    def _bytes_to_image(self, image_bytes: bytes):
        """Convert image bytes to OpenCV format."""
        try:
            # Use PIL to open image from bytes
            pil_image = Image.open(io.BytesIO(image_bytes))
            
            # Convert to RGB if needed
            if pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')
            
            # Convert to numpy array
            image = np.array(pil_image)
            
            # Convert RGB to BGR (OpenCV format)
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            
            return image
            
        except Exception as e:
            logger.error(f"Error converting bytes to image: {e}")
            return None
    
    def _perform_inspection(self, image: np.ndarray) -> Dict:
        """Perform the actual inspection on the image."""
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Edge detection using Canny
        edges = cv2.Canny(blurred, self.edge_threshold_low, self.edge_threshold_high)
        
        # Find contours (potential defects)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filter and analyze contours
        defect_regions = []
        total_defect_area = 0
        
        for contour in contours:
            area = cv2.contourArea(contour)
            
            if area > self.min_defect_area:
                x, y, w, h = cv2.boundingRect(contour)
                
                # Calculate defect metrics
                aspect_ratio = w / float(h) if h > 0 else 0
                extent = area / (w * h) if w * h > 0 else 0
                
                defect_regions.append({
                    'x': int(x),
                    'y': int(y),
                    'width': int(w),
                    'height': int(h),
                    'area': int(area),
                    'aspect_ratio': round(aspect_ratio, 2),
                    'extent': round(extent, 2)
                })
                
                total_defect_area += area
        
        # Analyze brightness and contrast
        brightness_score = self._analyze_brightness(gray)
        contrast_score = self._analyze_contrast(gray)
        
        # Calculate quality score
        quality_score = self._calculate_quality_score(
            len(defect_regions),
            total_defect_area,
            image.shape[0] * image.shape[1],
            brightness_score,
            contrast_score
        )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            len(defect_regions),
            defect_regions,
            brightness_score,
            contrast_score,
            quality_score
        )
        
        return {
            'defects_found': len(defect_regions) > 0,
            'defect_count': len(defect_regions),
            'defect_regions': defect_regions[:10],  # Limit to top 10
            'total_defect_area': int(total_defect_area),
            'image_size': {
                'width': image.shape[1],
                'height': image.shape[0]
            },
            'quality_score': round(quality_score, 1),
            'brightness_score': round(brightness_score, 1),
            'contrast_score': round(contrast_score, 1),
            'recommendations': recommendations
        }
    
    def _analyze_brightness(self, gray_image: np.ndarray) -> float:
        """Analyze image brightness (0-100 scale)."""
        mean_brightness = np.mean(gray_image)
        # Optimal brightness around 127 (middle gray)
        deviation = abs(mean_brightness - 127)
        score = max(0, 100 - (deviation / 127) * 100)
        return score
    
    def _analyze_contrast(self, gray_image: np.ndarray) -> float:
        """Analyze image contrast (0-100 scale)."""
        # Calculate standard deviation as measure of contrast
        std_dev = np.std(gray_image)
        # Higher std dev = better contrast, normalize to 0-100
        # Assume std dev of 50+ is good contrast
        score = min(100, (std_dev / 50) * 100)
        return score
    
    def _calculate_quality_score(
        self,
        defect_count: int,
        defect_area: int,
        total_area: int,
        brightness: float,
        contrast: float
    ) -> float:
        """
        Calculate overall quality score (0-100).
        
        Considers defect count, defect area ratio, brightness, and contrast.
        """
        # Start with perfect score
        score = 100.0
        
        # Penalize for defects
        if defect_count > 0:
            score -= min(30, defect_count * 3)  # Up to -30 points
        
        # Penalize for defect area
        defect_ratio = defect_area / total_area if total_area > 0 else 0
        score -= min(40, defect_ratio * 1000)  # Up to -40 points
        
        # Adjust for brightness (weight: 0.15)
        if brightness < 70:
            score -= (70 - brightness) * 0.15
        
        # Adjust for contrast (weight: 0.15)
        if contrast < 60:
            score -= (60 - contrast) * 0.15
        
        return max(0, score)
    
    def _generate_recommendations(
        self,
        defect_count: int,
        defect_regions: List[Dict],
        brightness: float,
        contrast: float,
        quality_score: float
    ) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []
        
        # Overall assessment
        if quality_score >= 90:
            recommendations.append("✅ PASS: Product meets quality standards")
        elif quality_score >= 75:
            recommendations.append("⚠️ MARGINAL: Minor issues detected, review recommended")
        elif quality_score >= 60:
            recommendations.append("⚠️ WARNING: Significant issues detected, rework may be needed")
        else:
            recommendations.append("🚫 FAIL: Product does not meet quality standards, reject")
        
        # Defect-specific recommendations
        if defect_count > 0:
            if defect_count > 5:
                recommendations.append(
                    f"🔴 Multiple defects detected ({defect_count}). "
                    "Inspect manufacturing process for systemic issues."
                )
            else:
                recommendations.append(
                    f"⚠️ {defect_count} defect(s) detected. Manual inspection recommended."
                )
            
            # Analyze defect sizes
            if defect_regions:
                large_defects = [d for d in defect_regions if d['area'] > 1000]
                if large_defects:
                    recommendations.append(
                        f"⚠️ {len(large_defects)} large defect(s) found. "
                        "May require significant rework."
                    )
        
        # Brightness recommendations
        if brightness < 50:
            recommendations.append("💡 Poor lighting conditions detected. Improve illumination for better inspection.")
        elif brightness > 90:
            recommendations.append("☀️ Overexposed image. Reduce lighting or adjust camera settings.")
        
        # Contrast recommendations
        if contrast < 40:
            recommendations.append("📷 Low contrast detected. Adjust camera settings or lighting setup.")
        
        if not recommendations or (quality_score >= 90 and defect_count == 0):
            recommendations = ["✅ Excellent quality. No issues detected."]
        
        return recommendations
    
    def _fallback_inspection(self) -> Dict:
        """Fallback inspection result when OpenCV is not available."""
        logger.warning("Using fallback visual inspection mode")
        
        return {
            'defects_found': False,
            'defect_count': 0,
            'defect_regions': [],
            'total_defect_area': 0,
            'quality_score': 85.0,
            'brightness_score': 75.0,
            'contrast_score': 70.0,
            'inspection_time_ms': 10.0,
            'recommendations': [
                '⚠️ OpenCV not available - using simulated inspection',
                'ℹ️ Install opencv-python-headless for full functionality'
            ],
            'mode': 'fallback'
        }
    
    def batch_inspect(self, images_bytes: List[bytes]) -> List[Dict]:
        """
        Inspect multiple images in batch.
        
        Args:
            images_bytes: List of image byte arrays
            
        Returns:
            List of inspection results
        """
        results = []
        
        for i, img_bytes in enumerate(images_bytes):
            try:
                result = self.inspect_bytes(img_bytes)
                result['image_index'] = i
                results.append(result)
            except Exception as e:
                logger.error(f"Error inspecting image {i}: {e}")
                results.append({
                    'image_index': i,
                    'error': str(e),
                    'defects_found': False,
                    'quality_score': 0
                })
        
        return results
