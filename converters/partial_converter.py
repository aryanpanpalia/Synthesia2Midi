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
    value = input(f"[Default: {default}] Enter the {variable_name.replace('_', ' ')}: ")
    if value.strip() == '':
        value = default

    return value if value.strip() != ' ' else default


def partial_convert(
        video_name=None,
        video_url=None,
        tag=None,
        first_note=None,
        first_white_note_col=None,
        tenth_white_note_col=None,
        read_height=None,
        left_hand_color=None,
        right_hand_color=None,
        background_color=None,
        minimum_note_width=None,
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

    if None in [first_note, first_white_note_col, tenth_white_note_col, read_height,
                left_hand_color, right_hand_color, background_color, minimum_note_width]:
        show_frames(frame_dir_path, num_frames)

    if first_note is None:
        first_note = prompt('first_note (capital)', 'A')

    if first_white_note_col is None:
        first_white_note_col = float(input("[No default] Enter the first white note column: "))

    if tenth_white_note_col is None:
        tenth_white_note_col = float(input("[No default] Enter the tenth white note column: "))

    if read_height is None:
        read_height = prompt('read_height', 50)

    if left_hand_color is None:
        left_hand_color = json.loads(input("Enter the left hand note's color in [R, G, B]: "))

    if right_hand_color is None:
        right_hand_color = json.loads(input("Enter the right hand note's color in [R, G, B]: "))

    if background_color is None:
        background_color = json.loads(input("Enter the background color in [R, G, B]: "))

    if minimum_note_width is None:
        minimum_note_width = int(input("Enter the minimum note width: "))

    left_hand, right_hand = frames2matrix.Frames2MatrixConverter(
        name=video_name,
        frame_dir=frame_dir_path,
        num_frames=num_frames,
        read_height=read_height,
        first_note=first_note,
        first_white_note_col=first_white_note_col,
        tenth_white_note_col=tenth_white_note_col,
        left_hand_color=left_hand_color,
        right_hand_color=right_hand_color,
        background_color=background_color,
        minimum_note_width=minimum_note_width
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
