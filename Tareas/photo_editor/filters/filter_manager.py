import numpy as np
from typing import List
from .base_filter import ImageFilter

class FilterManager:
    
    def __init__(self):
        self._filters: List[ImageFilter] = []
    
    def add_filter(self, filter_obj: ImageFilter):
        self._filters.append(filter_obj)
    
    def apply_all(self, image: np.ndarray) -> np.ndarray:
        if image is None:
            return None
            
        result = image.copy()
        for filter_obj in self._filters:
            result = filter_obj.apply(result)
        return result
    
    def get_filters(self) -> List[ImageFilter]:
        return self._filters
    
    def reset_all(self):
        for filter_obj in self._filters:
            if hasattr(filter_obj, 'reset'):
                filter_obj.reset()