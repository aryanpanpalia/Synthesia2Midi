import os
from multiprocessing import Process
import json

import cv2
import matplotlib.pyplot as plt
import py_midicsv as pm

import frames2matrix
import matrix2csv
import youtube2frames


def show_image(path):
    image = cv2.imread(path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    plt.imshow(image)
    plt.show()


def show_frames(frame_dir, n_f):
    index = int(n_f / 128)
    while True:
        p = Process(target=show_image, args=(f"{frame_dir}/frame_{index}.jpg",))
        p.start()
        ans = str(input(f"Is this frame ({index}) containing enough info? (Y/N): "))

        if ans.lower() == 'y':
            return
        else:
            index += int(n_f / 128)


if __name__ == '__main__':
    PROJECT_DIR = os.getcwd()

    VIDEO_NAME = 'Jazz'
    VIDEO_URL = 'https://www.youtube.com/watch?v=9p2kKIoF2xo'

    num_frames, fps = youtube2frames.get_frames(video_url=VIDEO_URL, video_name=VIDEO_NAME)

    show_frames(f"{PROJECT_DIR}/{VIDEO_NAME}/frames", num_frames)

    white_note_threshold = int(input("Enter the minimum pixel brightness that should correspond to a white note: "))
    white_key_height = int(input("Enter the white key height: "))
    black_key_height = int(input("Enter the black key height: "))
    clear_frame_number = int(input("Enter a clear frame number: "))
    read_height = int(input("Enter the read height: "))
    left_hand_color = json.loads(input("Enter the left hand note's color in [R, G, B]: "))
    right_hand_color = json.loads(input("Enter the right hand note's color in [R, G, B]: "))
    background_color = json.loads(input("Enter the background color in [R, G, B]: "))
    note_gap_length = int(input("Enter the note gap length: "))

    left_hand, right_hand = frames2matrix.Frames2MatrixConverter(
        f'{PROJECT_DIR}/{VIDEO_NAME}/frames',
        clear_frame=f"{PROJECT_DIR}/{VIDEO_NAME}/frames/frame_{clear_frame_number}.jpg",
        black_key_height=black_key_height,
        white_key_height=white_key_height,
        read_height=read_height,
        left_hand_color=left_hand_color,
        right_hand_color=right_hand_color,
        background_color=background_color,
        white_note_threshold=white_note_threshold,
        note_gap_length=note_gap_length
    ).convert()

    matrix2csv.matrix_to_csv(left_hand, right_hand, VIDEO_NAME, fps)

    # Parse the CSVs into a MIDI files, then save the parsed MIDI files
    with open(f"{PROJECT_DIR}/{VIDEO_NAME}/{VIDEO_NAME}.mid", "wb") as output_file:
        midi_object = pm.csv_to_midi(f'{PROJECT_DIR}/{VIDEO_NAME}/csvs/{VIDEO_NAME}.csv')
        midi_writer = pm.FileWriter(output_file)
        midi_writer.write(midi_object)

    with open(f"{PROJECT_DIR}/{VIDEO_NAME}/{VIDEO_NAME}_rh.mid", "wb") as output_file:
        midi_object = pm.csv_to_midi(f'{PROJECT_DIR}/{VIDEO_NAME}/csvs/{VIDEO_NAME}_rh.csv')
        midi_writer = pm.FileWriter(output_file)
        midi_writer.write(midi_object)

    with open(f"{PROJECT_DIR}/{VIDEO_NAME}/{VIDEO_NAME}_lh.mid", "wb") as output_file:
        midi_object = pm.csv_to_midi(f'{PROJECT_DIR}/{VIDEO_NAME}/csvs/{VIDEO_NAME}_lh.csv')
        midi_writer = pm.FileWriter(output_file)
        midi_writer.write(midi_object)
