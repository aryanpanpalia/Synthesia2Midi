import concurrent.futures
import os
import sys

import cv2
import numpy as np
from tqdm import tqdm


class Frames2MatrixConverter:
    def __init__(self, frame_dir, clear_frame, black_key_height, white_key_height, read_height,
                 left_hand_color, right_hand_color, white_note_threshold,
                 background_color=[33, 33, 33], note_gap_length=3):
        """
        :param frame_dir: the directory the frames are in
        :param clear_frame: a frame that has no notes colored/pressed/obstructed
        :param black_key_height: height of black keys
        :param white_key_height: height where no black keys
        :param read_height: the height from which to read notes
        :param left_hand_color: the color of the notes in the left hand
        :param right_hand_color: the color of the notes in the right hand
        :param white_note_threshold: the minimum pixel brightness that should correspond to a white note
        :param background_color: background color
        :param note_gap_length: maximum gap between white notes accounted for. If the gap is too large, notes can be
                                skipped as they are perceived as being a note gap instead of an actual note. If the gap
                                is too small, it will think of some note gaps as actual notes.
        """

        self.white_note_threshold = white_note_threshold
        self.frame_dir = frame_dir
        self.clear_frame = cv2.imread(clear_frame, cv2.IMREAD_GRAYSCALE)
        self.black_key_height = black_key_height
        self.white_key_height = white_key_height
        self.read_height = read_height
        self.note_gap_length = note_gap_length

        self.number_of_frames = len([name for name in os.listdir(frame_dir) if os.path.isfile(f'{frame_dir}/{name}')])

        self.left_hand_color = np.array(left_hand_color, dtype=np.uint8).reshape((1, 1, 3))
        self.right_hand_color = np.array(right_hand_color, dtype=np.uint8).reshape((1, 1, 3))
        self.background_color = np.array(background_color, dtype=np.uint8).reshape((1, 1, 3))

        self.left_hand_color_lab = cv2.cvtColor(self.left_hand_color, cv2.COLOR_RGB2LAB).reshape((3,)).astype('int32')
        self.right_hand_color_lab = cv2.cvtColor(self.right_hand_color, cv2.COLOR_RGB2LAB).reshape((3,)).astype('int32')
        self.background_color_lab = cv2.cvtColor(self.background_color, cv2.COLOR_RGB2LAB).reshape((3,)).astype('int32')

        self.pixel2note = self.create_pixel_to_note()
        self.last_key_number = list(self.pixel2note.values())[-1]

    def create_pixel_to_note(self):
        """
        creates a dictionary that maps the middle of all the keys to what note number they are
        :return: a dictionary that maps the middle of all the keys to what note number they are
        """

        def is_white(color):
            return color > self.white_note_threshold

        black_note_row = self.clear_frame[self.black_key_height:self.black_key_height + 1, :]
        black_note_row = np.array(
            [255 if is_white(black_note_row[0, i]) else 0 for i in range(black_note_row.shape[1])]
        )

        pixel_to_note = {}

        on_note = 0
        note_start = 0

        # only records black notes
        for i in range(black_note_row.shape[0]):
            last_note = black_note_row[i - 1]
            this_note = black_note_row[i]

            if np.abs(this_note - last_note) > 0:
                if i - note_start < self.note_gap_length:
                    note_start = i + 1
                else:
                    mid = ((note_start + i - 1) / 2)

                    # if its black, the color at the mid value will be black
                    if black_note_row[int(mid)] == 0:
                        pixel_to_note[mid] = on_note

                    # will increment note whether or not the last note was black
                    note_start = i + 1
                    on_note += 1

        white_note_row = self.clear_frame[self.white_key_height:self.white_key_height + 1, :]
        white_note_row = np.array(
            [255 if is_white(white_note_row[0, i]) else 0 for i in range(white_note_row.shape[1])]
        )

        for i in range(white_note_row.shape[0]):
            last_note = white_note_row[i - 1]
            this_note = white_note_row[i]

            if np.abs(this_note - last_note) > 0:
                if i - note_start < self.note_gap_length:
                    note_start = i + 1
                else:
                    used_notes = list(pixel_to_note.values())

                    for integer in range(88):
                        if integer not in used_notes:
                            on_note = integer
                            break

                    mid = ((note_start + i - 1) / 2)

                    # if its white, the color at the mid value will be white
                    if white_note_row[int(mid)] == 255:
                        pixel_to_note[mid] = on_note

                    note_start = i + 1

        pixel_to_note = {key: pixel_to_note[key] for key in sorted(pixel_to_note)}
        return pixel_to_note

    def get_note(self, pixel_col):
        """
        :param pixel_col: the column on the image
        :return: the note the pixel_col corresponds to (numerically)
        """
        pixel_to_note = self.pixel2note

        note = pixel_to_note.get(pixel_col) or \
               pixel_to_note[min(pixel_to_note.keys(), key=lambda key: abs(key - pixel_col))]

        return note

    def get_hand(self, color):
        """
        takes in a color and finds out which whether its closest to the left hand, the right hand, or the background
        :param color: pixels color in [blue, green, red]
        :return: 0 if not a note, 1 if its left hand, 2 if its right hand
        """
        color = np.array(color, dtype=np.uint8).reshape((1, 1, 3))
        color_lab = cv2.cvtColor(color, cv2.COLOR_BGR2LAB).reshape((3,)).astype('int32')

        dist_from_background = (color_lab[0] - self.background_color_lab[0]) ** 2 + \
                               (color_lab[1] - self.background_color_lab[1]) ** 2 + \
                               (color_lab[2] - self.background_color_lab[2]) ** 2

        dist_from_left_hand = (color_lab[0] - self.left_hand_color_lab[0]) ** 2 + \
                              (color_lab[1] - self.left_hand_color_lab[1]) ** 2 + \
                              (color_lab[2] - self.left_hand_color_lab[2]) ** 2

        dist_from_right_hand = (color_lab[0] - self.right_hand_color_lab[0]) ** 2 + \
                               (color_lab[1] - self.right_hand_color_lab[1]) ** 2 + \
                               (color_lab[2] - self.right_hand_color_lab[2]) ** 2

        if dist_from_left_hand < dist_from_background and dist_from_left_hand < dist_from_right_hand:
            return 1
        elif dist_from_right_hand < dist_from_background and dist_from_right_hand < dist_from_left_hand:
            return 2
        else:
            return 0

    def get_notes_from_frame(self, frame):
        """ takes in an image frame and returns the notes being played in it at the read height
        :param frame: the frame to read
        :return: the notes about to be played in the frame as a list. [left hand, right hand] with the hands being in
                 the form [note_number, note_letter, note_octave] with the note_number starting at 0
        """

        left_hand_notes = []
        right_hand_notes = []

        image = cv2.imread(frame)  # in BGR

        img_row = image[self.read_height:self.read_height + 1, :, :].reshape(-1, 3)
        img_len = img_row.shape[0]

        # makes information concise. no note is 0, left hand is 1, and right hand is 2.
        relevant_part_of_img = [self.get_hand(img_row[i]) for i in range(img_len)]

        note_start = 0
        # go through the relevant part of the image
        for i in range(1, img_len - 1):

            this_pixel = relevant_part_of_img[i]
            last_pixel = relevant_part_of_img[i - 1]

            # this means that at this position there is a note, while at the last position there wasn't, therefore this
            # is where a new note starts
            # TODO what if two of notes right next to each other? Account for that possibility.
            if this_pixel != 0 and last_pixel == 0:
                note_start = i

            # this means that at this position there is not a note, while at the last position there was, therefore,
            # this is where a note ends. Need to calculate middle of the note to find out what note it actually is.
            # i - notestart > 3 makes sure that one random pixel being on doesn't cause program to think a note is there
            if this_pixel == 0 and last_pixel != 0 and i - note_start > 3:
                mid = int(note_start + (i - note_start) / 2)
                note = self.get_note(mid)
                mid_pixel = relevant_part_of_img[mid]

                # this means that the last pixel was on the top/bottom of a note and therefore may be kinda wack so
                # skip it
                above_last_note = self.get_hand(image[self.read_height - 1][mid])
                below_last_note = self.get_hand(image[self.read_height + 1][mid])
                if above_last_note == 0 or below_last_note == 0:
                    continue

                if mid_pixel == 1:
                    left_hand_notes.append(note)
                elif mid_pixel == 2:
                    right_hand_notes.append(note)

        notes = [left_hand_notes, right_hand_notes]
        return notes

    def process_frame(self, frame_num):
        """
        finds all the notes being played in a frame and then formats it
        :param frame_num: frame number to get notes off of
        :return: 2 lists, one for each hand, which matches the notes and has a 1 if its being played and a 0 if not
        """
        notes = self.get_notes_from_frame(f'{self.frame_dir}/frame_{frame_num}.jpg')
        lr = [1 if i in notes[0] else 0 for i in range(self.last_key_number)]
        rr = [1 if i in notes[1] else 0 for i in range(self.last_key_number)]
        return lr, rr

    def convert(self):
        """
        converts the frames into 2 matrices, one for each hand, that tells when each key is being played
        :return: 2 matrices, one for each hand, that tells when each key is being played
        """
        left_hand = []
        right_hand = []

        # TODO change it so that the matrix time isn't in terms of frames but in seconds so that partial frames can be used

        with concurrent.futures.ProcessPoolExecutor() as executor:
            frames = range(self.number_of_frames)
            results = list(
                tqdm(
                    executor.map(self.process_frame, frames),
                    total=len(frames),
                    file=sys.stdout,
                    desc="Frames Processed"
                )
            )

            for result in results:
                left_hand.append(result[0])
                right_hand.append(result[1])

        left_hand = np.array(left_hand).reshape((self.number_of_frames, self.last_key_number))
        right_hand = np.array(right_hand).reshape((self.number_of_frames, self.last_key_number))

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
