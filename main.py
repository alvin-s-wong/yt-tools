from youtube_transcript_api import YouTubeTranscriptApi
import os
from pprint import pprint
from youtube_transcript_api.formatters import SRTFormatter
from dotenv import load_dotenv
from openai import OpenAI
import json
from pydantic import BaseModel


load_dotenv()
# Add your YouTube API key here
API_KEY = os.environ["GOOGLE_YOUTUBE_API_KEY"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]  # Add this line

# Initialize OpenAI API
client = OpenAI(api_key=OPENAI_API_KEY)

# border0 channel
CHANNEL_ID = "UCLjs_2pd3xMYTP1mo6jTy9A"


def fetch_transcript(video_id):
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    return transcript


def srt_output(transcript, video_id):
    formatter = SRTFormatter()

    # .format_transcript(transcript) turns the transcript into a srt string.
    srt_formatted = formatter.format_transcript(transcript)

    # Now we can write it out to a file.
    with open(f"{video_id}.srt", "w", encoding="utf-8") as srt_file:
        srt_file.write(srt_formatted)


def read_srt_file(video_id):
    # Add this function to read the SRT file
    with open(f"{video_id}.srt", "r", encoding="utf-8") as srt_file:
        return srt_file.read()


class VideoData(BaseModel):
    title: str
    description: str
    chapters: str
    subtitles: str


def process_content_with_llm(srt_content):
    prompt = f"""Based on the raw srt transcript I'll be sharing below, after analysis, please provide the following for YouTube video metadata posting: 
    
    - Engaging title
    - Clear and professional description
    - YouTube formatted chapters with line breaks
    - Subtitles in proper srt format  
    
    Please ensure the following as well:

    - Whenever there is reference to 'border zero', write the proper brand name of 'Border0'.
    - Chapters need to be at least 20 seconds.  Adjust chaptering accordingly.
    
    <raw srt content>
    {srt_content}
    </raw srt content>
    """
    response = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant that analyzes video transcripts and provides improved titles, descriptions, video chapters, and subtitles.",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        response_format=VideoData,
    )
    return response.choices[0].message.parsed


def write_subtitles(video_id, subtitles):
    with open(f"subtitles_{video_id}.srt", "w", encoding="utf-8") as f:
        f.write(subtitles)


def write_chapters(video_id, chapters):
    with open(f"chapters_{video_id}.txt", "w", encoding="utf-8") as f:
        f.write(chapters)


def write_description(video_id, description):
    with open(f"description_{video_id}.txt", "w", encoding="utf-8") as f:
        f.write(description)


def write_title(video_id, title):
    with open(f"title_{video_id}.txt", "w", encoding="utf-8") as f:
        f.write(title)


def main():
    global CHANNEL_ID

    video_id = "2SG4i0ZH69U"
    transcript = fetch_transcript(video_id)
    srt_output(transcript, video_id)

    srt_content = read_srt_file(video_id)
    video_data = process_content_with_llm(srt_content)

    write_subtitles(video_id, video_data.subtitles)
    write_chapters(video_id, video_data.chapters)
    # write_description(video_id, video_data.description)
    # write_title(video_id, video_data.title)

    print("Improved content has been written to separate files.")


if __name__ == "__main__":
    main()
