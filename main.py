import os
from multiprocessing import Process
import json

import cv2
import matplotlib.pyplot as plt
import py_midicsv as pm

import frames2matrix
import matrix2csv
import youtube2frames
import get_frame_data


def show_image(path):
    image = cv2.imread(path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    plt.imshow(image)
    plt.show()


def show_frames(frame_dir, n_f):
    index = int(n_f / 64)
    while True:
        p = Process(target=show_image, args=(f"{frame_dir}/frame_{index}.jpg",))
        p.start()
        ans = str(input(f"Is this frame ({index}) containing enough info? (Y/N): "))

        if ans.lower() == 'y':
            return
        else:
            index += int(n_f / 16)


if __name__ == '__main__':
    PROJECT_DIR = os.getcwd()

    VIDEO_NAME = 'Fur Elise'
    VIDEO_URL = 'https://www.youtube.com/watch?v=WvWuco54FHg'

    num_frames, fps = youtube2frames.get_frames(video_url=VIDEO_URL, video_name=VIDEO_NAME)

    show_frames(f"{PROJECT_DIR}/{VIDEO_NAME}/frames", num_frames)

    white_key_height, black_key_height, clear_frame_number = get_frame_data.get_data(VIDEO_NAME)

    read_height = int(input("Enter the read height: "))
    left_hand_color = json.loads(input("Enter the left hand note's color in [R, G, B]: "))
    right_hand_color = json.loads(input("Enter the right hand note's color in [R, G, B]: "))

    left_hand, right_hand = frames2matrix.Frames2MatrixConverter(
        f'{PROJECT_DIR}/{VIDEO_NAME}/frames',
        clear_frame=f"{PROJECT_DIR}/{VIDEO_NAME}/frames/frame_{clear_frame_number}.jpg",
        black_key_height=black_key_height,
        white_key_height=white_key_height,
        read_height=read_height,
        left_hand_color=left_hand_color,
        right_hand_color=right_hand_color
    ).convert()

    matrix2csv.matrix_to_csv(left_hand, right_hand, VIDEO_NAME, fps)

    # Parse the CSV into a MIDI file, then save the parsed MIDI file
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
