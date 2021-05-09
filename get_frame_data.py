import sys

import cv2
import os
from tqdm import trange


def is_colored(pixel):
    return abs(pixel[0] - pixel[1]) > 50 or abs(pixel[0] - pixel[2]) > 50 or abs(pixel[1] - pixel[2]) > 50


def get_data(song_name):
    frame_dir = f"./{song_name}/frames/"
    number_of_frames = len([name for name in os.listdir(frame_dir) if os.path.isfile(os.path.join(frame_dir, name))])
    interval = number_of_frames // 256

    white_rows = []
    black_rows = []
    clear_frames = []

    for frame_num in trange(interval, number_of_frames, interval, file=sys.stdout):
        image = cv2.imread(f"{frame_dir}/frame_{frame_num}.jpg")
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB).astype('int32')

        num_rows = image.shape[0]
        num_cols = image.shape[1]

        row_num = num_rows - 1
        running = True
        white_row = -1
        black_row = -1
        is_clear = True
        while running:
            # getting rows average color
            row = image[row_num]
            avg = sum(row) / num_cols
            avg_of_avg = sum(avg) / len(avg)

            # see if it is a clear frame.
            for i in range(row.shape[0]):
                if is_colored(row[i]):
                    is_clear = False
                    break

            if white_row == -1:  # if haven't yet found white row
                if avg_of_avg > 225:
                    white_row = row_num
            elif black_row == -1:  # if already found white row but not black row
                if 100 < avg_of_avg < 175:
                    black_row = row_num
            if (white_row != -1 and black_row != -1) or row_num == 0:
                running = False

            row_num -= 1

        white_rows.append(white_row)
        black_rows.append(black_row)
        if is_clear:
            clear_frames.append(frame_num)

    white_row_final = int(sum(white_rows) / len(white_rows)) - 1
    black_row_final = int(sum(black_rows) / len(black_rows)) - 1

    return white_row_final, black_row_final, clear_frames[0]
