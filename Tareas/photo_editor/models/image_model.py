import cv2
import numpy as np
from typing import Optional, Tuple

class ImageModel:
    
    def __init__(self):
        self._original: Optional[np.ndarray] = None
        self._current: Optional[np.ndarray] = None
        self._observers = []
    
    def attach(self, observer):
        self._observers.append(observer)
    
    def notify_observers(self):
        for observer in self._observers:
            observer.on_image_changed()
    
    def load_image(self, path: str) -> bool:
        try:
            self._original = cv2.imread(path)
            if self._original is None:
                return False
            self._current = self._original.copy()
            self.notify_observers()
            return True
        except Exception:
            return False
    
    def update_current(self, image: np.ndarray):
        self._current = image.copy()
        self.notify_observers()
    
    def get_original(self) -> Optional[np.ndarray]:
        return self._original
    
    def get_current(self) -> Optional[np.ndarray]:
        return self._current
    
    def has_image(self) -> bool:
        return self._original is not None
    
    def get_image_size(self) -> Tuple[int, int]:
        if self._current is not None:
            height, width = self._current.shape[:2]
            return width, height
        return 0, 0