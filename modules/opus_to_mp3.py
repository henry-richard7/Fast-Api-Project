import httpx

from ffmpeg import FFmpeg
from io import BytesIO
from mutagen.mp3 import MP3
from mutagen.id3 import TIT2, TPE1, TALB, APIC, USLT, SYLT
import re

from modules import YoutubeMusicApi


def synced_lyrics(artist_name, track_name, album_name, duration):
    duration = duration / 1000
    url = "https://lrclib.net/api/get"
    params = {
        "artist_name": artist_name,
        "track_name": track_name,
        "album_name": album_name,
        "duration": duration,
    }

    response = httpx.get(url=url, params=params).json()
    sync_lyrics = response.get("syncedLyrics")

    if sync_lyrics:
        pattern = re.compile(r"\[(\d+):(\d+\.\d+)\] (.+)")
        lyrics = []
        for line in sync_lyrics.split("\n"):
            match = pattern.match(line)
            if match:
                minutes = int(match.group(1))
                seconds = float(match.group(2))
                text = match.group(3)
                timestamp = int(
                    (minutes * 60 + seconds) * 1000
                )  # Convert to milliseconds
                lyrics.append((text, timestamp))
        return lyrics

    else:
        return None


def convert_to_mp3(file_bytes: bytes) -> bytes:
    bytes_io = BytesIO(file_bytes)

    process = FFmpeg().input("pipe:0").output("pipe:1", f="mp3")
    raw_mp3 = process.execute(bytes_io)

    return raw_mp3


def add_meta_data(
    raw_mp3: bytes,
    song_name: str,
    artist_name: str,
    album_name: str,
    art: str,
    lyrics: str = None,
    synced_lyrics=None,
) -> BytesIO:
    muta_input = BytesIO(raw_mp3)

    audio = MP3(muta_input)

    audio["TIT2"] = TIT2(encoding=3, text=song_name)
    audio["TPE1"] = TPE1(encoding=3, text=artist_name)
    audio["TALB"] = TALB(encoding=3, text=album_name)
    cover_image_data = httpx.get(art).content

    if lyrics is not None:
        audio["USLT"] = USLT(
            encoding=3,
            lang="eng",
            text=lyrics,
        )

    if synced_lyrics:

        audio["SYLT"] = SYLT(
            encoding=3,  # 3 is for utf-8
            lang="eng",  # Language
            format=2,  # 2 is for milliseconds
            type=1,  # 1 is for lyrics
            text=synced_lyrics,
        )

    audio["APIC"] = APIC(
        encoding=3,  # 3 is for utf-8
        mime="image/jpeg",  # image mime type
        type=3,  # 3 is for the cover image
        desc="Cover",
        data=cover_image_data,
    )

    audio.save(muta_input)

    return muta_input


def download_song(video_id):
    youtube_api = YoutubeMusicApi()

    song_meta = youtube_api.song(video_id=video_id)
    direct_link_response = youtube_api.get_direct_link(video_id=video_id)

    duration = eval(direct_link_response["results"]["approxDurationMs"])
    direct_link = direct_link_response["results"]["url"]

    non_sync_lyrics = youtube_api.fetch_lyrics(video_id=video_id)
    synced_lyrics_ = synced_lyrics(
        artist_name=song_meta["artist_name"],
        track_name=song_meta["song_name"],
        album_name=song_meta["album_name"],
        duration=duration,
    )

    dl = 0
    download_opus = []
    with httpx.stream("GET", direct_link) as response:
        total_length = int(response.headers.get("content-length", 0))
        for chunk in response.iter_bytes():
            dl += len(chunk)
            download_opus.append(chunk)
            completed_percentage = round((dl / total_length) * 100, 2)

    download_opus = b"".join(download_opus)
    raw_mp3 = convert_to_mp3(download_opus)

    meta_added_mp3 = add_meta_data(
        raw_mp3,
        song_name=song_meta["song_name"],
        art=song_meta["art"],
        artist_name=song_meta["artist_name"],
        album_name=song_meta["album_name"],
        synced_lyrics=synced_lyrics_,
        lyrics=non_sync_lyrics.get('results') if non_sync_lyrics["success"] else None,
    )

    file_path = f"downloads/{song_meta["song_name"]}.mp3"
    
    try:
        with open(file_path, "wb") as file:
            file.write(meta_added_mp3.getvalue())
            
        print("[*] Song converted & Saved Successfully.")

        return {
            "success":True,
            "file_path":file_path
        }
        
        
    
    except Exception as e:
        print(f"[!] Song Converstion Failed with Exception {e}.")
        return {
            "success":False,
            "file_path":None
        }
    
