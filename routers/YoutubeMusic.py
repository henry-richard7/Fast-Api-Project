from uuid import uuid4
from fastapi import APIRouter, status, BackgroundTasks, Depends, HTTPException
from fastapi.responses import JSONResponse, Response, StreamingResponse, FileResponse
from modules import YoutubeMusicApi, download_song
from schemas import DownloadStatus, engine
from sqlmodel import Session, select
from request_models import (
    YoutubeMusicSearchRequest,
)

from response_models import (
    YoutubeMusicSearchResult,
    YoutubeMusicLyricsResult,
    YoutubeMusicDirectlinkResult,
    Mp3DownloadProcessResponse,
)

router = APIRouter()
youtube_music_api = YoutubeMusicApi()


def get_session():
    with Session(engine) as session:
        yield session


@router.post("/search", tags=["Youtube Music"])
def search_music(
    youtube_search_request: YoutubeMusicSearchRequest,
) -> YoutubeMusicSearchResult:
    search_result = youtube_music_api.search(**youtube_search_request.model_dump())

    response = YoutubeMusicSearchResult(**search_result)
    return response


@router.get("/lyrics", tags=["Youtube Music"])
def get_lyrics(
    video_id: str,
) -> YoutubeMusicLyricsResult:
    lyrics_result = youtube_music_api.fetch_lyrics(video_id)

    response = YoutubeMusicLyricsResult(**lyrics_result)

    if not response.success:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=response.model_dump(),
        )
    return response


@router.get("/direct_link", tags=["Youtube Music"])
def get_direct_link(video_id: str) -> YoutubeMusicDirectlinkResult:
    direct_link_result = youtube_music_api.get_direct_link(video_id)

    response = YoutubeMusicDirectlinkResult(**direct_link_result)
    if not response.success:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=response.model_dump(),
        )
    return response


@router.get("/direct_stream", tags=["Youtube Music"])
def get_direct_response(video_id: str) -> StreamingResponse:
    direct_link_result = youtube_music_api.get_direct_link(video_id)

    response = YoutubeMusicDirectlinkResult(**direct_link_result)
    if not response.success:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=response.model_dump(),
        )
    return StreamingResponse(
        status_code=status.HTTP_200_OK,
        media_type=response.results.mimeType,
        content=response.results.url,
    )


def download_task(video_id: str, uuid: str, session: Session):
    init_state = DownloadStatus(
        uuid=uuid,
        status="In-Progress",
        file_path=None,
    )

    session.add(init_state)
    session.commit()
    session.refresh(init_state)

    response = download_song(video_id=video_id)

    if response["success"]:
        final_state = DownloadStatus(
            uuid=uuid,
            status="Completed",
            file_path=response["file_path"],
        )

        previous_state = session.get(DownloadStatus, uuid)

        final_state_dict = final_state.model_dump(exclude_unset=True)
        previous_state.sqlmodel_update(final_state_dict)
        session.add(previous_state)
        session.commit()
        session.refresh(previous_state)
    else:
        final_state = DownloadStatus(
            uuid=uuid,
            status="Failed",
            file_path=None,
        )

        previous_state = session.get(DownloadStatus, uuid)

        final_state_dict = final_state.model_dump(exclude_unset=True)
        previous_state.sqlmodel_update(final_state_dict)
        session.add(previous_state)
        session.commit()
        session.refresh(previous_state)


@router.get("/process_mp3", tags=["Youtube Music"])
async def process_mp3(
    video_id: str,
    download_task_: BackgroundTasks,
    session: Session = Depends(get_session),
) -> Mp3DownloadProcessResponse:
    uuid = str(uuid4())
    download_task_.add_task(download_task, video_id, uuid, session)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=Mp3DownloadProcessResponse(
            status="OK", uuid=uuid, message="Download Started."
        ).model_dump(),
    )


@router.get("/download_status", tags=["Youtube Music"])
def get_download_status(
    uuid: str,
    session: Session = Depends(get_session),
) -> DownloadStatus:
    download_item = session.exec(
        select(DownloadStatus).where(DownloadStatus.uuid == uuid)
    ).first()

    return download_item


@router.get("/download_mp3/{uuid}", tags=["Youtube Music"])
def download_mp3(uuid: str, session: Session = Depends(get_session)) -> FileResponse:
    download_item = session.exec(
        select(DownloadStatus).where(DownloadStatus.uuid == uuid)
    ).first()

    if not download_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="There is no task for given UUID.",
        )

    file_path = download_item.file_path
    file_name = file_path.replace("downloads/", "")

    return FileResponse(path=file_path, filename=file_name, media_type="audio/mpeg")
