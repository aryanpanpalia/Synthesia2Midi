import concurrent.futures
import sys

import cv2
import numpy as np
from tqdm import tqdm


class Frames2MatrixConverter:
    def __init__(self, name, frame_dir, num_frames, read_height, first_note, first_white_note_col, tenth_white_note_col,
                 left_hand_color, right_hand_color, background_color, minimum_note_width):
        """
        :param name: name of the song
        :param frame_dir: the directory the frames are in
        :param num_frames: the number of frames
        :param read_height: the height from which to read notes
        :param first_note: the letter value of the first note (must be capital)
        :param first_white_note_col: column of the first white note
        :param tenth_white_note_col: column on the tenth white note
        :param left_hand_color: the color of the notes in the left hand
        :param right_hand_color: the color of the notes in the right hand
        :param background_color: background color
        :param minimum_note_width: maximum gap between white notes accounted for. If the gap is too large, notes can be
                                skipped as they are perceived as being a note gap instead of an actual note. If the gap
                                is too small, it will think of some note gaps as actual notes.
        """

        self.name = name
        self.frame_dir = frame_dir
        self.read_height = read_height
        self.minimum_note_width = minimum_note_width
        self.number_of_frames = num_frames
        self.first_note_value = ord(first_note) - 65  # A->0, B->1, etc...
        self.first_white_note_col = first_white_note_col
        self.tenth_white_note_col = tenth_white_note_col

        self.left_hand_color = np.array(left_hand_color, dtype=np.uint8).reshape((1, 1, 3))
        self.right_hand_color = np.array(right_hand_color, dtype=np.uint8).reshape((1, 1, 3))
        self.background_color = np.array(background_color, dtype=np.uint8).reshape((1, 1, 3))

        self.left_hand_color_lab = cv2.cvtColor(self.left_hand_color, cv2.COLOR_RGB2LAB).reshape((3,)).astype('int32')
        self.right_hand_color_lab = cv2.cvtColor(self.right_hand_color, cv2.COLOR_RGB2LAB).reshape((3,)).astype('int32')
        self.background_color_lab = cv2.cvtColor(self.background_color, cv2.COLOR_RGB2LAB).reshape((3,)).astype('int32')

        self.column2note = self.create_column2note()
        self.last_key_number = list(self.column2note.values())[-1]

    def create_column2note(self):
        """
        creates a dictionary that maps the middle of all the keys to what note number they are
        :return: a dictionary that maps the middle of all the keys to what note number they are
        """
        distance_between_white_notes = (self.tenth_white_note_col - self.first_white_note_col) / 9
        white_note_columns = [
            self.first_white_note_col + distance_between_white_notes * counter for counter in range(60)
        ]
        note_columns = []

        for counter in range(1, len(white_note_columns)):
            last_white_note_col = white_note_columns[counter - 1]
            this_white_note_col = white_note_columns[counter]

            note_columns.append(last_white_note_col)

            if counter % 7 not in [(2 - self.first_note_value) % 7, (5 - self.first_note_value) % 7]:
                # if the current white note is B or E
                # (the black note is closer to this white note than the last white note)
                if (self.first_note_value + counter) % 7 in [1 - self.first_note_value, 4 - self.first_note_value]:
                    approx_black_note_col = (last_white_note_col + 2 * this_white_note_col) / 3
                # if the current white note is D or G
                # (the black note is closer to the last white note than this white note)
                elif (self.first_note_value + counter) % 7 in [2 - self.first_note_value, 6 - self.first_note_value]:
                    approx_black_note_col = (2 * last_white_note_col + this_white_note_col) / 3
                else:
                    approx_black_note_col = (last_white_note_col + this_white_note_col) / 2

                note_columns.append(approx_black_note_col)

        column2note = {note_col: note_num for note_num, note_col in enumerate(note_columns)}

        return column2note

    def get_note(self, pixel_col):
        """
        given a column, returns the note number of the note played at that column
        :param pixel_col: the column on the image
        :return: the note the pixel_col corresponds to (numerically)
        """
        note = self.column2note[min(self.column2note.keys(), key=lambda key: abs(key - pixel_col))]

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

    def get_notes_from_frame(self, frame_num):
        """ takes in an image frame and returns the notes being played in it at the read height
        :param frame_num: the frame number to read
        :return: the notes about to be played in the frame as a list. [left hand, right hand] with the hands being an
                 array with where each note number corresponds with one index and a 1 in the array corresponds to a note
                 being played.
        """

        left_hand_notes = np.zeros(shape=(self.last_key_number,), dtype=np.uint8)
        right_hand_notes = np.zeros(shape=(self.last_key_number,), dtype=np.uint8)

        image = cv2.imread(f'{self.frame_dir}/frame_{frame_num}.jpg')  # in BGR

        img_row = image[self.read_height:self.read_height + 1, :, :].reshape(-1, 3)
        img_len = img_row.shape[0]

        relevant_part_of_img = [self.get_hand(img_row[i]) for i in range(img_len)]

        # De-noising. If a pixel does not have any neighbors that are the same, it is a mistake to be removed.
        for i in range(1, img_len - 1):
            this_pixel = relevant_part_of_img[i]
            last_pixel = relevant_part_of_img[i - 1]
            next_pixel = relevant_part_of_img[i + 1]

            if this_pixel != last_pixel and this_pixel != next_pixel:
                relevant_part_of_img[i] = 0

        note_start = 0

        for i in range(1, img_len - 1):
            this_pixel = relevant_part_of_img[i]
            last_pixel = relevant_part_of_img[i - 1]

            # this means that a new note begins here
            if this_pixel != 0 and last_pixel != this_pixel:
                note_start = i

            # This is where a note ends. Need to calculate middle of the note to find out what note it actually is.
            # i - notestart > x makes sure that one random pixel being on doesn't cause program to think a note is there
            if last_pixel != 0 and this_pixel != last_pixel and i - note_start > self.minimum_note_width:
                mid = int(note_start + (i - note_start) / 2)
                note = self.get_note(mid)
                mid_pixel = relevant_part_of_img[mid]

                # means that the last pixel was on the top/bottom row of a note so skip it
                above_last_note = self.get_hand(image[self.read_height - 1][mid])
                below_last_note = self.get_hand(image[self.read_height + 1][mid])
                if above_last_note == 0 or below_last_note == 0:
                    continue

                if mid_pixel == 1:
                    left_hand_notes[note] = 1
                elif mid_pixel == 2:
                    right_hand_notes[note] = 1

        return left_hand_notes, right_hand_notes

    def convert(self):
        """
        converts the frames into 2 matrices, one for each hand, that tells when each key is being played
        :return: 2 matrices, one for each hand, that tells when each key is being played (0 corresponding to note off
                 1 to note on.) Tells the time in frame number.
        """
        left_hand = []
        right_hand = []

        with concurrent.futures.ProcessPoolExecutor() as executor:
            frames = range(self.number_of_frames)
            results = list(
                tqdm(
                    executor.map(self.get_notes_from_frame, frames),
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

        return right_hand, left_hand
