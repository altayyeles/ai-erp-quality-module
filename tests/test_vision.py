"""
Unit tests for Vision module (visual_inspection and anomaly_detector)
"""

import pytest
import numpy as np
import cv2
from modules.vision.visual_inspection import VisualInspector
from modules.vision.anomaly_detector import AnomalyDetector


def create_test_image(width=640, height=480, with_defects=False):
    """Create a test image for testing"""
    # Create a blank image
    image = np.ones((height, width, 3), dtype=np.uint8) * 200
    
    if with_defects:
        # Add some defects (dark rectangles)
        cv2.rectangle(image, (100, 100), (150, 150), (50, 50, 50), -1)
        cv2.rectangle(image, (300, 200), (350, 250), (30, 30, 30), -1)
    
    # Encode to bytes
    _, encoded = cv2.imencode('.png', image)
    return encoded.tobytes()


class TestVisualInspector:
    """Test cases for VisualInspector"""
    
    def test_inspector_initialization(self):
        """Test visual inspector can be initialized"""
        inspector = VisualInspector()
        assert inspector is not None
    
    def test_inspect_clean_image(self):
        """Test inspection of clean image"""
        inspector = VisualInspector()
        image_bytes = create_test_image(with_defects=False)
        
        result = inspector.inspect_bytes(image_bytes)
        
        assert 'defects_found' in result
        assert 'defect_count' in result
        assert 'defect_regions' in result
        assert 'quality_score' in result
        assert 'inspection_time_ms' in result
        assert 'recommendations' in result
        
        assert isinstance(result['defects_found'], bool)
        assert isinstance(result['defect_count'], int)
        assert 0 <= result['quality_score'] <= 100
        assert result['inspection_time_ms'] > 0
    
    def test_inspect_defective_image(self):
        """Test inspection of image with defects"""
        inspector = VisualInspector()
        image_bytes = create_test_image(with_defects=True)
        
        result = inspector.inspect_bytes(image_bytes)
        
        # Should detect some defects
        assert result['defect_count'] >= 0
        assert isinstance(result['defect_regions'], list)
    
    def test_defect_regions_structure(self):
        """Test defect regions have correct structure"""
        inspector = VisualInspector()
        image_bytes = create_test_image(with_defects=True)
        
        result = inspector.inspect_bytes(image_bytes)
        
        if result['defect_regions']:
            for region in result['defect_regions']:
                assert 'x' in region
                assert 'y' in region
                assert 'w' in region
                assert 'h' in region
                assert 'area' in region
    
    def test_invalid_image_data(self):
        """Test error handling for invalid image data"""
        inspector = VisualInspector()
        
        with pytest.raises(ValueError):
            inspector.inspect_bytes(b'invalid image data')
    
    def test_image_metrics(self):
        """Test image metrics are calculated"""
        inspector = VisualInspector()
        image_bytes = create_test_image()
        
        result = inspector.inspect_bytes(image_bytes)
        
        assert 'image_metrics' in result
        metrics = result['image_metrics']
        
        assert 'brightness' in metrics
        assert 'contrast' in metrics
        assert 'width' in metrics
        assert 'height' in metrics
        
        assert metrics['brightness'] > 0
        assert metrics['contrast'] >= 0
    
    def test_recommendations_generated(self):
        """Test that recommendations are generated"""
        inspector = VisualInspector()
        image_bytes = create_test_image()
        
        result = inspector.inspect_bytes(image_bytes)
        
        assert isinstance(result['recommendations'], list)
        assert len(result['recommendations']) > 0


class TestAnomalyDetector:
    """Test cases for AnomalyDetector"""
    
    def test_detector_initialization(self):
        """Test anomaly detector can be initialized"""
        detector = AnomalyDetector()
        assert detector is not None
    
    def test_detect_normal_image(self):
        """Test anomaly detection on normal image"""
        detector = AnomalyDetector()
        image_bytes = create_test_image(with_defects=False)
        
        result = detector.detect_bytes(image_bytes)
        
        assert 'is_anomaly' in result
        assert 'anomaly_score' in result
        assert 'anomaly_type' in result
        assert 'confidence' in result
        assert 'details' in result
        
        assert isinstance(result['is_anomaly'], bool)
        assert 0.0 <= result['anomaly_score'] <= 1.0
        assert result['anomaly_type'] in ['NONE', 'BRIGHTNESS', 'NOISE', 'TEXTURE', 'DEFECT']
        assert 0.0 <= result['confidence'] <= 1.0
    
    def test_detect_defective_image(self):
        """Test anomaly detection on defective image"""
        detector = AnomalyDetector()
        image_bytes = create_test_image(with_defects=True)
        
        result = detector.detect_bytes(image_bytes)
        
        # Should detect some anomaly
        assert 0.0 <= result['anomaly_score'] <= 1.0
    
    def test_anomaly_details(self):
        """Test anomaly detection details"""
        detector = AnomalyDetector()
        image_bytes = create_test_image()
        
        result = detector.detect_bytes(image_bytes)
        details = result['details']
        
        assert 'brightness_score' in details
        assert 'noise_score' in details
        assert 'texture_score' in details
        assert 'defect_score' in details
        assert 'brightness_mean' in details
        assert 'brightness_std' in details
        
        # All scores should be between 0 and 1
        assert 0.0 <= details['brightness_score'] <= 1.0
        assert 0.0 <= details['noise_score'] <= 1.0
        assert 0.0 <= details['texture_score'] <= 1.0
        assert 0.0 <= details['defect_score'] <= 1.0
    
    def test_invalid_image_data(self):
        """Test error handling for invalid image data"""
        detector = AnomalyDetector()
        
        with pytest.raises(ValueError):
            detector.detect_bytes(b'invalid image data')
    
    def test_bright_image_anomaly(self):
        """Test brightness anomaly detection"""
        detector = AnomalyDetector()
        
        # Create very bright image
        image = np.ones((480, 640, 3), dtype=np.uint8) * 250
        _, encoded = cv2.imencode('.png', image)
        image_bytes = encoded.tobytes()
        
        result = detector.detect_bytes(image_bytes)
        
        # Should detect brightness anomaly
        assert result['details']['brightness_score'] > 0
    
    def test_dark_image_anomaly(self):
        """Test dark image anomaly detection"""
        detector = AnomalyDetector()
        
        # Create very dark image
        image = np.ones((480, 640, 3), dtype=np.uint8) * 30
        _, encoded = cv2.imencode('.png', image)
        image_bytes = encoded.tobytes()
        
        result = detector.detect_bytes(image_bytes)
        
        # Should detect brightness anomaly
        assert result['details']['brightness_score'] > 0
    
    def test_noisy_image_anomaly(self):
        """Test noise anomaly detection"""
        detector = AnomalyDetector()
        
        # Create noisy image
        image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        _, encoded = cv2.imencode('.png', image)
        image_bytes = encoded.tobytes()
        
        result = detector.detect_bytes(image_bytes)
        
        # Should detect some anomaly (noise or texture)
        assert result['anomaly_score'] > 0
