import json
import re
import logging
import os
from difflib import SequenceMatcher
from typing import List, Dict, Any

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

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

def extract_team_names(title: str) -> List[str]:
    if not isinstance(title, str):
        return []
    title = re.sub(r'^.*?:', '', title)
    match = re.search(r'([^-]+)-([^|]+)', title)
    if match:
        team1 = clean_title(match.group(1))
        team2 = clean_title(match.group(2))
        return [team1, team2]
    return []

def teams_similarity(teams1: List[str], teams2: List[str]) -> bool:
    if len(teams1) != 2 or len(teams2) != 2:
        return False
    forward_match = (
            SequenceMatcher(None, teams1[0], teams2[0]).ratio() > 0.8 and
            SequenceMatcher(None, teams1[1], teams2[1]).ratio() > 0.8
    )
    return forward_match

class MatchHighlightsMatcher:
    def __init__(self, min_similarity: float , streams_folder: str, highlights_folder: str):
        self.min_similarity = min_similarity
        self.streams_folder = streams_folder
        self.highlights_folder = highlights_folder

    def find_matching_highlights(self, match: Dict[str, Any], highlights_datas: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        matching_highlights = []
        full_match_teams = extract_team_names(match["title"])

        if not full_match_teams:
            logging.warning(f"No team name found in the match: {match["title"]}")
            return matching_highlights

        for highlight in highlights_datas:
            highlight_teams = extract_team_names(highlight["title"])

            if not highlight_teams:
                continue

            if teams_similarity(full_match_teams, highlight_teams):
                local_path = highlight["local_path"]
                # local_path = "path"
                matching_highlights.append({
                    "highlight_id": highlight["video_id"],
                    "highlight_title": highlight["title"],
                    "url": highlight["url"],
                    # "url": match["video_url"],
                    "local_path": local_path,
                    "file_exists": True,
                    "duration_seconds": highlight["duration_seconds"],
                    "definition": highlight["definition"],
                    "view_count": highlight["view_count"],
                    "like_count": highlight["like_count"],
                    "comment_count": highlight["comment_count"],
                    "tags": highlight["tags"],
                    "similarity_score": SequenceMatcher(None, match["title"], highlight["title"]).ratio(),
                    "teams_matched": full_match_teams,
                    "linking_info": {
                        "linking_method": "string_matching",
                        "confidence_level": "high" if self.min_similarity > 0.8 else "medium"
                    }
                })

        return matching_highlights

    def create_relationship_json(self, streams_file: str, highlights_file: str, output_file: str) -> Dict[str, Any]:
        logging.info(f"Checking folder {self.streams_folder} - Found {len(os.listdir(self.streams_folder))} files")
        logging.info(f"Checking folder {self.highlights_folder} - Found {len(os.listdir(self.highlights_folder))} files")

        try:
            streams_path = os.path.join(os.path.dirname(__file__), "..", "data", streams_file)
            highlights_path = os.path.join(os.path.dirname(__file__), "..", "data", highlights_file)
            with open(streams_path, 'r', encoding="utf-8") as f:
                streams_data = json.load(f)

            with open(highlights_path, 'r', encoding="utf-8") as f:
                highlights_data = json.load(f)

            # if 'streams' not in full_matches_data or 'videos' not in highlights_data:
            #     raise ValueError("Dữ liệu đầu vào không đúng định dạng yêu cầu")

            streams_datas = streams_data["infos"]
            highlights_datas = highlights_data["infos"]

            # streams_datas = streams_data["streams"]
            # highlights_datas = highlights_data["videos"]

            relationships = []
            for match in streams_datas:
                matching_highlights = self.find_matching_highlights(match, highlights_datas)

                if matching_highlights:
                    local_path = match["local_path"]
                    # local_path = "path"
                    relationship = {
                        "full_match": {
                            "video_id": match["video_id"],
                            "title": match["title"],
                            "url": match["url"],
                            # "url": match["video_url"],
                            "local_path": local_path,
                            "file_exists": True,
                            "duration_seconds": match["duration_seconds"],
                            "definition": match["definition"],
                            "published_date": match["published_date"],
                            "view_count": match["view_count"],
                            "like_count": match["like_count"],
                            "comment_count": match["comment_count"],
                            "tags": match["tags"],
                            "team_names": extract_team_names(match["title"])
                        },
                        "highlights": matching_highlights
                    }
                    relationships.append(relationship)

            output_data = {
                "total_matches": len(relationships),
                "relationships": relationships
            }

            output_path = os.path.join(os.path.dirname(__file__), "..", "data", output_file)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)

            logging.info(f"Successfully joined {len(relationships)} videos")
            print(f"Total matches: {len(streams_datas)}")
            print(f"Total highlights: {len(highlights_datas)}")
            return output_data

        except FileNotFoundError as e:
            logging.error(f"File not found: {str(e)}")
            raise
        except json.JSONDecodeError as e:
            logging.error(f"JSON format error: {str(e)}")
            raise
        except Exception as e:
            logging.error(f"Error: {str(e)}")
            raise


def main():
    try:
        matcher = MatchHighlightsMatcher(0.6, "F:/original", "F:/highlight")
        relationships = matcher.create_relationship_json(
            # "youtube_streams.json",
            # "youtube_highlights.json",
            # "match_streams_highlights.json"
            "Full_Match_Info.json",
            "Highlight_Match_Info.json",
            "Match_Streams_With_Highlights.json"
        )
        print(f"{relationships['total_matches']} pairs have been created")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
