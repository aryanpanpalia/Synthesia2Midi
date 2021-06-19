import os
import sys

import numpy as np
import py_midicsv as pm

sys.path.append('.')

from core import youtube2frames, frames2matrix, matrix2csv


def write_lines(file_name, lines):
    open(file_name, 'w').close()
    file = open(file_name, 'a')
    for line in lines:
        file.write(line)
    file.close()


def full_convert(
        video_name,
        video_url,
        tag,
        white_note_threshold,
        white_key_height,
        black_key_height,
        clear_frame_number,
        read_height,
        left_hand_color,
        right_hand_color,
        background_color,
        note_gap_length,
        video_dir_path=None,
        frame_dir_path=None,
        array_dir_path=None,
        csv_dir_path=None,
        midi_dir_path=None,
):
    if video_dir_path is None:
        video_dir_path = f'./{video_name}'
    if frame_dir_path is None:
        frame_dir_path = f'./{video_name}/frames'
    if array_dir_path is None:
        array_dir_path = f'./{video_name}/arrays'
    if csv_dir_path is None:
        csv_dir_path = f'./{video_name}/csvs'
    if midi_dir_path is None:
        midi_dir_path = f'./{video_name}'

    for path in [video_dir_path, frame_dir_path, array_dir_path, csv_dir_path, midi_dir_path]:
        os.makedirs(path, exist_ok=True)
        print(f'Created the following directory: {path}')

    num_frames, fps = youtube2frames.get_frames(
        video_url=video_url,
        video_name=video_name,
        video_dir_path=video_dir_path,
        frame_dir_path=frame_dir_path,
        tag=tag
    )

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

    os.makedirs(array_dir_path, exist_ok=True)
    print(f'Created the following directory: {array_dir_path}')
    np.save(f'{array_dir_path}/left_hand.npy', left_hand)
    np.save(f'{array_dir_path}/right_hand.npy', right_hand)

    full_csv_lines, right_csv_lines, left_csv_lines = matrix2csv.matrix_to_csv(left_hand, right_hand, fps)

    os.makedirs(csv_dir_path, exist_ok=True)
    print(f'Created the following directory: {csv_dir_path}')
    write_lines(f'{csv_dir_path}/{video_name}.csv', full_csv_lines)
    write_lines(f'{csv_dir_path}/{video_name}_rh.csv', right_csv_lines)
    write_lines(f'{csv_dir_path}/{video_name}_lh.csv', left_csv_lines)

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
