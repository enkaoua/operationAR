from data.aruco_dict_types import ARUCO_DICT
import numpy as np
import os
import numpy as np
import sksurgeryvtk.models.vtk_surface_model_directory_loader as vdl


def parse_int_tuple(input):
    return tuple(int(k.strip()) for k in input[1:-1].split(','))


def load_matrix(name: str,
                path_to_file: str,
                expected_shape: (int, int),
                is_mandatory: bool = True):
    """
    Loads a matrix and checks size.
    """
    matrix = np.loadtxt(path_to_file)
    exp_rows, exp_cols = expected_shape

    if matrix is None:
        raise ValueError(f"Could not find {name} matrix at: {path_to_file}")
    shape = matrix.shape
    if len(shape) > 1:
        if matrix.shape[0] != exp_rows:
            raise ValueError(f"{name} matrix at: {path_to_file}, doesn't have {exp_rows} rows.")
        if matrix.shape[1] != exp_cols:
            raise ValueError(f"{name} matrix at: {path_to_file}, doesn't have {exp_cols} columns.")
    else:
        matrix = matrix.reshape((exp_rows, exp_cols))

    if is_mandatory and matrix is None:
        raise ValueError(f"Failed to create matrix from {path_to_file}, and shape {expected_shape}.")

    return matrix


def create_model_loader(path_to_directory: str,
                        rendering_defaults: str,
                        is_mandatory: bool = True):
    """
    Loads models using sksurgeryvtk.models.vtk_surface_model_directory_loader,
    and returns the actual loader object containing all the models.
    """
    if path_to_directory is None or len(path_to_directory) == 0:
        raise ValueError(f"Invalid directory passed in:{path_to_directory}")
    if not os.path.isdir(path_to_directory):
        raise ValueError(f"Path {path_to_directory} is not a directory.")
    if rendering_defaults is None or len(rendering_defaults) == 0:
        raise ValueError(f"Invalid rendering defaults file given:{rendering_defaults}")

    defaults_file = os.path.join(path_to_directory, rendering_defaults)
    if not os.path.isfile(defaults_file):
        raise ValueError(f"The rendering defaults file:{defaults_file}, does not exist.")

    loader = vdl.VTKSurfaceModelDirectoryLoader(path_to_directory, defaults_file)

    if is_mandatory and loader is None:
        raise ValueError(f"Failed to create VTKSurfaceModelDirectoryLoader from {path_to_directory}, and {rendering_defaults}.")

    return loader


def load_aruco_config(config):
    section = config['ARUCO']  # extracting first section of ini file

    # extract args from config file section 'ARUCO'
    aruco_dict = ARUCO_DICT[section["aruco_dict"]]

    # aruco_dict = cv2.aruco.getPredefinedDictionary(aruco_dict_num)
    size_in_bits = int(section["size_in_bits"])
    border_bits = int(section["border_bits"])
    gap_between_markers_in_bits = int(section["gap_between_markers_in_bits"])
    marker_length = int(section["marker_length"])
    markers_w = int(section["markers_w"])
    markers_h = int(section["markers_h"])
    pixels_per_bit = int(section["pixels_per_bit"])
    save_path = section["save_path"]
    marker_separation = float(section["marker_separation"])

    pointer_present = bool(section["pointer_present"])
    if pointer_present:
        pointer_aruco_dict = ARUCO_DICT[section["pointer_aruco_dict"]]
        pointer_marker_length = int(section["pointer_marker_length"])
        pointer_markers_w = int(section["pointer_markers_w"])
        pointer_markers_h = int(section["pointer_markers_h"])
        pointer_marker_separation = float(section["pointer_marker_separation"])
        pointer_save_path = section["pointer_save_path"]

    return aruco_dict, size_in_bits, border_bits, gap_between_markers_in_bits, marker_length, markers_w, markers_h, pixels_per_bit, save_path, marker_separation, pointer_marker_length, pointer_markers_w, pointer_markers_h, pointer_marker_separation, pointer_aruco_dict, pointer_save_path



def load_AR_display_config(config):
    AR_section = config["AR_DISPLAY"]

    # Path to file containing camera intrinsic parameters (3x3)
    intrinsics_pth = AR_section["intrinsics_pth"]

    # Path to file containing cam distortion parameters (1x5).
    distortion_pth = AR_section["distortion_pth"]

    # If provided, path to file containing video from realsense camera, or just OpenCV device id. e.g. 0
    video_source = AR_section["video_source"]

    # Path to file containing (4x4) matrix of surface registration, MRI to ArUco.
    registration_matrix = AR_section["registration_matrix"]

    # Path to directory containing models.
    models = AR_section["models"]

    # File name of .json file containing rendering parameters.
    rendering_defaults = AR_section["rendering_defaults"]

    # rate at which video is read
    frame_rate = int(AR_section["frame_rate"])

    return intrinsics_pth, distortion_pth, video_source, registration_matrix, models, rendering_defaults, frame_rate
