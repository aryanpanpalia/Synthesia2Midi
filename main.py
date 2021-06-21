from converters.full_converter import full_convert
from converters.partial_converter import partial_convert

if __name__ == '__main__':
    full_convert(
        video_name='Ricky',
        video_url='https://www.youtube.com/watch?v=4w2icYjruEY',
        tag=18,
        first_note='A',
        read_height=50,
        first_white_note_col=5.5,
        tenth_white_note_col=116.3,
        left_hand_color=[85, 123, 222],
        right_hand_color=[255, 218, 225],
        background_color=[0, 0, 0],
        minimum_note_width=5
    )
