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


def get_lines_from(hand, track_num, fps, ticks_per_ms):
    """
    goes through a hand and converts its information into the form required for the csv file
    :param hand: a list/array/matrix that has the information of what is being played by a hand 
    :param track_num: what track number to give this hand
    :param fps: frames per second of the video downloaded. Used to calculate the time at which a note should be played
    :param ticks_per_ms: number of ticks that occur per millisecond
    :return: a list of lines to be put into the csv for the hand given
    """
    lines = []

    for note_num in range(len(hand)):
        note = hand[note_num]
        for record in note:
            frame_num = record[1]
            second = frame_num / fps
            millisecond = second * 1000
            tick = int(millisecond * ticks_per_ms)

            if record[0] == 0:  # note off event
                lines.append(f"{track_num}, {tick}, Note_off_c, 0, {note_num + 21}, 0\n")
            elif record[0] == 1:  # note on event
                lines.append(f"{track_num}, {tick}, Note_on_c, 0, {note_num + 21}, 127\n")

    return lines


def write_lines(file_name, lines):
    # empty file
    file = open(file_name, 'w')
    file.write("")
    file.close()

    # write lines to file
    file = open(file_name, 'a')
    for line in lines:
        file.write(line)
    file.close()


def matrix_to_csv(l, r, song_name, fps):
    # constants used to calculate timing
    PPQ = 1800
    BPM = 100
    TEMPO = int(60000000 / BPM)
    ticks_per_ms = (BPM * PPQ) / 60000

    right_lines = [
        "1, 0, Start_track\n",
        "1, 0, Title_t, \"Right Hand\"\n",
        f"1, 0, Tempo, {TEMPO}\n"
    ]

    # adds the notes played by the right hand to the right lines for its csv, sorts them, then ends the track
    right_lines.extend(get_lines_from(r, 1, fps, ticks_per_ms))
    merge_sort(right_lines, 0, len(right_lines))
    end_time = int(float(right_lines[-1].split(',')[1]))
    right_lines.append(f"1, {end_time + 5000}, End_track\n")

    left_lines = [
        "2, 0, Start_track\n",
        "2, 0, Title_t, \"Left Hand\"\n",
        "2, 0, Tempo, 600000\n"
    ]

    # adds the notes played by the left hand to the left lines for its csv, sorts them, then ends the track
    left_lines.extend(get_lines_from(l, 2, fps, ticks_per_ms))
    merge_sort(left_lines, 0, len(left_lines))
    end_time = int(float(left_lines[-1].split(',')[1]))
    left_lines.append(f"2, {end_time + 5000}, End_track\n")

    try:
        os.mkdir(f'{song_name}/csvs')
    except FileExistsError:
        pass

    os.chdir(f'{song_name}/csvs')

    # full song
    lines = []
    lines.extend([f"0, 0, Header, 1, 2, {PPQ}\n"])
    lines.extend(right_lines)
    lines.extend(left_lines)
    lines.extend(["0, 0, End_of_file\n"])
    write_lines(f"{song_name}.csv", lines)

    # right hand only
    lines = []
    lines.extend([f"0, 0, Header, 1, 1, {PPQ}\n"])
    lines.extend(right_lines)
    lines.extend(["0, 0, End_of_file\n"])
    write_lines(f"{song_name}_rh.csv", lines)

    # left hand only
    left_lines = [
        "1, 0, Start_track\n",
        "1, 0, Title_t, \"Left Hand\"\n",
        f"1, 0, Tempo, {TEMPO}\n"
    ]

    # adds the notes played by the left hand to the left lines for its csv, sorts them, then ends the track
    left_lines.extend(get_lines_from(l, 1, fps, ticks_per_ms))
    merge_sort(left_lines, 0, len(left_lines))
    end_time = int(float(left_lines[-1].split(',')[1]))
    left_lines.append(f"1, {end_time + 5000}, End_track\n")

    lines = []
    lines.extend([f"0, 0, Header, 1, 1, {PPQ}\n"])
    lines.extend(left_lines)
    lines.extend([f"0, 0, Header, 1, 1, {PPQ}\n"])

    write_lines(f"{song_name}_lh.csv", lines)
