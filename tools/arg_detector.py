# Compatibility shim: re-export ARGDetector from src.tools.arg_detector
try:
    from src.tools.arg_detector import ARGDetector  # type: ignore
    __all__ = ["ARGDetector"]
except Exception:
    # In case src isn't importable in some environments, provide a clear error
    raise
