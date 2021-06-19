import json
import os
import sys
from multiprocessing import Process

import cv2
import matplotlib.pyplot as plt
import numpy as np
import py_midicsv as pm

sys.path.append('.')

from core import youtube2frames, frames2matrix, matrix2csv


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


def write_lines(file_name, lines):
    open(file_name, 'w').close()
    file = open(file_name, 'a')
    for line in lines:
        file.write(line)
    file.close()


def prompt(variable_name: str, default):
    value = input(f"[Default: \"{default}\"] Enter the {variable_name.replace('_', ' ')}: ")
    if value.strip() == '':
        value = default

    return value if value.strip() != ' ' else default


def partial_convert(
        video_name=None,
        video_url=None,
        tag=None,
        white_note_threshold=None,
        white_key_height=None,
        black_key_height=None,
        clear_frame_number=None,
        read_height=None,
        left_hand_color=None,
        right_hand_color=None,
        background_color=None,
        note_gap_length=None,
        video_dir_path=None,
        frame_dir_path=None,
        array_dir_path=None,
        csv_dir_path=None,
        midi_dir_path=None,
):
    if None in locals().values():
        print("Click enter to use default values.")

    if video_name is None:
        video_name = prompt('video_name', 'video name')

    if video_url is None:
        video_url = input("[No default] Enter the video url: ")

    if video_dir_path is None:
        video_dir_path = prompt('video_dir_path', f'./{video_name}')

    if frame_dir_path is None:
        frame_dir_path = prompt('frame_dir_path', f'./{video_name}/frames')

    os.makedirs(video_dir_path, exist_ok=True)
    print(f'Created the following directory: {video_dir_path}')

    num_frames, fps = youtube2frames.get_frames(
        video_url=video_url,
        video_name=video_name,
        video_dir_path=video_dir_path,
        frame_dir_path=frame_dir_path,
        tag=tag
    )

    if None in [white_note_threshold, white_key_height, black_key_height, clear_frame_number, read_height,
                left_hand_color, right_hand_color, background_color, note_gap_length]:
        show_frames(frame_dir_path, num_frames)

    if white_note_threshold is None:
        prompt('white_note_threshold', 240)

    if white_key_height is None:
        white_key_height = int(input("[No default] Enter the white key height: "))

    if black_key_height is None:
        black_key_height = int(input("[No default] Enter the black key height: "))

    if clear_frame_number is None:
        clear_frame_number = int(input("Enter a clear frame number: "))

    if read_height is None:
        prompt('read_height', 10)

    if left_hand_color is None:
        left_hand_color = json.loads(input("Enter the left hand note's color in [R, G, B]: "))

    if right_hand_color is None:
        right_hand_color = json.loads(input("Enter the right hand note's color in [R, G, B]: "))

    if black_key_height is None:
        black_key_height = prompt('black_key_height', [33, 33, 33])

    if note_gap_length is None:
        note_gap_length = int(input("Enter the note gap length: "))

    left_hand, right_hand = frames2matrix.Frames2MatrixConverter(
        name=video_name,
        frame_dir=frame_dir_path,
        clear_frame_number=clear_frame_number,
        num_frames=num_frames,
        black_key_height=black_key_height,
        white_key_height=white_key_height,
        read_height=read_height,
        left_hand_color=left_hand_color,
        right_hand_color=right_hand_color,
        background_color=background_color,
        white_note_threshold=white_note_threshold,
        note_gap_length=note_gap_length
    ).convert()

    if array_dir_path is None:
        array_dir_path = prompt('array_dir_path', f'./{video_name}/arrays')

    os.makedirs(array_dir_path, exist_ok=True)
    print(f'Created the following directory: {array_dir_path}')
    np.save(f'{array_dir_path}/left_hand.npy', left_hand)
    np.save(f'{array_dir_path}/right_hand.npy', right_hand)

    full_csv_lines, right_csv_lines, left_csv_lines = matrix2csv.matrix_to_csv(left_hand, right_hand, fps)

    if csv_dir_path is None:
        csv_dir_path = prompt('csv_dir_path', f'./{video_name}/csvs')

    os.makedirs(csv_dir_path, exist_ok=True)
    print(f'Created the following directory: {csv_dir_path}')
    write_lines(f'{csv_dir_path}/{video_name}.csv', full_csv_lines)
    write_lines(f'{csv_dir_path}/{video_name}_rh.csv', right_csv_lines)
    write_lines(f'{csv_dir_path}/{video_name}_lh.csv', left_csv_lines)

    if midi_dir_path is None:
        midi_dir_path = prompt('midi_dir_path', f'./{video_name}')

    os.makedirs(midi_dir_path, exist_ok=True)
    print(f'Created the following directory: {midi_dir_path}')

    # Parse the CSVs into a MIDI files, then save the parsed MIDI files
    with open(f"{midi_dir_path}/{video_name}.mid", "wb") as output_file:
        midi_object = pm.csv_to_midi(f'{csv_dir_path}/{video_name}.csv')
        pm.FileWriter(output_file).write(midi_object)

    with open(f"{midi_dir_path}/{video_name}_rh.mid", "wb") as output_file:
        midi_object = pm.csv_to_midi(f'{csv_dir_path}/{video_name}_rh.csv')
        pm.FileWriter(output_file).write(midi_object)

    with open(f"{midi_dir_path}/{video_name}_lh.mid", "wb") as output_file:
        midi_object = pm.csv_to_midi(f'{csv_dir_path}/{video_name}_lh.csv')
        pm.FileWriter(output_file).write(midi_object)
