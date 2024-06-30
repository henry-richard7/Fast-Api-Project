from pydantic import BaseModel


class YoutubeMusicSearchRequest(BaseModel):
    query: str = "IU"


class YoutubeMusicLyricsRequest(BaseModel):
    video_id: str = "Wu5FY8J6P8Q"


class YoutubeMusicDirectLinkRequest(BaseModel):
    video_id: str = "Wu5FY8J6P8Q"
