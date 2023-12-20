import os
import argparse
import numpy as np
import sksurgeryvtk.models.vtk_surface_model_directory_loader as vdl
from src.loading_config_utils import load_matrix, create_model_loader, load_AR_display_config, load_aruco_config
from src.main import run_ar_gui
import configparser


def create_AR_parser():
    """
    Creates the command line parser for AR_gui.
    :return: argparse.ArgumentParser()
    """
    parser = argparse.ArgumentParser(description='AR_gui')

    parser.add_argument('--config_path',
                        required=False,
                        type=str,
                        default='config/config.ini',
                        help='path to json file containing all the arguments. If this is not specified, you need to specify all the arguments in the command line.')

    parser.add_argument("-i", "--intrinsics",
                        required=False,
                        type=str,
                        help="Path to file containing camera intrinsic parameters (3x3).")

    parser.add_argument("-d", "--distortion",
                        required=False,
                        type=str,
                        help="Path to file containing distortion parameters (1x5).")

    parser.add_argument("-vr", "--video_source",
                        required=False,
                        type=str,
                        help="If provided, path to file containing video, or just OpenCV device id. e.g. 0")


    parser.add_argument("-r", "--registration",
                        required=False,
                        type=str,
                        help="Path to file containing (4x4) registration matrix to ArUco coord.")

    parser.add_argument("-m", "--models",
                        required=False,
                        type=str,
                        help="Path to directory containing models.")

    parser.add_argument("-rd", "--rendering_defaults",
                        required=False,
                        default="rendering_defaults.json",
                        type=str,
                        help="File name of .json file containing rendering parameters.")

    parser.add_argument("-fr", "--frame_rate",
                        required=False,
                        default=1,
                        type=int,
                        help="Approximate frame rate (fps).")

    return parser


def main(args=None):
    """
    Main function, parses args, exits early if error then launches GUI.
    """
    parser = create_AR_parser()
    parsed_args = parser.parse_args()

    # Command line parser will check for the presence/absence of required/optional
    # arguments. We will now do some basic loading and checking of inputs
    # here, and pass objects through to the main app, as there is no point creating
    # the actual GUI if the input data is invalid.

    # check if user submitted config file
    if len(parsed_args.config_path) > 0:
        config = configparser.ConfigParser()
        config.read(parsed_args.config_path)

        # load all the arguments from the config file
        intrinsics_pth, distortion_pth, video_source, registration_matrix, models, rendering_defaults, frame_rate = load_AR_display_config(
            config)
        # load aruco params
        aruco_dict, size_in_bits, border_bits, gap_between_markers_in_bits, \
            marker_length, markers_w, markers_h, pixels_per_bit, save_path, marker_separation, \
            pointer_marker_length, pointer_markers_w, pointer_markers_h, pointer_marker_separation, \
            pointer_aruco_dict, pointer_save_path \
                  = load_aruco_config(config)
        print('marker length: ', marker_length)
        print('markers w: ', markers_w)
        print('markers h: ', markers_h)
        print('marker separation: ', marker_separation)
        print('pointer marker length: ', pointer_marker_length)
        print('pointer markers w: ', pointer_markers_w)
        print('pointer markers h: ', pointer_markers_h)
        print('pointer marker separation: ', pointer_marker_separation)

    else:
        intrinsics_pth = parsed_args.intrinsics
        distortion_pth = parsed_args.distortion

        registration_matrix = parsed_args.registration
        models = parsed_args.models
        rendering_defaults = parsed_args.rendering_defaults

        video_source = parsed_args.video_realsense

        frame_rate = parsed_args.frame_rate


    cl_args = dict()
    cl_args['intrinsics'] = load_matrix(name="intrinsics",
                                                  path_to_file=intrinsics_pth,
                                                  expected_shape=(3, 3))

    cl_args['distortion'] = load_matrix(name="distortion",
                                                  path_to_file=distortion_pth,
                                                  expected_shape=(1, 5))

    cl_args['registration_matrix'] = load_matrix(name="registration_matrix",
                                                 path_to_file=registration_matrix,
                                                 expected_shape=(4, 4))

    cl_args['model_loader'] = create_model_loader(path_to_directory=models,
                                                  rendering_defaults=rendering_defaults)

    cl_args['video_source'] = video_source  # 0/1

    # aruco params
    cl_args['aruco_markers_w'] = markers_w
    cl_args['aruco_markers_h'] = markers_h
    cl_args['aruco_marker_length'] = marker_length
    cl_args['aruco_marker_separation'] = marker_separation


    cl_args['pointer_aruco_markers_w'] = pointer_markers_w
    cl_args['pointer_aruco_markers_h'] = pointer_markers_h
    cl_args['pointer_aruco_marker_length'] =pointer_marker_length
    cl_args['pointer_aruco_marker_separation'] = pointer_marker_separation

    cl_args['frame_rate'] = frame_rate


    run_ar_gui(cl_args)


if __name__ == '__main__':
    main()
