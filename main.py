from converters.full_converter import full_convert
from converters.partial_converter import partial_convert

if __name__ == '__main__':
    partial_convert(
        video_name='Round Midnight',
        video_url='https://www.youtube.com/watch?v=9p2kKIoF2xo',
        tag=18,
        white_note_threshold=200,
        white_key_height=345,
        black_key_height=300,
        clear_frame_number=62,
        read_height=50,
        left_hand_color=[136, 168, 207],
        right_hand_color=[167, 223, 90],
        background_color=[50, 50, 50],
        note_gap_length=3,
        video_dir_path='./Round Midnight/',
        frame_dir_path='./Round Midnight/frames/',
        array_dir_path='./Round Midnight/arrays',
        csv_dir_path='./Round Midnight/csvs/',
        midi_dir_path='./Round Midnight/',
    )