import cv2
import numpy as np


class Pixel2Note:

    def __init__(self, clear_frame, black_keys_height, white_keys_height, note_gap_length=3):
        """
        :param clear_frame: a frame where no note is being played and no hands are covering top of piano.
        :param note_gap_length: maximum length of the gap between a B and a C or an E and an F note. If the gap is too
                                large, notes can be skipped as they are perceived as being a note gap instead of an
                                actual note. If the gap is too small, will think of some note gaps as notes.
        :param black_keys_height: height on image of the top of piano keys. this is where the program will read to find
                                  note bounds. Have slightly below the actual top of notes and have pixels unmarked,
                                  uncolored, and unblocked at this height
        """
        self.clear_frame = clear_frame
        self.black_keys_height = black_keys_height
        self.white_keys_height = white_keys_height
        self.image = cv2.imread(clear_frame, cv2.IMREAD_GRAYSCALE)
        self.note_gap_length = note_gap_length

    @staticmethod
    def is_white(color):
        return color > 200

    def get_pixel_to_note(self):
        """
        :return: a dictionary with the keys as approximate pixel values and the values as notes  starting at 1
        """

        top_of_black_notes = self.image[self.black_keys_height:self.black_keys_height + 1, :]
        top_of_black_notes = np.array(
            [255 if Pixel2Note.is_white(top_of_black_notes[0, i]) else 0 for i in range(top_of_black_notes.shape[1])])

        pixel_to_note = {}

        on_note = 0
        note_start = 0

        # only records black notes
        for i in range(top_of_black_notes.shape[0]):
            last_note = top_of_black_notes[i - 1]
            this_note = top_of_black_notes[i]
            diff = np.abs(this_note - last_note) > 0

            if diff:
                if i - note_start < self.note_gap_length:
                    # not a note
                    note_start = i + 1
                else:
                    # is a note and needs to be recorded
                    mid = ((note_start + i) / 2)

                    # if its black, the color at the mid value will be black
                    if top_of_black_notes[int(mid)] == 0:
                        pixel_to_note[mid] = on_note

                    note_start = i + 1
                    on_note += 1

        top_of_white_notes = self.image[self.white_keys_height:self.white_keys_height + 1, :]
        top_of_white_notes = np.array(
            [255 if Pixel2Note.is_white(top_of_white_notes[0, i]) else 0 for i in range(top_of_white_notes.shape[1])])

        for i in range(top_of_white_notes.shape[0]):
            last_note = top_of_white_notes[i - 1]
            this_note = top_of_white_notes[i]
            diff = np.abs(this_note - last_note) > 0

            if diff:
                if i - note_start < self.note_gap_length:
                    # not a note
                    note_start = i + 1
                else:
                    # is a note and needs to be recorded
                    used_notes = list(pixel_to_note.values())

                    for integer in range(88):
                        if integer not in used_notes:
                            on_note = integer
                            break

                    mid = ((note_start + i) / 2)

                    # if its white, the color at the mid value will be white
                    if top_of_white_notes[int(mid)] == 255:
                        pixel_to_note[mid] = on_note

                    note_start = i + 1

        pixel_to_note = {key: pixel_to_note[key] for key in sorted(pixel_to_note)}
        return pixel_to_note

    def get_nearest_note(self, pixel_col):
        """
        :param pixel_col: the column on the image
        :return: the note the pixel_col corresponds to
        """
        pixel_to_note = self.get_pixel_to_note()

        note = pixel_to_note.get(pixel_col) or pixel_to_note[min(pixel_to_note.keys(), key=lambda key: abs(key - pixel_col))]

        return note
