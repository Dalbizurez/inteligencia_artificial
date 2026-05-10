import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.image_model import ImageModel
from filters.filter_manager import FilterManager
from controllers.image_controller import ImageController
from views.main_view import MainView

def main():
    model = ImageModel()
    filter_manager = FilterManager()
    controller = ImageController(model, filter_manager)
    view = MainView(controller)
    
    model.attach(view)
    
    view.run()

if __name__ == "__main__":
    main()