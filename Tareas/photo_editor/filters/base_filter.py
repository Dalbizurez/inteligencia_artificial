from abc import ABC, abstractmethod
import numpy as np
from typing import Dict, Any

class ImageFilter(ABC):
    
    def __init__(self):
        self._enabled = True
        self._params = {}
    
    @abstractmethod
    def apply(self, image: np.ndarray) -> np.ndarray:
        pass
    
    @abstractmethod
    def get_control_widget(self, parent, callback) -> Any:
        pass
    
    def set_enabled(self, enabled: bool):
        self._enabled = enabled
    
    def is_enabled(self) -> bool:
        return self._enabled
    
    def update_params(self, **kwargs):
        self._params.update(kwargs)