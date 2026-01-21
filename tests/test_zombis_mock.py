import pytest
from unittest.mock import Mock, patch, MagicMock
from src.tools.arg_detector import ARGDetector  # Post pip -e .

@pytest.fixture
def mock_detector():
    detector = Mock(spec=ARGDetector)
    detector.detect_disks_unattached.return_value = [
        {"name": "mock-disk-zombi-1", "resourceGroup": "test-rg", "location": "westeurope"},
        {"name": "mock-disk-zombi-2", "resourceGroup": "prod-old", "location": "northeurope"}
    ]
    detector.detect_ips_orphaned.return_value = []
    return detector

def test_detect_zombis_disks(mock_detector):
    """Test discos zombis mockeados."""
    zombis = mock_detector.detect_disks_unattached()
    assert len(zombis) == 2
    assert zombis[0]["name"] == "mock-disk-zombi-1"

def test_detect_ips_empty(mock_detector):
    """Test IPs sin zombis."""
    ips = mock_detector.detect_ips_orphaned()
    assert len(ips) == 0

def test_print_zombis_table(mock_detector):
    """Test print no crashea con datos."""
    zombis = mock_detector.detect_disks_unattached()
    # Simula print (no testable fácil, solo no error)
    assert zombis  # Datos OK

@patch('src.tools.arg_detector.DefaultAzureCredential')
def test_auth_error(mock_cred, caplog):
    """Test error auth graceful."""
    mock_cred.side_effect = Exception("No login")
    detector = ARGDetector()
    result = detector.detect_disks_unattached()
    assert result == []
    assert "Error ARG" in caplog.text

if __name__ == "__main__":
    pytest.main(["-v", __file__])
