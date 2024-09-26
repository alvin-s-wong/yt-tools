import os
from googleapiclient.discovery import build


from dotenv import load_dotenv

load_dotenv()
# Add your YouTube API key here
API_KEY = os.environ["GOOGLE_YOUTUBE_API_KEY"]


def fetch_channel_videos(channel_id, max_results=60):
    """
    Fetches a list of videos from a specific YouTube channel.

    Args:
    channel_id (str): The ID of the YouTube channel.
    max_results (int): Maximum number of video results to return.

    Returns:
    list: A list of dictionaries containing video information.
    """
    youtube = build("youtube", "v3", developerKey=API_KEY)

    # Get uploads playlist ID
    channel_response = (
        youtube.channels().list(part="contentDetails", id=channel_id).execute()
    )

    uploads_playlist_id = channel_response["items"][0]["contentDetails"][
        "relatedPlaylists"
    ]["uploads"]

    # Fetch videos from uploads playlist
    videos = []
    next_page_token = None

    while True:
        playlist_response = (
            youtube.playlistItems()
            .list(
                part="snippet",
                playlistId=uploads_playlist_id,
                maxResults=min(50, max_results - len(videos)),
                pageToken=next_page_token,
            )
            .execute()
        )

        videos.extend(playlist_response["items"])
        next_page_token = playlist_response.get("nextPageToken")

        if next_page_token is None or len(videos) >= max_results:
            break

    return videos


def main():
    # Replace with the desired channel ID
    channel_id = "UCLjs_2pd3xMYTP1mo6jTy9A" # border0 channel here
    videos = fetch_channel_videos(channel_id)

    for video in videos:
        print(f"Title: {video['snippet']['title']}")
        print(f"Video ID: {video['snippet']['resourceId']['videoId']}")
        print(f"Published at: {video['snippet']['publishedAt']}")
        print("---")


# UPDATED: Corrected the if statement
if __name__ == "__main__":
    main()
