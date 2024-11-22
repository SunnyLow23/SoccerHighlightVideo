import cv2
import numpy as np
from moviepy.editor import VideoFileClip
from sklearn.cluster import KMeans
import os
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm


class VideoTimeCutter:
    def __init__(self, input_folder, output_folder):
        self.input_folder = input_folder
        self.output_folder = output_folder
        os.makedirs(output_folder, exist_ok=True)

    def detect_scene_change(self, frame1, frame2, threshold=30):
        """Phát hiện thay đổi cảnh dựa trên sự khác biệt giữa các frame"""
        diff = cv2.absdiff(frame1, frame2)
        return np.mean(diff) > threshold

    def is_football_scene(self, frame):
        """Phát hiện cảnh bóng đá dựa trên đặc điểm màu sắc và cấu trúc"""
        # Chuyển frame sang HSV để phân tích màu sắc
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Tìm màu xanh của sân cỏ
        lower_green = np.array([35, 30, 30])
        upper_green = np.array([85, 255, 255])
        green_mask = cv2.inRange(hsv, lower_green, upper_green)

        # Tính tỷ lệ pixel màu xanh
        green_ratio = np.sum(green_mask > 0) / (frame.shape[0] * frame.shape[1])

        return green_ratio > 0.3  # Ngưỡng tỷ lệ màu xanh của sân cỏ

    # def process_single_video(self, video_path):
    #     """Xử lý một video và cắt phần không liên quan"""
    #     try:
    #         output_path = os.path.join(self.output_folder, os.path.basename(video_path))
    #         print(output_path)
    #         clip = VideoFileClip(video_path)
    #
    #         # Lấy mẫu frames để phân tích
    #         sample_times = np.linspace(0, clip.duration, 100)
    #         frames = [clip.get_frame(t) for t in sample_times]
    #         print(frames)
    #
    #         # Phát hiện cảnh bóng đá
    #         is_football = [self.is_football_scene(frame) for frame in frames]
    #         print(is_football)
    #
    #         # Tìm đoạn video chính
    #         start_idx = is_football.index(True)
    #         end_idx = len(is_football) - 1 - is_football[::-1].index(True)
    #         print(start_idx, end_idx)
    #
    #         # Cắt video
    #         start_time = sample_times[start_idx]
    #         end_time = sample_times[end_idx]
    #         print(start_time, end_time)
    #
    #         # Tạo video mới
    #         new_clip = clip.subclip(start_time, end_time)
    #         new_clip.write_videofile(output_path, codec='libx264', audio_codec='aac')
    #         print("Create new video")
    #
    #         clip.close()
    #         new_clip.close()
    #
    #         return True, video_path
    #
    #     except Exception as e:
    #         return False, f"Error processing {video_path}: {str(e)}"

    def process_single_video(self, video_path):
        """Xử lý một video và cắt phần không liên quan"""
        try:
            output_path = os.path.join(self.output_folder, os.path.basename(video_path))
            print(f"Output path: {output_path}")

            print("Đang đọc video...")
            clip = VideoFileClip(video_path)
            print(f"Đã đọc video. Độ dài: {clip.duration} giây")

            # Kiểm tra xem video có đọc được không
            if clip.reader is None:
                raise Exception("Không thể đọc video")

            print("Đang lấy mẫu frames...")
            try:
                # Giảm số lượng frame mẫu xuống để test
                sample_times = np.linspace(0, clip.duration, 20)  # Giảm xuống 20 frame
                frames = []
                for t in sample_times:
                    try:
                        frame = clip.get_frame(t)
                        frames.append(frame)
                        print(f"Đã lấy frame tại thời điểm {t:.2f}s")
                    except Exception as e:
                        print(f"Lỗi khi lấy frame tại {t}s: {str(e)}")

                if not frames:
                    raise Exception("Không lấy được frame nào")

                print(f"Đã lấy được {len(frames)} frames")

            except Exception as e:
                print(f"Lỗi khi lấy mẫu frames: {str(e)}")
                if clip:
                    clip.close()
                return False, f"Error sampling frames: {str(e)}"

            # Phát hiện cảnh bóng đá
            print("Đang phân tích frames...")
            try:
                is_football = []
                for i, frame in enumerate(frames):
                    try:
                        result = self.is_football_scene(frame)
                        is_football.append(result)
                        print(f"Frame {i}: {'là' if result else 'không phải'} cảnh bóng đá")
                    except Exception as e:
                        print(f"Lỗi khi phân tích frame {i}: {str(e)}")

                if not is_football:
                    raise Exception("Không phân tích được frame nào")

                print("Kết quả phân tích:", is_football)

            except Exception as e:
                print(f"Lỗi khi phân tích frames: {str(e)}")
                if clip:
                    clip.close()
                return False, f"Error analyzing frames: {str(e)}"

            try:
                # Tìm đoạn video chính
                if True not in is_football:
                    raise Exception("Không tìm thấy cảnh bóng đá nào")

                start_idx = is_football.index(True)
                end_idx = len(is_football) - 1 - is_football[::-1].index(True)
                print(f"Đoạn video chính: từ frame {start_idx} đến frame {end_idx}")

                # Cắt video
                start_time = sample_times[start_idx]
                end_time = sample_times[end_idx]
                print(f"Thời gian cắt: từ {start_time:.2f}s đến {end_time:.2f}s")

                # Tạo video mới
                print("Đang tạo video mới...")
                new_clip = clip.subclip(start_time, end_time)
                new_clip.write_videofile(output_path, codec='libx264', audio_codec='aac')
                print("Đã tạo xong video mới")

                clip.close()
                new_clip.close()

                return True, video_path

            except Exception as e:
                print(f"Lỗi trong quá trình cắt và lưu video: {str(e)}")
                if clip:
                    clip.close()
                return False, f"Error in cutting and saving video: {str(e)}"

        except Exception as e:
            print(f"Lỗi tổng thể: {str(e)}")
            return False, f"General error: {str(e)}"

    def process_batch(self, num_workers=4):
        """Xử lý hàng loạt video sử dụng đa luồng"""
        video_files = [f for f in os.listdir(self.input_folder) if f.endswith(('.mp4', '.mkv', '.avi'))]

        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            futures = []
            for video_file in video_files:
                video_path = os.path.join(self.input_folder, video_file)
                futures.append(executor.submit(self.process_single_video, video_path))

            # Theo dõi tiến trình xử lý
            results = []
            for future in tqdm(futures, total=len(video_files)):
                results.append(future.result())

        # Tạo báo cáo
        successful = [r[1] for r in results if r[0]]
        failed = [r[1] for r in results if not r[0]]

        print(f"Processed {len(successful)} videos successfully")
        print(f"Failed to process {len(failed)} videos")
        if failed:
            print("Failed videos:")
            for f in failed:
                print(f"- {f}")

# Khởi tạo processor
processor = VideoTimeCutter(
    input_folder="F:/processed_original",
    output_folder="F:/test"
)

path = "F:/processed_original/cNHVkAvqkMA.mp4"

# Xử lý tất cả video trong thư mục
processor.process_batch(num_workers=4)  # Số luồng có thể điều chỉnh tùy theo CPU
# processor.process_single_video(path)