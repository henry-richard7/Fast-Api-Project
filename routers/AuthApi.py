from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from schemas import User, UserCreate, engine
from sqlmodel import Session, select
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from response_models import RegisterResponse

import secrets

security = HTTPBasic()


def get_session():
    with Session(engine) as session:
        yield session


def verify_credentials(
    credentials: HTTPBasicCredentials = Depends(security),
    session: Session = Depends(get_session),
):
    statement = select(User).where(User.username == credentials.username)
    user = session.exec(statement).first()
    if not user or not secrets.compare_digest(user.password, credentials.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return user


router = APIRouter()


@router.post("/register", tags=["Basic Auth Endpoint"])
def register_user(
    *,
    user: UserCreate,
    session: Session = Depends(get_session),
) -> RegisterResponse:
    user_present = session.exec(
        select(User).where(User.username == user.username)
    ).first()

    if user_present:
        raise HTTPException(status_code=400, detail="Username already registered.")
    db_user_item = User.model_validate(user)
    session.add(db_user_item)
    session.commit()
    session.refresh(db_user_item)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=RegisterResponse(
            status="ok", response=f"User {user.username} is registered."
        ).model_dump(),
    )


@router.get("/check", tags=["Basic Auth Endpoint"])
def check_auth(
    *,
    session: Session = Depends(get_session),
    user: User = Depends(verify_credentials),
) -> dict:
    return {"status": "OK", "messsage": "Session Is Authorized."}
