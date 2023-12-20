# -*- coding: utf-8 -*-

""" Base Widget defining widgets for AR_gui. """

import platform
import logging
import cv2
import numpy as np
from PySide6 import QtWidgets, QtCore
import sksurgeryimage.acquire.video_source as vs
import sksurgeryvtk.widgets.vtk_overlay_window as ow

#from src.AR_gui_rs_api_widget import RealsenseVideoSourceAPI

LOGGER = logging.getLogger(__name__)


class ARGuiBaseWidget(QtWidgets.QWidget):
    """
    AR_gui base widget. Responsible for managing 2 VTKOverlayWidget's.
    """

    def __init__(self, cl_args: dict):
        """
        ARGuiBaseWidget constructor.
        """
        LOGGER.info("Creating ARGuiBaseWidget")
        super(ARGuiBaseWidget, self).__init__()

        self.intrinsics = cl_args['intrinsics']
        self.distortion = cl_args['distortion']
        self.model_loader = cl_args['model_loader']
        self.video_source = cl_args['video_source']
        self.update_rate = cl_args['frame_rate']

        # whether to use realsense API or not for realsense viewer
        #self.rs_api = cl_args['realsense_api']

        print(
            f'video source {type(self.video_source)}, {self.video_source}'
        )

        if platform.system() == 'Linux':
            init_vtk_widget = False
        else:
            init_vtk_widget = True

        self.setContentsMargins(0, 0, 0, 0)

        self.video_viewer = ow.VTKOverlayWindow(init_widget=init_vtk_widget)
        self.video_viewer.setContentsMargins(0, 0, 0, 0)
        #self.endoscope_viewer = ow.VTKOverlayWindow(init_widget=init_vtk_widget)
        #self.endoscope_viewer.setContentsMargins(0, 0, 0, 0)
        self.layout = QtWidgets.QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.layout.addWidget(self.video_viewer)
        #self.layout.addWidget(self.endoscope_viewer)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_view)

        # Initialise models for both windows.

        # Either load all models in all windows?
        # self.realsense_viewer.add_vtk_models(self.model_loader.models)
        # self.endoscope_viewer.add_vtk_models(self.model_loader.models)

        # or maybe specific models in specific windows.
        for m in self.model_loader.models:
            
            self.video_viewer.add_vtk_models([m])

        # Setup file reading for videos.
        self.video = None
        if self.video_source:

            if self.video_source.isdigit():
                self.video_source = int(self.video_source)

            #if self.rs_api:
            #    self.video_realsense = RealsenseVideoSourceAPI()
            #else:
            self.video = vs.TimestampedVideoSource(
                    self.video_source)  # self.video_realsense_source

        else:
            raise RuntimeError(f"You haven't provided a video source.")

        LOGGER.info("Created ARGuiBaseWidget")

    def start(self):
        """
        Starts the timer, which repeatedly triggers the update_view() method.
        """
        self.timer.start(1000.0 / self.update_rate)

    def stop(self):
        """
        Stops the timer.
        """
        self.timer.stop()

    def terminate(self):
        """
        Make sure that the VTK Interactor terminates nicely, otherwise
        it can throw some error messages, depending on the usage.
        """
        self.video_viewer._RenderWindow.Finalize()  # pylint: disable=protected-access
        self.video_viewer.TerminateApp()

    def update_view(self):
        """
        Grabs video, then calls update_video which derived classes should implement.
        """
        im_undistorted = np.zeros((3, 3, 3), np.uint8)
        im_undistorted_grey = np.zeros((3, 3), np.uint8)

        ret, image = self.video.read()

        if ret:
            im_undistorted = cv2.undistort(image, self.intrinsics,
                                                  self.distortion)
            im_undistorted_grey = cv2.cvtColor(im_undistorted, cv2.COLOR_RGB2GRAY)
        else:
            LOGGER.error("Failed to read from source")


        if ret:
            self.update_video(im_undistorted,
                              im_undistorted_grey)

    def update_video(self, image_from_realsense, image_from_endoscope):
        """
        Derived classes should implement this method to update the screen.
        """
        raise NotImplementedError("Derived classes should implement 'update_video()'")
