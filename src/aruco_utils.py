import glob
import cv2
from cv2 import aruco
import numpy as np
from pathlib import Path
import copy
import os


def annotate_board(image, corners, color_lines=(0, 255, 0), color_circles=(0, 255, 0)):
    corner = corners.reshape((4, 2))
    (bottomLeft, topLeft, topRight, bottomRight) = corner

    topRight = (int(topRight[0]), int(topRight[1]))
    bottomRight = (int(bottomRight[0]), int(bottomRight[1]))
    bottomLeft = (int(bottomLeft[0]), int(bottomLeft[1]))
    topLeft = (int(topLeft[0]), int(topLeft[1]))

    cv2.line(image, topLeft, topRight, color_lines, 2)
    cv2.line(image, topRight, bottomRight, color_lines, 2)
    cv2.line(image, bottomRight, bottomLeft, color_lines, 2)
    cv2.line(image, bottomLeft, topLeft, color_lines, 2)

    # centre of marker
    cX = int((topLeft[0] + bottomRight[0]) / 2.0)
    cY = int((topLeft[1] + bottomRight[1]) / 2.0)
    cv2.circle(image, (cX, cY), 2, color_circles, -1)
    # bottom left corner
    cv2.circle(image, bottomLeft, 4, (0, 0, 255), -1)

    cv2.putText(image, str(bottomLeft), (bottomLeft[0], bottomLeft[1] - 10), cv2.FONT_HERSHEY_SIMPLEX,
                0.5, color_lines, 2)
    # print("[Inference] ArUco marker ID: {}".format(markerID))
    return image, bottomLeft


def generate_aruco_board_for_printing(aruco_dict=cv2.aruco.DICT_4X4_50,
                                      size_in_bits=4,
                                      border_bits=1,
                                      gap_between_markers_in_bits=2,
                                      marker_length=30,
                                      markers_w=5,
                                      markers_h=8,
                                      pixels_per_bit=10,
                                      save_path=f'{Path(__file__).parent.resolve()}/data/aruco_boards/aruco_board.png'

                                      ):
    """ Function that generates aruco markers

    this function will generate an aruco board with the given parameters. The board will be saved in
    the main directory and can be printed after correct size is specified with gimp. The size is printed
    when running the function.

    Args:
        aruco_dict: aruco dictionary that will be used (eg. aruco.DICT_4X4_50)
        size_in_bits: The size_in_bits variable must match the size of dictionary, i.e. DICT_4X4_50.
        border_bits: The black border surrounded by the aruco marker. Eg. if it is 1 and the aruco itself is
                     4x4, then the aruco will now be 6x6 as the black border goes all around the marker.
        gap_between_markers_in_bits: This will be the white gap (in bits) between consecutive aruco markers.
        marker_length: length of each marker in mm
        markers_w: number of aruco markers along the width of the grid
        markers_h: number of aruco markers along the height of the grid
        pixels_per_bit: number of pixels per bit. This will be used to convert bits to pixels for drawing.
        save_path: path where aruco board will be saved


    Returns:
        saves image of aruco board under current project path
    """

    # size of marker in bits- where bits refers to the pixel-like shape of the aruco.
    # Each aruco will be composed of the size_in_bits (which is dependent on the dictionary used)
    # plus the number of bits in the border specified. This border is the black border around the marker.
    # For example, if we use the 50 4x4 dict, each marker's size is 4 bits, and if we specify the
    # border_bit to 1, the size in bits will be 6 as there will be a border on each side of the marker.
    size_of_marker_in_bits = size_in_bits + (2 * border_bits)

    # gap between consecutive markers
    gap_ratio = float(gap_between_markers_in_bits) / float(size_of_marker_in_bits)

    # This gives the physical units.
    # So when you calibrate, you have the same units.
    marker_separation = (int)(marker_length * gap_ratio)

    # load aruco dictionary to be used for board
    aruco_dict = cv2.aruco.getPredefinedDictionary(aruco_dict)  # dictionary of markers provided
    # Create an aruco Board (The ids in ascending order starting on 0)
    grid_board = cv2.aruco.GridBoard((markers_w, markers_h),
                                     marker_length,
                                     marker_separation,
                                     aruco_dict)

    # width will be the number of markers*length plus whatever separation there is between each marker.
    # note that the separation is only within the grid so the last separation isn't counted
    width_millimetres = (markers_w * marker_length) + ((markers_w - 1) * marker_separation)
    # the same applies to the height
    height_millimetres = (markers_h * marker_length) + ((markers_h - 1) * marker_separation)

    # measuring width and height of img in pixels
    width_pixels = pixels_per_bit * (
            (markers_w * size_of_marker_in_bits) + ((markers_w - 1) * gap_between_markers_in_bits))
    height_pixels = pixels_per_bit * (
            (markers_h * size_of_marker_in_bits) + ((markers_h - 1) * gap_between_markers_in_bits))
    img_size = (width_pixels, height_pixels)

    # generating image from board for printing
    img = grid_board.generateImage(img_size,  # outSize size of the output image in pixels.
                                   marginSize=0,  # minimum margins (in pixels) of the board in the output image
                                   borderBits=border_bits  # borderBits width of the marker borders.
                                   )

    ## create directory if save_path dir doesnt exist
    save_path = Path(save_path)
    save_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"Load image into GIMP. Image size={width_pixels} x {height_pixels} pixels.")
    print(f"Set image size to: {width_millimetres} x {height_millimetres} millimetres")
    cv2.imwrite(f"{save_path}", img)
    print(save_path)


def create_aruco_board(aruco_dict_type=cv2.aruco.DICT_4X4_50,  # aruco dictionary type
                       markers_w=5,  # Number of markers in the X direction.
                       markers_h=7,  # Number of markers in the y direction.
                       marker_length=20,  # length of aruco marker (mm)
                       marker_separation=3  # separation between markers (mm)
                       ):
    '''
    Creates opencv aruco board object with given parameters

    params (all optional- default within square brackets):
        - aruco_dict_type (obj): aruco dictionary type, [cv2.aruco.DICT_4X4_50]
        - markers_w (int) : Number of markers in the X direction, [5]
        - markers_h (int): Number of markers in the y direction. [7]
        - marker_length (int): length of aruco marker (mm) [16]
        - marker_separation (int): separation between markers (mm) [5]
    '''

    # For validating results, show aruco board to camera.
    aruco_dict = cv2.aruco.getPredefinedDictionary(aruco_dict_type)  # aruco dictionary we will use

    # create arUco board
    board = cv2.aruco.GridBoard((markers_w, markers_h), marker_length, marker_separation, aruco_dict)

    return board


def detect_aruco_board_pose(img, intrinsics, distortion, board, return_corners=False, display_pose=False):
    """
    detects aruco board pose from single image frame and annotates image

    first parameter is a boolean: if pose detected it's set as true, if not it's set as false
    annotated_img: image with axis and aruco borders annotated on it
    rvec: rotation vector of board
    tvec: translation vector of baord
    """

    arucoParams = cv2.aruco.DetectorParameters()
    # get dictionary from board class
    aruco_dict = board.getDictionary()

    # im_gray = cv2.cvtColor(img,cv2.COLOR_RGB2GRAY)
    im_undistorted = cv2.undistort(img, intrinsics, distortion, None, intrinsics)
    # TODO check when to use im_undistorted and when to use gray (i just changed to gray and using dist)
    # detect corners of aruco markers
    corners, ids, rejectedImgPoints = aruco.detectMarkers(im_undistorted, aruco_dict, parameters=arucoParams)

    # if corners are detected, find aruco board pose and display detected aruco markers and axes of board
    if corners:
        ret, rvec, tvec = aruco.estimatePoseBoard(corners, ids, board, intrinsics, None, None, None)  # For a board

        # print ("Rotation ", rvec, "Translation", tvec)
        if ret:
            # draw detected markers corners on frame
            im_undistorted = cv2.aruco.drawDetectedMarkers(im_undistorted, corners)
            annotated_img = cv2.drawFrameAxes(im_undistorted, intrinsics, None, rvec, tvec, length=37)
            if display_pose:
                cv2.imshow('annotated pose', annotated_img)
                cv2.waitKey(1)
            if return_corners:
                return True, annotated_img, rvec, tvec, corners, ids
            return True, annotated_img, rvec, tvec  # , corners, ids

    return False, [], False, False

