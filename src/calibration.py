import cv2
import numpy as np
import glob
import os
#from cv2 import aruco
from aruco_utils import create_aruco_board

def calibrate_camera_intrinsics_with_aruco_board(board):
    """
    Calibrates camera with an aruco borad

    params:
        - calib_imgs_path: path where calibration images stored
        - board: aruco GridBoard object (board = cv2.aruco.GridBoard((markers_w, markers_h), marker_length, marker_separation, aruco_dict))
    returns:
        - mtx: intrinsics calibration params of camera
        - dist: distortion calibration params of camera
    """

    # initialise aruco board params
    arucoParams = cv2.aruco.DetectorParameters()
    aruco_dict = board.getDictionary()

    # going through all images to find corners
    counter, corners_list, id_list = [], [], []
    first = True
    ids = 0

    cap = cv2.VideoCapture(0)
    # live calibration
    while True:
        # Capture frame-by-frame
        ret, im = cap.read()
        if not ret:
            continue

        # load img and change to gray
        #im = cv2.imread(str(fn))
        img_gray = cv2.cvtColor(im, cv2.COLOR_RGB2GRAY)

        # detect corners of aruco markers
        corners, ids, rejectedImgPoints = cv2.aruco.detectMarkers(img_gray, aruco_dict, parameters=arucoParams)
        if len(corners) == 0:  # if no corners detected go to next frame
            continue

        if first == True:
            corners_list = corners
            id_list = ids
            first = False
        else:
            # adding corners and ids of detected aruco markers to list
            corners_list = np.vstack((corners_list, corners))
            id_list = np.vstack((id_list, ids))
        counter.append(len(ids))

        # draw detected markers corners on frame
        im = cv2.aruco.drawDetectedMarkers(im, corners)

        cv2.imshow('frame', im)
        cv2.waitKey(1)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    print('Found {} unique markers'.format(np.unique(ids)))

    counter = np.array(counter)
    ret, mtx, dist, rvecs, tvecs = cv2.aruco.calibrateCameraAruco(corners_list, id_list, counter, board, img_gray.shape,
                                                              None, None)

    return mtx, dist


if __name__ == '__main__':
    board = create_aruco_board(
        aruco_dict_type=cv2.aruco.DICT_4X4_50,
        markers_w=5,  # Number of markers in the X direction.
        markers_h=7,  # Number of markers in the y direction.
        marker_length=16,  # length of aruco marker (mm)
        marker_separation=5  # separation between markers (mm)
    )
    calibrate_camera_intrinsics_with_aruco_board(board)