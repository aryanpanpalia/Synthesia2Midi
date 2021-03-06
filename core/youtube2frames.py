import concurrent.futures
import os
import shutil
import sys

# image operation
import cv2
from pytube import YouTube
from tqdm import tqdm


def display_progress_bar(bytes_received: int, filesize: int, ch: str = "█", scale: float = 0.55):
    columns = shutil.get_terminal_size().columns
    max_width = int(columns * scale)

    filled = int(round(max_width * bytes_received / float(filesize)))
    remaining = max_width - filled
    progress_bar = ch * filled + " " * remaining
    percent = round(100.0 * bytes_received / float(filesize), 1)
    text = f"Video downloaded: {percent}%|{progress_bar}| {bytes_received}/{filesize}\r"
    sys.stdout.write(text)
    sys.stdout.flush()


def on_progress(stream, chunk: bytes, bytes_remaining: int):
    filesize = stream.filesize
    bytes_received = filesize - bytes_remaining
    display_progress_bar(bytes_received, filesize)


def get_frames(video_url, video_dir_path, frame_dir_path, video_name, tag=None):
    video = YouTube(video_url, on_progress_callback=on_progress)

    if tag is None:
        print('*' * 60)
        for stream in video.streams.filter(mime_type="video/mp4").order_by('fps'):
            tag = repr(stream)[repr(stream).find("tag"):repr(stream).find("mime")]
            res = repr(stream)[repr(stream).find("res"):repr(stream).find("fps")]
            fps = repr(stream)[repr(stream).find("fps"):repr(stream).rfind("vcodec")]
            progressive = repr(stream)[repr(stream).find("pro"):repr(stream).rfind("type")]
            print(tag, res, fps, progressive)
        print('*' * 60)
        tag = int(input("Enter a tag to download: "))

    video = video.streams.get_by_itag(tag)

    video.download(output_path=f'{video_dir_path}/', filename=video_name)

    vid_cap = cv2.VideoCapture(f'{video_dir_path}/{video_name}.mp4')
    n_frames = int(vid_cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = int(vid_cap.get(cv2.CAP_PROP_FPS))

    os.makedirs(frame_dir_path, exist_ok=True)
    print(f'\nCreated the following directory: {frame_dir_path}')

    with concurrent.futures.ThreadPoolExecutor() as executor:
        images = (vid_cap.read()[1] for _ in range(n_frames))

        executor.map(
            lambda directory, image, frame_num: cv2.imwrite(f"{directory}/frame_{frame_num}.jpg", image),
            [frame_dir_path] * n_frames,
            tqdm(
                images,
                file=sys.stdout,
                desc="Frames saved",
                total=n_frames
            ),
            range(n_frames)
        )

    vid_cap.release()
    cv2.destroyAllWindows()

    return n_frames, fps
