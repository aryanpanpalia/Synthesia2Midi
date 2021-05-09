import concurrent.futures
import os
import sys

# image operation
import cv2
from pytube import YouTube
from tqdm import tqdm


class FrameExtractor:
    def __init__(self, video_path):
        self.vid_cap = cv2.VideoCapture(video_path)
        self.n_frames = int(self.vid_cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.fps = int(self.vid_cap.get(cv2.CAP_PROP_FPS))

    def extract_frames(self, dest_path=None):
        if dest_path is None:
            raise Exception("You did not pass in a path for the images to go")

        os.mkdir(dest_path)
        print(f'Created the following directory: {dest_path}')

        with concurrent.futures.ThreadPoolExecutor() as executor:
            images = (self.vid_cap.read()[1] for _ in range(self.n_frames))

            executor.map(save_image,
                         [dest_path] * self.n_frames,
                         tqdm(
                             images,
                             file=sys.stdout,
                             desc="Frames saved",
                             total=self.n_frames
                         ),
                         range(self.n_frames))

        self.vid_cap.release()
        cv2.destroyAllWindows()


def get_frames(video_url, video_name=None):
    video = YouTube(video_url)
    if video_name is None:
        video_name = video.title

    print('************************************************************')
    for stream in video.streams.filter(mime_type="video/mp4").order_by('fps'):
        tag = repr(stream)[repr(stream).find("tag"):repr(stream).find("mime")]
        res = repr(stream)[repr(stream).find("res"):repr(stream).find("fps")]
        fps = repr(stream)[repr(stream).find("fps"):repr(stream).rfind("vcodec")]
        progressive = repr(stream)[repr(stream).find("pro"):repr(stream).rfind("type")]
        print(tag, res, fps, progressive)
    print('************************************************************')
    tag = int(input("Enter a tag to download: "))

    video = video.streams.get_by_itag(tag)

    video.download(output_path=f'./{video_name}/', filename=video_name)
    print("\n")

    fe = FrameExtractor(f'./{video_name}/' + video_name + '.mp4')
    fe.extract_frames(dest_path=f'./{video_name}/frames')
    return fe.n_frames, fe.fps


def save_image(dest_path, image, frame_num):
    img_path = f"{dest_path}/frame_{frame_num}.jpg"
    cv2.imwrite(img_path, image)
