import pytest
from tools.arg_detector import ARGDetector

def test_detector_init():
    detector = ARGDetector()
    assert detector.client is not None
