# -*- coding: utf-8 -*-

""" Main Widget defining functionality for AR_gui. """
import logging
import cv2
import numpy as np
import src.AR_gui_base_widget as bw
#import sksurgeryvtk.utils.matrix_utils as mu
from sksurgerycalibration.video.video_calibration_utils import extrinsic_vecs_to_matrix
import sksurgeryvtk.utils.matrix_utils as mu

LOGGER = logging.getLogger(__name__)

from src.aruco_utils import create_aruco_board

"""
def create_aruco_board(aruco_dict_type=cv2.aruco.DICT_4X4_50,
                       markers_w=5,  # Number of markers in the X direction.
                       markers_h=7,  # Number of markers in the y direction.
                       marker_length=20,  # length of aruco marker (mm)
                       marker_separation=3  # separation between markers (mm)
                       ):

    aruco_dict = cv2.aruco.getPredefinedDictionary(aruco_dict_type)
    board = cv2.aruco.GridBoard((markers_w, markers_h), marker_length, marker_separation, aruco_dict)

    return board
"""


def guess_clipping_range_from_pose(pose_matrix):
    """
    The camera pose matrix should enable us to estimate the clipping range.
    """
    distance = np.linalg.norm(pose_matrix[0:3, 3])
    min_clip = 0.01
    max_clip = 5 * distance
    return min_clip, max_clip


class ARGuiMainWidget(bw.ARGuiBaseWidget):
    """
    AR_gui main widget. Responsible for most application logic.
    """

    def __init__(self, cl_args: dict):
        """
        ARGuiMainWidget constructor.
        """
        LOGGER.info("Creating ARGuiMainWidget")
        super(ARGuiMainWidget, self).__init__(cl_args)

        # Creating member variables from command line args passed in.
        # Note: frame_rate, model_loader and video sources are used in base class.
        self.registration_matrix = cl_args['registration_matrix']
        #self.calibration_matrix = cl_args['calibration_matrix']

        # The models (face, tumour etc) should be in MR space, so they need multiplying by registration.
        # self.registration_matrix_vtk = mu.create_vtk_matrix_from_numpy(self.registration_matrix)
        # for m in self.model_loader.models:
        #    m.set_model_transform(self.registration_matrix_vtk)

        # initialising aruco board for tracking
        self.aruco_board = create_aruco_board(
            aruco_dict_type=cv2.aruco.DICT_4X4_50,
            markers_w=cl_args['aruco_markers_w'],  # Number of markers in the X direction.
            markers_h=cl_args['aruco_markers_h'],  # Number of markers in the y direction.
            marker_length=cl_args['aruco_marker_length'],  # length of aruco marker (mm)
            marker_separation=cl_args['aruco_marker_separation']  # separation between markers (mm)
        )

        self.pointer_aruco_board = create_aruco_board(
            aruco_dict_type=cv2.aruco.DICT_5X5_50,
            markers_w=cl_args['pointer_aruco_markers_w'],  # Number of markers in the X direction.
            markers_h=cl_args['pointer_aruco_markers_h'],  # Number of markers in the y direction.
            marker_length=cl_args['pointer_aruco_marker_length'],  # length of aruco marker (mm)
            marker_separation=cl_args['pointer_aruco_marker_separation']  # separation between markers (mm)
        )

        self.aruco_dict = self.aruco_board.getDictionary()
        self.pointer_aruco_dict = self.pointer_aruco_board.getDictionary()
        self.aruco_params = cv2.aruco.DetectorParameters()

        LOGGER.info("Created ARGuiMainWidget")

    def detect_aruco_board_pose(self, undistorted_image, undistorted_grey_image, intrinsics, aruco_board, aruco_dict):
        """
        Detects aruco board pose from single image frame.
        """
        is_success = False
        image = undistorted_image
        pose = np.eye(4)

        corners, ids, rejected_img_points = cv2.aruco.detectMarkers(undistorted_grey_image,
                                                                    aruco_dict,
                                                                    parameters=self.aruco_params)

        if corners:
            ret, rvec, tvec = cv2.aruco.estimatePoseBoard(corners, ids,
                                                          aruco_board, intrinsics,
                                                          None, None, None)

            if ret:
                pose = extrinsic_vecs_to_matrix(rvec, tvec)
                image = cv2.aruco.drawDetectedMarkers(undistorted_image, corners)
                image = cv2.drawFrameAxes(image, intrinsics, None, rvec, tvec, length=37)
                is_success = True

        return is_success, image, pose

    def update_video(self,
                     img_undistorted,
                     img_undistorted_grey):
        """
        Called by update_view in base class.
        """
        pose_ok, annotated_image, pose = self.detect_aruco_board_pose(img_undistorted,
                                                                                img_undistorted_grey,
                                                                                self.intrinsics, 
                                                                                self.aruco_board,
                                                                                self.aruco_dict)
        
        pointer_pose_ok, annotated_image, pose_pointer = self.detect_aruco_board_pose(annotated_image,
                                                                                img_undistorted_grey,
                                                                                self.intrinsics, 
                                                                                self.pointer_aruco_board, 
                                                                                self.pointer_aruco_dict)
        # First set video images.
        if pose_ok:
            self.video_viewer.set_video_image(annotated_image)
        else:
            self.video_viewer.set_video_image(img_undistorted)

        # Then sort out cameras. Slight code duplication, but easier to read.
        # So, currently, if tracking not ok, then overlays stop updating.
        if pose_ok:
            # ArUco pose is aruco_board (world) to camera.
            # The VTKOverlayWindow expects camera to world.
            # So, we have to invert the pose.

            camera_to_world = np.linalg.inv(pose @ self.registration_matrix)
            world_to_pointer = pose_pointer @ np.linalg.inv(camera_to_world)
            # hand_T_aruco = pose

            self.video_viewer.set_camera_matrix(self.intrinsics)
            self.video_viewer.set_camera_pose(camera_to_world)

            world_mtx_vtk = mu.create_vtk_matrix_from_numpy(np.linalg.inv(pose))
            pointer_mtx_vtk = mu.create_vtk_matrix_from_numpy(world_to_pointer)
            for m in self.model_loader.models:
                if m.get_name() in ['pointer', 'weiss']:
                    print('found model')
                    m.set_model_transform(pointer_mtx_vtk)
                #else:
                    #m.set_user_matrix(world_mtx_vtk)
                        
            min_clip, max_clip = guess_clipping_range_from_pose(world_to_pointer)
            self.video_viewer.get_foreground_camera().SetClippingRange(min_clip, max_clip)
        self.video_viewer.Render()
