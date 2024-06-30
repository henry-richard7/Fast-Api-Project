from sqlmodel import Field, SQLModel, create_engine
from dotenv import load_dotenv
from os import getenv

# Loading .env file
load_dotenv()

# Getting mysql configurations
hostname = getenv("hostname")
port = getenv("port")
username = getenv("user")
password = getenv("password")
database = getenv("database")


class TodoItemBase(SQLModel):
    todo_title: str
    todo_description: str
    completed: bool = False


class TodoItem(TodoItemBase, table=True):
    id: int | None = Field(default=None, primary_key=True)


class TodoItemCreate(TodoItemBase):
    pass


class TodoItemUpdate(SQLModel):
    completed: bool = False


class UserBase(SQLModel):
    username: str
    password: str


class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)


class UserCreate(UserBase):
    pass


class DownloadStatus(SQLModel, table=True):
    uuid: str | None = Field(default=None, primary_key=True)
    status: str = "In-Progress"
    file_path: str | None = None


# Making Connection String
connection_string = (
    f"mysql+pymysql://{username}:{password}@{hostname}:{port}/{database}"
)

# Creating Mysql Engine
engine = create_engine(connection_string)


def create_tables():
    # Creating all tables
    SQLModel.metadata.create_all(engine)
