import os


def merge_sort(array, left_index, right_index):
    if left_index >= right_index:
        return
    middle = (left_index + right_index) // 2
    merge_sort(array, left_index, middle)
    merge_sort(array, middle + 1, right_index)
    merge(array, left_index, right_index, middle)


def merge(array, left_index, right_index, middle):
    left_copy = array[left_index:middle + 1]
    right_copy = array[middle + 1:right_index + 1]

    left_copy_index = 0
    right_copy_index = 0
    sorted_index = left_index

    while left_copy_index < len(left_copy) and right_copy_index < len(right_copy):

        left_item = left_copy[left_copy_index]
        right_item = right_copy[right_copy_index]

        left_elem_to_compare = int(
            float(left_item[left_item.index(",") + 2: left_item.index(",", left_item.index(",") + 2)]))
        right_elem_to_compare = int(
            float(right_item[right_item.index(",") + 2:right_item.index(",", right_item.index(",") + 2)]))

        if left_elem_to_compare <= right_elem_to_compare:
            array[sorted_index] = left_item
            left_copy_index = left_copy_index + 1
        else:
            array[sorted_index] = right_item
            right_copy_index = right_copy_index + 1

        sorted_index = sorted_index + 1

    while left_copy_index < len(left_copy):
        array[sorted_index] = left_copy[left_copy_index]
        left_copy_index = left_copy_index + 1
        sorted_index = sorted_index + 1

    while right_copy_index < len(right_copy):
        array[sorted_index] = right_copy[right_copy_index]
        right_copy_index = right_copy_index + 1
        sorted_index = sorted_index + 1


def get_lines_from(hand, track_num, fps, tpms):
    lines = []

    for note_num in range(len(hand)):
        note = hand[note_num]
        for record in note:
            if record[0] == 0:  # note off event
                frame_num = record[1]
                second = frame_num / fps
                millisecond = second * 1000
                tick = int(millisecond * tpms)

                lines.append(f"{track_num}, {tick}, Note_off_c, 0, {note_num + 9 + 12}, 0\n")
            elif record[0] == 1:  # note on event
                frame_num = record[1]
                second = frame_num / fps
                millisecond = second * 1000
                tick = millisecond * tpms

                lines.append(f"{track_num}, {tick}, Note_on_c, 0, {note_num + 9 + 12}, 127\n")

    return lines


def write_lines(file_name, ls):
    # empty file
    file = open(file_name, 'w')
    file.write("")
    file.close()

    # put all the lines together
    lines = []
    for item in ls:
        lines.extend(item)

    # write lines to file
    file = open(file_name, 'a')
    for line in lines:
        file.write(line)
    file.close()


def matrix_to_csv(l, r, song_name, fps):
    PPQ = 1800
    BPM = 100
    TEMPO = 60000000 / BPM
    tpms = (BPM * PPQ) / 60000

    last_line = "0, 0, End_of_file\n"

    right_lines = ["1, 0, Start_track\n",
                   "1, 0, Title_t, \"Right Hand\"\n",
                   f"1, 0, Tempo, {TEMPO}\n"]

    # adds right hand
    right_lines.extend(get_lines_from(r, 1, fps, tpms))
    merge_sort(right_lines, 0, len(right_lines))
    end_time = int(float(right_lines[-1].split(',')[1]))
    right_lines.append(f"1, {end_time + 5000}, End_track\n")

    left_lines = ["2, 0, Start_track\n",
                  "2, 0, Title_t, \"Left Hand\"\n",
                  "2, 0, Tempo, 600000\n"]

    # adds left hand
    left_lines.extend(get_lines_from(l, 2, fps, tpms))
    merge_sort(left_lines, 0, len(left_lines))
    end_time = int(float(left_lines[-1].split(',')[1]))
    left_lines.append(f"2, {end_time + 5000}, End_track\n")

    try:
        os.mkdir(f'{song_name}/csvs')
    except FileExistsError:
        pass

    os.chdir(f'{song_name}/csvs')

    # full song
    write_lines(f"{song_name}.csv", [[f"0, 0, Header, 1, 2, {PPQ}\n"], right_lines, left_lines, [last_line]])
    # right hand only
    write_lines(f"{song_name}_rh.csv", [[f"0, 0, Header, 1, 1, {PPQ}\n"], right_lines, [last_line]])

    # left hand only
    left_lines = ["1, 0, Start_track\n",
                  "1, 0, Title_t, \"Left Hand\"\n",
                  f"1, 0, Tempo, {TEMPO}\n"]

    left_lines.extend(get_lines_from(l, 1, fps, tpms))
    merge_sort(left_lines, 0, len(left_lines))
    end_time = int(float(left_lines[-1].split(',')[1]))
    left_lines.append(f"1, {end_time + 5000}, End_track\n")

    write_lines(f"{song_name}_lh.csv", [[f"0, 0, Header, 1, 1, {PPQ}\n"], left_lines, [last_line]])