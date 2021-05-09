import concurrent.futures
import os
import sys

import numpy as np
from tqdm import tqdm

from frame2notes import Frame2Notes
from pixel2note import Pixel2Note


def process_frame(f2n, f_dir, f_num, lkn):
    notes = f2n.get(f_dir + f"/frame_{f_num}.jpg")
    lr = [1 if i in notes[0] else 0 for i in range(lkn)]
    rr = [1 if i in notes[1] else 0 for i in range(lkn)]
    return lr, rr


def get_matrix(frame_dir, clear_frame, black_key_height, white_key_height, read_height,
               left_hand_color, right_hand_color, note_gap_length=3):
    """
    :param frame_dir: the directory the frames are in
    :param clear_frame: a frame that has no notes colored/pressed/obstructed
    :param black_key_height: height of black keys
    :param white_key_height: height where no black keys
    :param read_height: the height from which to read notes
    :param left_hand_color: the color of the notes in the left hand
    :param right_hand_color: the color of the notes in the right hand
    :param note_gap_length: max gap between white notes
    :return: array which row 0 is time 0 and row n is time n. column 0 is first note and column n is note n
    """

    p2n_object = Pixel2Note(f"{frame_dir}/{clear_frame}", black_key_height, white_key_height, note_gap_length)

    p2n_dict = p2n_object.get_pixel_to_note()
    f2n = Frame2Notes(p2n_object, read_height, left_hand_color, right_hand_color)

    number_of_frames = len([name for name in os.listdir(frame_dir) if os.path.isfile(os.path.join(frame_dir, name))])
    last_key_number = list(p2n_dict.values())[-1]

    left_hand = []
    right_hand = []

    # TODO change it so that the matrix time isn't in terms of frames but in seconds so that partial frames can be used

    with concurrent.futures.ProcessPoolExecutor() as executor:
        frames = range(number_of_frames)
        length = len(frames)
        results = list(
            tqdm(
                executor.map(process_frame, [f2n] * length, [frame_dir] * length, frames, [last_key_number] * length),
                total=len(frames),
                file=sys.stdout,
                desc="Frames Processed"
            )
        )

        for result in results:
            left_hand.append(result[0])
            right_hand.append(result[1])

    left_hand = np.array(left_hand).reshape((number_of_frames, last_key_number))  # should be seconds by last key number
    right_hand = np.array(right_hand).reshape((number_of_frames, last_key_number))

    def to_intervals(array):
        in_intervals = []

        for column_index in range(array.shape[1]):
            col = array[:, column_index]
            new = []
            count = 1

            for i in range(1, col.shape[0]):
                if col[i] == col[i - 1]:
                    count += 1
                    if i == col.shape[0] - 1:  # if on the last element of column. have to record now.
                        new.append([col[i], count])
                else:
                    new.append([col[i - 1], count])
                    count = 1

            in_intervals.append(new)

        return in_intervals

    def to_abs(array):
        in_abs = []

        for note in array:
            new = []
            time_count = 0
            for occurrence in note:
                new.append([occurrence[0], time_count])
                time_count += occurrence[1]
            in_abs.append(new)

        return in_abs

    return to_abs(to_intervals(left_hand)), to_abs(to_intervals(right_hand))