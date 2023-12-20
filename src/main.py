# -*- coding: utf-8 -*-

"""
Entry point for AR_Gui.
"""
import sys
import logging
from PySide6.QtWidgets import QApplication

import src.AR_gui_window as agw
# from src.loading_config_utils import load_matrix, create_model_loader
# from cl_apps.cl_AR_display import main


LOGGER = logging.getLogger(__name__)


def run_ar_gui(cl_args):
    """
    First function to actually start the GUI.
    """
    LOGGER.info(f"Calling run_AR_gui.")

    # Check if already an instance of QApplication is present or not
    if not QApplication.instance():
        app = QApplication([])
    else:
        app = QApplication.instance()

    # app = QtWidgets.QApplication([])
    window = agw.ARGuiMainWindow(cl_args)
    window.show()
    window.start()
    return sys.exit(app.exec())


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    run_ar_gui()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
