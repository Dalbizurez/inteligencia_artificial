import cv2
import numpy as np
from typing import Optional, List

class ImageController:
    
    def __init__(self, model, filter_manager):
        self._model = model
        self._filter_manager = filter_manager
        self._view = None
        self._rotation_angle = 0
        self._selection_mode = None
        self._selection_x = 50
        self._selection_y = 50
        self._selection_size = 20
        self._selection_color = [0, 0, 0]
    
    def set_view(self, view):
        self._view = view
    
    def load_image(self, path: str) -> bool:
        success = self._model.load_image(path)
        if success:
            self._rotation_angle = 0
            self._apply_filters_and_update()
        return success
    
    def _apply_filters_and_update(self):
        if not self._model.has_image():
            return
            
        original = self._model.get_original_image()
        filtered = self._filter_manager.apply_all(original)
        
        if self._rotation_angle != 0:
            filtered = self._rotate_image(filtered, self._rotation_angle)
        
        if self._selection_mode:
            filtered = self._apply_selection(filtered)
        
        self._model.update_current_image(filtered)
    
    def _rotate_image(self, image: np.ndarray, angle: float) -> np.ndarray:
        height, width = image.shape[:2]
        
        angle_normalized = angle % 360
        
        if abs(angle_normalized - 90) < 0.1:
            rotated = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
        elif abs(angle_normalized - 180) < 0.1:
            rotated = cv2.rotate(image, cv2.ROTATE_180)
        elif abs(angle_normalized - 270) < 0.1:
            rotated = cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
        else:
            center = (width // 2, height // 2)
            rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
            
            cos = abs(rotation_matrix[0, 0])
            sin = abs(rotation_matrix[0, 1])
            
            new_width = int((height * sin) + (width * cos))
            new_height = int((height * cos) + (width * sin))
            
            rotation_matrix[0, 2] += (new_width / 2) - center[0]
            rotation_matrix[1, 2] += (new_height / 2) - center[1]
            
            rotated = cv2.warpAffine(image, rotation_matrix, (new_width, new_height), 
                                    borderMode=cv2.BORDER_CONSTANT, 
                                    borderValue=(0, 0, 0),
                                    flags=cv2.INTER_LINEAR)
        
        return rotated
    
    def _apply_selection(self, image: np.ndarray) -> np.ndarray:
        result = image.astype(np.int16)
        height, width = image.shape[:2]
        
        x = int(self._selection_x * width / 100)
        y = int(self._selection_y * height / 100)
        size = int(self._selection_size * min(width, height) / 100)
        
        if self._selection_mode == 'cuadrado':
            x1 = max(0, x - size // 2)
            y1 = max(0, y - size // 2)
            x2 = min(width, x + size // 2)
            y2 = min(height, y + size // 2)
            
            if x1 < x2 and y1 < y2:
                for c in range(3):
                    result[y1:y2, x1:x2, c] += self._selection_color[c]
        
        elif self._selection_mode == 'circulo':
            center_x = x
            center_y = y
            radius = size // 2
            
            Y, X = np.ogrid[:height, :width]
            mask = (X - center_x) ** 2 + (Y - center_y) ** 2 <= radius ** 2
            
            for c in range(3):
                result[mask, c] += self._selection_color[c]
        
        return np.clip(result, 0, 255).astype(np.uint8)
    
    def apply_filters(self):
        self._apply_filters_and_update()
    
    def get_current_image(self):
        return self._model.get_current_image()
    
    def flip_horizontal(self):
        current = self._model.get_current_image()
        if current is not None:
            flipped = cv2.flip(current, 1)
            self._model.update_current_image(flipped)
    
    def flip_vertical(self):
        current = self._model.get_current_image()
        if current is not None:
            flipped = cv2.flip(current, 0)
            self._model.update_current_image(flipped)
    
    def rotate(self, delta_angle: float):
        self._rotation_angle = (self._rotation_angle + delta_angle) % 360
        self._apply_filters_and_update()
    
    def set_rotation_angle(self, angle: float):
        self._rotation_angle = angle % 360
        self._apply_filters_and_update()
    
    def reset_rotation(self):
        self._rotation_angle = 0
        self._apply_filters_and_update()
    
    def reset_filters(self):
        self._filter_manager.reset_all()
        self._rotation_angle = 0
        self._selection_mode = None
        self._selection_color = [0, 0, 0]
        self._apply_filters_and_update()
    
    def get_rotation_angle(self) -> float:
        return self._rotation_angle
    
    def set_selection_mode(self, mode):
        self._selection_mode = mode
        self._apply_filters_and_update()
    
    def set_selection_position(self, x: int, y: int):
        self._selection_x = x
        self._selection_y = y
        self._apply_filters_and_update()
    
    def set_selection_size(self, size: int):
        self._selection_size = size
        self._apply_filters_and_update()
    
    def set_selection_color(self, r: int, g: int, b: int):
        self._selection_color = [b, g, r]
        self._apply_filters_and_update()
    
    def disable_selection(self):
        self._selection_mode = None
        self._apply_filters_and_update()