import re
import os
import json
import shutil
from difflib import SequenceMatcher
import logging
import hashlib

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def generate_hash(value: str) -> str:
    return hashlib.md5(value.encode('utf-8')).hexdigest()

def clean_title(title: str) -> str:
    if not isinstance(title, str):
        return ""
    title = re.sub(r"[/.🔴:|：｜⧸'&＂-]", '', title)
    title = title.lower()
    return '_'.join(title.split())

def clean_text(text: str) -> str:
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r"[/.🔴:|'&-]", '', text)
    text = re.sub(r"amp;", "", text)
    text = re.sub(r"#39;", "", text)
    text = re.sub(r"quot;", "", text)
    return '_'.join(text.split())

class VideoFileRenamer:
    def __init__(self, source_folder: str, destination_folder: str, json_file: str):
        self.source_folder = source_folder
        self.destination_folder = destination_folder
        self.json_file = os.path.join(
            os.path.dirname(__file__),
            "..",
            "data",
            json_file
        )
        os.makedirs(destination_folder, exist_ok=True)

    def find_matching_video(self, filename: str, datas: list) -> dict:
        cleaned_filename = self.clean_title(filename)

        for video in datas:
            json_title = self.clean_text(video.get("title", ""))
            similarity = SequenceMatcher(None, cleaned_filename, json_title).ratio()

            if similarity >= 0.95:
                return {
                    "video_id": video.get("video_id"),
                    "similarity": similarity,
                    "original_title": video.get("title")
                }
        return None

    def process_files(self):
        try:
            with open(self.json_file, 'r', encoding="utf-8") as f:
                file_data = json.load(f)

            datas = file_data.get("infos")
            processed_count = 0
            skipped_count = 0

            video_info_by_hash = {}
            for video in datas:
                hashed_title = generate_hash(clean_text(video["title"]))
                video_info_by_hash[hashed_title] = video

            for file_name in os.listdir(self.source_folder):
                if file_name.endswith(".mp4"):
                    cleaned_file_name = clean_title(os.path.splitext(file_name)[0])
                    hashed_file_name = generate_hash(cleaned_file_name)

                    # match = self.find_matching_video(filename, datas)
                    if hashed_file_name in video_info_by_hash:
                        extension = os.path.splitext(file_name)[1]
                        new_file_name = f"{video_info_by_hash[hashed_file_name]["video_id"]}{extension}"

                        source_path = os.path.join(self.source_folder, file_name)
                        destination_path = os.path.join(self.destination_folder, new_file_name)
                        shutil.copy2(source_path, destination_path)

                        processed_count += 1

                        logging.info(f"Processed: {file_name}")
                        logging.info(f"New name: {new_file_name}")
                        # logging.info(f"Similarity: {match["similarity"]:.2%}")
                    else:
                        skipped_count += 1
                        logging.warning(f"No match found for: {file_name}")

            logging.info(f"Processing completed. Processed: {processed_count}, Skipped: {skipped_count}")

        except Exception as e:
            logging.error(f"Error: {str(e)}")
            raise

def main():
    settings = {
        # "source_folder": r"F:/original",
        # "destination_folder": r"F:/processed_original",
        # "json_file": "Full_Match_Info.json"
        "source_folder": r"F:/highlight",
        "destination_folder": r"F:/processed_highlight",
        "json_file": "Highlight_Match_Info.json"
    }

    try:
        renamer = VideoFileRenamer(**settings)
        renamer.process_files()
    except Exception as e:
        logging.error(f"Error: {str(e)}")


if __name__ == "__main__":
    main()