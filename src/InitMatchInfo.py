import os
import json
import logging
from typing import Dict, Any
import hashlib
import re

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
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

class InitMatchInfo:
    def __init__(self, input_file: str, input_folder: str, output_file: str):
        self.input_file = os.path.join(
            os.path.dirname(__file__),
            "..",
            "data",
            input_file,
        )
        self.input_folder = input_folder
        self.output_file = os.path.join(
            os.path.dirname(__file__),
            "..",
            "data",
            output_file,
        )

    def initialize_match_infomation(self) -> Dict[str, Any]:
        logging.info(f"Checking file {self.input_file}")
        logging.info(f"Checking folder {self.input_folder}")

        try:
            with open(self.input_file, 'r', encoding='utf-8') as f:
                file_data = json.load(f)

            datas = file_data.get("streams") or file_data.get("videos")
            if not datas:
                raise ValueError("Invalid input file: no 'streams' or 'videos' key found.")

            video_type = "Full Match" if "streams" in file_data else "Highlight Match"

            video_info_by_hash = {}
            for video in datas:
                hashed_title = generate_hash(clean_text(video["title"]))
                # print(clean_text(video["title"]))
                video_info_by_hash[hashed_title] = video

            infos = []
            for file_name in os.listdir(self.input_folder):
                if file_name.endswith(".mp4"):
                    cleaned_file_name = clean_title(os.path.splitext(file_name)[0])
                    hashed_file_name = generate_hash(cleaned_file_name)

                    if hashed_file_name in video_info_by_hash:
                        video = video_info_by_hash[hashed_file_name]
                        local_path = os.path.join(self.input_folder, f"{video["title"]}.mp4").replace("/", '')
                        info = {
                            "id": video["id"],
                            "video_id": video["video_id"],
                            "title": video["title"],
                            "url": video["video_url"],
                            "local_path": local_path,
                            "duration_seconds": video["duration_seconds"],
                            "published_date": video["published_date"],
                            "definition": video["definition"],
                            "view_count": video["view_count"],
                            "like_count": video["like_count"],
                            "comment_count": video["comment_count"],
                            "tags": video["tags"],
                        }
                        infos.append(info)
                    # if hashed_file_name not in video_info_by_hash:
                    #     print(cleaned_file_name)

            output_data = {
                "type": video_type,
                "total_videos": len(infos),
                "infos": infos,
            }

            with open(self.output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)

            logging.info(f"File {self.output_file} has been initialized")
            return output_data


        except FileNotFoundError as e:
            logging.error(f"File not found: {str(e)}")
            raise
        except json.JSONDecodeError as e:
            logging.error(f"JSON decoding error: {str(e)}")
            raise
        except Exception as e:
            logging.error(f"Unexpected error: {str(e)}")
            raise

def main():
    try:
        initMatchInfo = InitMatchInfo(
            input_file="youtube_streams.json",
            input_folder="F:/original",
            output_file="Full_Match_Info.json"
        )
        infos = initMatchInfo.initialize_match_infomation()
        print(f"Infomation has been initialized: {infos['total_videos']} videos")

        initHighlightInfo = InitMatchInfo(
            input_file="youtube_highlights.json",
            input_folder="F:/highlight",
            output_file="Highlight_Match_Info.json"
        )
        infos = initHighlightInfo.initialize_match_infomation()
        print(f"Infomation has been initialized: {infos['total_videos']} videos")

    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
