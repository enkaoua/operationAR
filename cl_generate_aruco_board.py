
import argparse, configparser
from src.aruco_utils import generate_aruco_board_for_printing    
from data.aruco_dict_types import ARUCO_DICT
from src.loading_config_utils import load_aruco_config

def add_aruco_args_to_parser(parser):
    parser.add_argument('--config_path', 
                        required=False,
                        type=str, 
                        default='config/config.ini', 
                        help='path to json file containing all the arguments. If this is not specified, you need to specify all the arguments in the command line.')

    parser.add_argument('--aruco_dict', 
                        required=False,
                        type=str, 
                        default="DICT_4X4_50", 
                        help='dictionary of aruco board- full list of options can be seen in data/aruco_dict_types.py')
    parser.add_argument('--size_in_bits', 
                        required=False,
                        type=int, 
                        default=4, 
                        help='The size_in_bits variable must match the size of dictionary, i.e. DICT_4X4_50.')   
    parser.add_argument('--border_bits', 
                        required=False,
                        type=int, 
                        default=1, 
                        help='The black border surrounded by the aruco marker. Eg. if it is 1 and the aruco itself is 4x4, then the aruco will now be 6x6 as the black border goes all around the marker.')   
    parser.add_argument('--gap_between_markers_in_bits', 
                        required=False,
                        type=int, 
                        default=2, help=' This will be the white gap (in bits) between consecutive aruco markers.')
    parser.add_argument('--marker_length',
                        required=False, 
                        type=int, 
                        default=30, 
                        help='length of each marker in mm')    
    parser.add_argument('--markers_w', 
                        required=False,
                        type=int, 
                        default=5, 
                        help='number of aruco markers along the width of the grid')   
    parser.add_argument('--markers_h',
                        required=False, 
                        type=int, 
                        default=8, 
                        help='number of aruco markers along the height of the grid')  
    parser.add_argument('--pixels_per_bit', 
                        required=False,
                        type=int, 
                        default=10, 
                        help='number of pixels per bit. This will be used to convert bits to pixels for drawing.')    
    parser.add_argument('--save_path', 
                        required=False,
                        type=str, 
                        default='data/resources/aruco_boards/aruco_board.png', 
                        help='path where aruco board will be saved')    
    return parser


def main(): 
    parser = argparse.ArgumentParser(description='Generate Aruco board for printing')
    add_aruco_args_to_parser(parser)
    args = parser.parse_args()
    

    if len(args.config_path) > 0:
        config = configparser.ConfigParser()
        config.read(args.config_path)

        aruco_dict, size_in_bits, border_bits, gap_between_markers_in_bits, \
            marker_length, markers_w, markers_h, pixels_per_bit, save_path, marker_separation, \
            pointer_marker_length, pointer_markers_w, pointer_markers_h, pointer_marker_separation, \
            pointer_aruco_dict, pointer_save_path \
                  = load_aruco_config(config)
    else:
        aruco_dict = ARUCO_DICT[args.aruco_dict]
        size_in_bits = int(args.size_in_bits)
        border_bits = int(args.border_bits)
        gap_between_markers_in_bits = int(args.gap_between_markers_in_bits)
        marker_length = int(args.marker_length)
        markers_w = int(args.markers_w)
        markers_h = int(args.markers_h)
        pixels_per_bit = int(args.pixels_per_bit)
        save_path = args.save_path

    generate_aruco_board_for_printing(
        aruco_dict=aruco_dict,
        size_in_bits=size_in_bits,
        border_bits=border_bits,
        gap_between_markers_in_bits=gap_between_markers_in_bits,
        marker_length=marker_length,
        markers_w=markers_w,
        markers_h=markers_h,
        pixels_per_bit=pixels_per_bit,
        save_path=save_path
    )

    generate_aruco_board_for_printing(
        aruco_dict=pointer_aruco_dict,
        size_in_bits=size_in_bits,
        border_bits=border_bits,
        gap_between_markers_in_bits=gap_between_markers_in_bits,
        marker_length=pointer_marker_length,
        markers_w=pointer_markers_w,
        markers_h=pointer_markers_h,
        pixels_per_bit=pixels_per_bit,
        save_path=pointer_save_path
    )
    
    return 


if __name__=='__main__':
    main() 