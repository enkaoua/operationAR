# -*- coding: utf-8 -*-

""" Main Window containing the main widget for the AR_gui. """

import logging
from PySide6 import QtWidgets
import src.AR_gui_main_widget as mw


LOGGER = logging.getLogger(__name__)


class ARGuiMainWindow(QtWidgets.QMainWindow):
    """
    AR_gui main window. Responsible for creating ARGuiMainWidget.py.

    I've used a QtWidgets.QMainWindow, as it provides other features that
    we may need later, eg. status bar.
    """
    def __init__(self, cl_args: dict):
        """
        MainWindow constructor.
        """
        LOGGER.info("Creating ARGuiMainWindow.")
        super().__init__()

        self.main_widget = mw.ARGuiMainWidget(cl_args)
        self.setCentralWidget(self.main_widget)
        self.setContentsMargins(0, 0, 0, 0)

        LOGGER.info("Created ARGuiMainWindow.")

    def start(self):
        """
        Starts the internal timer in ARGuiMainWidget.
        """
        self.main_widget.start()

