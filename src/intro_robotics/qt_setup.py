"""Small compatibility helper for the course's Qt-based 3D viewer."""

import os


def prepare_qt_environment():
    """Let PySide6 find its own Qt plugins after a GUI OpenCV import.

    Linux OpenCV wheels may set Qt 5 plugin/font paths. Those paths are not
    suitable for a PySide6 Qt 6 application. Preserve other user-supplied paths.
    """
    for name in ("QT_QPA_PLATFORM_PLUGIN_PATH", "QT_QPA_FONTDIR"):
        value = os.environ.get(name, "").replace("\\", "/")
        if "/cv2/qt/" in value:
            os.environ.pop(name, None)
