from converters.full_converter import full_convert
from converters.partial_converter import partial_convert

if __name__ == '__main__':
    partial_convert(
        video_name='Ricky',
        video_url='https://www.youtube.com/watch?v=NHShFsBj0cs',
        tag=18,
        first_note='A',
        first_white_note_col=5.7,
        tenth_white_note_col=118.5,
        left_hand_color=[117, 172, 228],
        right_hand_color=[63, 195, 0],
        background_color=[0, 0, 0],
        minimum_note_width=5,
        read_height=50
    )
