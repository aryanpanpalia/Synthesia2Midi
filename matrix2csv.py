def get_lines_from(hand, track_num, fps, ticks_per_ms):
    """
    goes through a hand and converts its information into the form required for the csv file
    :param hand: a matrix that has the information of what is being played by a hand
    :param track_num: what track number to give this hand
    :param fps: frames per second of the video downloaded. Used to calculate the time at which a note should be played
    :param ticks_per_ms: number of ticks that occur per millisecond
    :return: a list of lines to be put into the csv for the hand given
    """

    def to_intervals(array):
        in_intervals = []

        for column_index in range(array.shape[1]):
            col = array[:, column_index]
            new = []
            count = 1

            for i in range(1, col.shape[0]):
                if col[i] == col[i - 1]:
                    count += 1
                    if i == col.shape[0] - 1:  # if on the last element of column. have to record now.
                        new.append([col[i], count])
                else:
                    new.append([col[i - 1], count])
                    count = 1

            in_intervals.append(new)

        return in_intervals

    def to_abs(array):
        in_abs = []

        for note in array:
            new = []
            time_count = 0
            for occurrence in note:
                new.append([occurrence[0], time_count])
                time_count += occurrence[1]
            in_abs.append(new)

        return in_abs

    hand = to_abs(to_intervals(hand))

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


def matrix_to_csv(left_hand_array, right_hand_array, fps):
    # constants used to calculate timing
    PPQ = 1800
    BPM = 100
    TEMPO = int(60000000 / BPM)
    ticks_per_ms = (BPM * PPQ) / 60000

    right_hand_lines = [
        "1, 0, Start_track\n",
        "1, 0, Title_t, \"Right Hand\"\n",
        f"1, 0, Tempo, {TEMPO}\n"
    ]

    # adds the notes played by the right hand to the right lines for its csv, sorts them, then ends the track
    right_hand_lines.extend(get_lines_from(right_hand_array, track_num=1, fps=fps, ticks_per_ms=ticks_per_ms))
    right_hand_lines.sort(key=lambda line: float(line[line.index(",") + 2: line.index(",", line.index(",") + 2)]))
    end_time = int(float(right_hand_lines[-1].split(',')[1]))
    right_hand_lines.append(f"1, {end_time + 5000}, End_track\n")

    left_hand_lines = [
        "2, 0, Start_track\n",
        "2, 0, Title_t, \"Left Hand\"\n",
        "2, 0, Tempo, 600000\n"
    ]

    # adds the notes played by the left hand to the left lines for its csv, sorts them, then ends the track
    left_hand_lines.extend(get_lines_from(left_hand_array, track_num=2, fps=fps, ticks_per_ms=ticks_per_ms))
    left_hand_lines.sort(key=lambda line: float(line[line.index(",") + 2: line.index(",", line.index(",") + 2)]))
    end_time = int(float(left_hand_lines[-1].split(',')[1]))
    left_hand_lines.append(f"2, {end_time + 5000}, End_track\n")

    # full song
    full_csv_lines = []
    full_csv_lines.extend([f"0, 0, Header, 1, 2, {PPQ}\n"])
    full_csv_lines.extend(right_hand_lines)
    full_csv_lines.extend(left_hand_lines)
    full_csv_lines.extend(["0, 0, End_of_file\n"])

    # right hand only
    right_csv_lines = []
    right_csv_lines.extend([f"0, 0, Header, 1, 1, {PPQ}\n"])
    right_csv_lines.extend(right_hand_lines)
    right_csv_lines.extend(["0, 0, End_of_file\n"])

    # left hand only
    left_hand_lines = [
        "1, 0, Start_track\n",
        "1, 0, Title_t, \"Left Hand\"\n",
        f"1, 0, Tempo, {TEMPO}\n"
    ]

    # adds the notes played by the left hand to the left lines for its csv, sorts them, then ends the track
    left_hand_lines.extend(get_lines_from(left_hand_array, track_num=1, fps=fps, ticks_per_ms=ticks_per_ms))
    left_hand_lines.sort(key=lambda line: float(line[line.index(",") + 2: line.index(",", line.index(",") + 2)]))
    end_time = int(float(left_hand_lines[-1].split(',')[1]))
    left_hand_lines.append(f"1, {end_time + 5000}, End_track\n")

    left_csv_lines = []
    left_csv_lines.extend([f"0, 0, Header, 1, 1, {PPQ}\n"])
    left_csv_lines.extend(left_hand_lines)
    left_csv_lines.extend([f"0, 0, Header, 1, 1, {PPQ}\n"])

    return full_csv_lines, right_csv_lines, left_csv_lines
