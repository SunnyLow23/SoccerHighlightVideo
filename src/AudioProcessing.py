import os
from moviepy.editor import VideoFileClip
import cv2
from tqdm import tqdm

def process_video(video_path, audio_folder, frame_folder):
    video_name = os.path.splitext(os.path.basename(video_path))[0]

    video_frames_dir = os.path.join(frame_folder, video_name)

    os.makedirs(audio_folder, exist_ok=True)
    os.makedirs(frame_folder, exist_ok=True)
    os.makedirs(video_frames_dir, exist_ok=True)

    try:
        video = VideoFileClip(video_path)
        audio = video.audio
        if audio is not None:
            audio_path = os.path.join(audio_folder, f"{video_name}.mp3")
            audio.write_audiofile(audio_path)
        video.close()
    except Exception as e:
        print(f"Error audio {video_name}: {str(e)}")

    # try:
    #     cap = cv2.VideoCapture(video_path)
    #     total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    #
    #     with tqdm(total=total_frames, desc=f"Processing {video_name}") as pbar:
    #         frame_count = 0
    #         while True:
    #             ret, frame = cap.read()
    #             if not ret:
    #                 break
    #
    #             frame_path = os.path.join(video_frames_dir, f"frame_{frame_count:06d}.jpg")
    #             cv2.imwrite(frame_path, frame)
    #
    #             frame_count += 1
    #             pbar.update(1)
    #
    #     cap.release()
    #
    # except Exception as e:
    #     print(f"Error frames {video_name}: {str(e)}")


def process_all_videos(input_folder, audio_folder, frame_folder):
    os.makedirs(audio_folder, exist_ok=True)
    os.makedirs(frame_folder, exist_ok=True)

    video_extensions = ['.mp4', '.avi', '.mov', '.mkv']

    video_files = []
    for root, _, files in os.walk(input_folder):
        for file in files:
            if any(file.lower().endswith(ext) for ext in video_extensions):
                video_files.append(os.path.join(root, file))

    print(f"Found {len(video_files)} video")

    for video_path in video_files:
        process_video(video_path, audio_folder, frame_folder)


if __name__ == "__main__":
    try:
        input_folder = "F:/processed_original"
        audio_folder = "F:/audio"
        frame_folder = "F:/frame"

        path = "F:/processed_original/_KPD_5LtFNw.mp4"

        process_all_videos(input_folder, audio_folder, frame_folder)
        # process_video(path, audio_folder, frame_folder)

    except Exception as e:
        print(e)