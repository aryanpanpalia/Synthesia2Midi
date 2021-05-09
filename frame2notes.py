import cv2

import numpy as np


class Frame2Notes:

    def __init__(self, first_note, first_octave, pixel2note, read_height,
                 left_hand_color, right_hand_color, background_color=[33, 33, 33]):
        """
        :param first_note: First note of the keyboard. Used to orient everything
        :param first_octave: Octave given to first note on keyboard. Used to orient everything
        :param pixel2note: a pixel_to_note object to get where notes are
        :param read_height: height on frame from which to read notes
        :param left_hand_color: colors of notes played by left hand. given in RGB as [red, green, blue]
        :param right_hand_color: colors of notes played by right hand. given in RGB as [red, green, blue]
        :param background_color: color of background. Given in RGB as [red, green, blue]
        """

        self.NOTES = ["A", "A#", "B", "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#",
                      "A", "A#", "B", "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#",
                      "A", "Bb", "B", "C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab",
                      "A", "Bb", "B", "C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab"]
        first_index = self.NOTES.index(first_note)
        self.NOTES = self.NOTES[first_index:first_index + 12]
        self.NOTES.insert(0, None)

        self.first_octave = first_octave
        self.first_note = first_note
        self.pixel2note = pixel2note
        self.read_height = read_height

        self.left_hand_color = np.array(left_hand_color, dtype=np.uint8).reshape((1, 1, 3))
        self.right_hand_color = np.array(right_hand_color, dtype=np.uint8).reshape((1, 1, 3))
        self.background_color = np.array(background_color, dtype=np.uint8).reshape((1, 1, 3))

        self.left_hand_color_lab = cv2.cvtColor(self.left_hand_color, cv2.COLOR_RGB2LAB).reshape((3,)).astype('int32')
        self.right_hand_color_lab = cv2.cvtColor(self.right_hand_color, cv2.COLOR_RGB2LAB).reshape((3,)).astype('int32')
        self.background_color_lab = cv2.cvtColor(self.background_color, cv2.COLOR_RGB2LAB).reshape((3,)).astype('int32')

    def get_hand(self, color):
        """
        :param color: pixels color in [blue, green, red]
        :return: 1 if its left hand, 0 if not a note, 2 if its right hand
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

        # print(color_lab, dist_from_background, dist_from_left_hand, dist_from_right_hand, self.left_hand_color_lab, self.right_hand_color_lab)

        if dist_from_left_hand < dist_from_background and dist_from_left_hand < dist_from_right_hand:
            return 1
        elif dist_from_right_hand < dist_from_background and dist_from_right_hand < dist_from_left_hand:
            return 2
        else:
            return 0

    def get(self, frame, numbers_only=False):
        """ takes in an image frame and returns the notes being played in it at the read height
        :param frame: the frame to read
        :param numbers_only: whether to only return the number value of the note
        :return: the notes about to be played in the frame as a list. [left hand, right hand] with the hands being in
                 the form [note_number, note_letter, note_octave] with the note_number starting at 0
        """

        left_hand_notes = []
        right_hand_notes = []

        image = cv2.imread(frame)  # in BGR

        img_row = image[self.read_height:self.read_height + 1, :, :].reshape(-1, 3)
        img_len = img_row.shape[0]

        # makes information concise. no note is 0, left hand is 1, and right hand is 2.
        # relevant_part_of_img = [self.get_hand(img_row[i]) for i in range(img_len)]
        # relevant_part_of_img_prime = list(map(self.get_hand, img_row))

        relevant_part_of_img = np.empty(shape=img_len, dtype=np.int8)
        for i in range(img_len):
            relevant_part_of_img[i] = self.get_hand(img_row[i])

        # debugging
        # print({i: relevant_part_of_img[i] for i in range(len(relevant_part_of_img))})

        note_start = 0
        # go through the relevant part of the image
        for i in range(1, img_len - 1):

            this_pixel = relevant_part_of_img[i]
            last_pixel = relevant_part_of_img[i - 1]

            # this means that at this position there is a note, while at the last position there wasn't, therefore this
            # is where a new note starts

            # what if left hand and right hand pixels right next to each other? do thispixel != last pixel?
            if this_pixel != 0 and last_pixel == 0:
                note_start = i

            # this means that at this position there is not a note, while at the last position there was, therefore,
            # this is where a note ends. Need to calculate middle of the note to find out what note it actually is.
            # i - notestart > 3 makes sure that one random pixel being on doesn't cause program to think a note is there
            if this_pixel == 0 and last_pixel != 0 and i - note_start > 3:
                mid = int(note_start + (i - note_start) / 2)
                note = self.pixel2note.get_nearest_note(mid)
                mid_pixel = relevant_part_of_img[mid]

                # this means that the last pixel was on the top/bottom of a note and therefore may be kinda wack so
                # skip it
                above_last_note = self.get_hand(image[self.read_height - 1][mid])
                below_last_note = self.get_hand(image[self.read_height + 1][mid])
                if above_last_note == 0 or below_last_note == 0:
                    continue

                if numbers_only:
                    if mid_pixel == 1:
                        left_hand_notes.append(note)
                    elif mid_pixel == 2:
                        right_hand_notes.append(note)
                else:
                    note_letter = self.NOTES[note % 12 + 1] if not note % 12 == 0 else self.first_note
                    note_octave = note // 12 + self.first_octave
                    if mid_pixel == 1:
                        left_hand_notes.append([note, note_letter + str(note_octave)])
                    elif mid_pixel == 2:
                        right_hand_notes.append([note, note_letter + str(note_octave)])

        notes = [left_hand_notes, right_hand_notes]
        return notes
