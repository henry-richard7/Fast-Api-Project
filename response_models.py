from typing import List
from pydantic import BaseModel


class RegisterResponse(BaseModel):
    status: str = "ok"
    response: str = "User {user_name} is registered"


class YoutubeMusicSearchItem(BaseModel):
    video_id: str
    song_name: str
    artist_name: str
    album_name: str
    art: str


class YoutubeMusicSearchResult(BaseModel):
    success: bool
    results: List[YoutubeMusicSearchItem]


class YoutubeMusicLyricsResult(BaseModel):
    success: bool
    results: str


class YoutubeMusicDirectlinkMeta(BaseModel):
    url: str
    mimeType: str
    bitrate: str | int
    approxDurationMs: str | int


class YoutubeMusicDirectlinkResult(BaseModel):
    success: bool
    results: YoutubeMusicDirectlinkMeta | str


class Mp3DownloadProcessResponse(BaseModel):
    status: str
    uuid: str | None
    message: str
