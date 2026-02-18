"""
Visual Inspection Module

This module implements computer vision-based visual inspection using OpenCV
for defect detection and quality assessment.

Key Features:
- Edge detection and contour analysis
- Brightness and contrast analysis
- Defect region identification
- Quality scoring (0-100)
- Inspection time tracking
- Actionable recommendations
"""

import cv2
import numpy as np
import logging
import time
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class VisualInspector:
    """
    OpenCV-based visual inspection system.
    
    Analyzes images for defects using edge detection, contour analysis,
    and image quality metrics.
    """
    
    def __init__(self):
        """Initialize the visual inspector."""
        logger.info("VisualInspector initialized")
    
    def inspect_bytes(self, image_bytes: bytes) -> Dict:
        """
        Inspect an image for defects from raw bytes.
        
        Args:
            image_bytes: Raw image data as bytes
            
        Returns:
            Dictionary with inspection results including:
                - defects_found: Boolean indicating if defects detected
                - defect_count: Number of defects found
                - defect_regions: List of defect locations (x, y, w, h)
                - quality_score: Overall quality score (0-100)
                - inspection_time_ms: Time taken for inspection
                - recommendations: List of actionable recommendations
                
        Raises:
            ValueError: If image data is invalid
        """
        start_time = time.time()
        
        try:
            # Convert bytes to numpy array
            nparr = np.frombuffer(image_bytes, np.uint8)
            
            # Decode image
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                raise ValueError("Failed to decode image. Invalid image format.")
            
            logger.info(f"Inspecting image of shape: {image.shape}")
            
            # Perform inspection
            result = self._analyze_image(image)
            
            # Calculate inspection time
            inspection_time_ms = (time.time() - start_time) * 1000
            result['inspection_time_ms'] = round(inspection_time_ms, 2)
            
            logger.info(f"✓ Inspection complete: {result['defect_count']} defects, score: {result['quality_score']}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error during inspection: {e}")
            raise ValueError(f"Image inspection failed: {str(e)}")
    
    def _analyze_image(self, image: np.ndarray) -> Dict:
        """
        Analyze image for defects using OpenCV.
        
        Args:
            image: OpenCV image (BGR format)
            
        Returns:
            Dictionary with analysis results
        """
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Analyze brightness and contrast
        brightness = np.mean(gray)
        contrast = np.std(gray)
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Edge detection using Canny
        edges = cv2.Canny(blurred, 50, 150)
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filter significant contours (potential defects)
        defect_regions = []
        min_area = 100  # Minimum area to consider as defect
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > min_area:
                x, y, w, h = cv2.boundingRect(contour)
                defect_regions.append({
                    'x': int(x),
                    'y': int(y),
                    'w': int(w),
                    'h': int(h),
                    'area': int(area)
                })
        
        # Sort by area (largest first)
        defect_regions.sort(key=lambda r: r['area'], reverse=True)
        
        # Keep only top 10 largest defects
        defect_regions = defect_regions[:10]
        
        defect_count = len(defect_regions)
        defects_found = defect_count > 0
        
        # Calculate quality score
        quality_score = self._calculate_quality_score(
            defect_count, brightness, contrast, image.shape
        )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            defect_count, quality_score, brightness, contrast
        )
        
        return {
            'defects_found': defects_found,
            'defect_count': defect_count,
            'defect_regions': defect_regions,
            'quality_score': quality_score,
            'image_metrics': {
                'brightness': round(float(brightness), 2),
                'contrast': round(float(contrast), 2),
                'width': int(image.shape[1]),
                'height': int(image.shape[0])
            },
            'recommendations': recommendations
        }
    
    def _calculate_quality_score(
        self,
        defect_count: int,
        brightness: float,
        contrast: float,
        image_shape: tuple
    ) -> float:
        """
        Calculate overall quality score based on inspection results.
        
        Args:
            defect_count: Number of defects detected
            brightness: Average brightness
            contrast: Standard deviation (contrast measure)
            image_shape: Image dimensions
            
        Returns:
            Quality score (0-100)
        """
        # Start with perfect score
        score = 100.0
        
        # Penalize for defects (each defect reduces score)
        score -= defect_count * 5
        
        # Penalize for poor brightness (too dark or too bright)
        ideal_brightness = 127.5
        brightness_deviation = abs(brightness - ideal_brightness) / ideal_brightness
        score -= brightness_deviation * 20
        
        # Penalize for poor contrast (too low = blurry, too high = noisy)
        ideal_contrast = 50
        contrast_deviation = abs(contrast - ideal_contrast) / ideal_contrast
        score -= contrast_deviation * 15
        
        # Ensure score is in valid range
        score = max(0, min(100, score))
        
        return round(score, 2)
    
    def _generate_recommendations(
        self,
        defect_count: int,
        quality_score: float,
        brightness: float,
        contrast: float
    ) -> List[str]:
        """
        Generate actionable recommendations based on inspection results.
        
        Args:
            defect_count: Number of defects
            quality_score: Overall quality score
            brightness: Image brightness
            contrast: Image contrast
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        # Defect-based recommendations
        if defect_count == 0:
            recommendations.append("✓ No defects detected. Product passes visual inspection.")
        elif defect_count <= 2:
            recommendations.append("⚠️ Minor defects detected. Review defect regions for acceptance criteria.")
        elif defect_count <= 5:
            recommendations.append("⚠️ Multiple defects detected. Consider rework or detailed inspection.")
        else:
            recommendations.append("🚨 Significant defects detected. Reject product and investigate root cause.")
        
        # Brightness recommendations
        if brightness < 85:
            recommendations.append("💡 Image too dark. Improve lighting conditions for better inspection.")
        elif brightness > 170:
            recommendations.append("💡 Image too bright. Reduce lighting or adjust camera exposure.")
        
        # Contrast recommendations
        if contrast < 30:
            recommendations.append("📷 Low contrast detected. Check camera focus and lighting uniformity.")
        elif contrast > 70:
            recommendations.append("📷 High contrast detected. May indicate noise or uneven lighting.")
        
        # Overall quality recommendations
        if quality_score >= 90:
            recommendations.append("✓ Excellent visual quality. Approved for shipment.")
        elif quality_score >= 75:
            recommendations.append("✓ Good visual quality. Acceptable with minor observations.")
        elif quality_score >= 60:
            recommendations.append("⚠️ Marginal quality. Requires supervisor review.")
        else:
            recommendations.append("🚨 Poor quality. Reject and investigate production issues.")
        
        return recommendations


def create_demo_inspector() -> VisualInspector:
    """
    Create a demo visual inspector.
    
    Returns:
        Initialized VisualInspector
    """
    return VisualInspector()
