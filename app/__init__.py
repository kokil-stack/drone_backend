"""
Intelligent Drone Mining & Digital Mine Platform Backend.
UAV remote sensing, high-precision LiDAR (6cm deviation), volume acceptance.
"""

from app.core.config import settings
from app.main import app

__version__ = settings.VERSION

__all__ = ["app", "settings", "__version__"]
