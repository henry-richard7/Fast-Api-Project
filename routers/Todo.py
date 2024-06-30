from typing import List
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from schemas import TodoItem, TodoItemCreate, TodoItemUpdate, engine
from sqlmodel import Session, select


router = APIRouter()


def get_session():
    with Session(engine) as session:
        yield session


@router.post("/create", tags=["Todo Endpoint"])
def create_todo(
    *,
    session: Session = Depends(get_session),
    todo_item: TodoItemCreate,
) -> TodoItemCreate:
    """
    Create a Todo Item
    """

    db_todo_item = TodoItem.model_validate(todo_item)
    session.add(db_todo_item)
    session.commit()
    session.refresh(db_todo_item)
    return db_todo_item


@router.get("/items", tags=["Todo Endpoint"])
def list_items(*, session: Session = Depends(get_session)) -> List[TodoItem]:
    """
    Shows all Todo Items in DB.
    """

    heroes = session.exec(select(TodoItem)).all()
    return heroes


@router.delete("/delete/{todo_id}", tags=["Todo Endpoint"])
def delete_item(*, session: Session = Depends(get_session), todo_id: int):
    """
    Deletes an Todo Item for given Todo Item id
    """

    todo_item = session.get(TodoItem, todo_id)

    if not todo_item:
        raise HTTPException(
            status_code=404, detail=f"Todo Item with ID: {todo_id} Not Found"
        )
    session.delete(todo_item)
    session.commit()
    return JSONResponse(
        status_code=200,
        content={
            "success": True,
            "response": f"Todo Item with ID: {todo_id} is deleted.",
        },
    )


@router.patch("/update/{todo_id}", tags=["Todo Endpoint"])
def update_todo_item(
    *,
    session: Session = Depends(get_session),
    todo_id: int,
    completed: TodoItemUpdate,
) -> TodoItemCreate:
    with Session(engine) as session:
        # Sellecting Todo Item for given todo id
        todo_item = session.get(TodoItem, todo_id)

        # If no todo item found for given id raise 404
        if not todo_item:
            raise HTTPException(
                status_code=404, detail=f"Todo Item with ID: {todo_id} Not Found"
            )

        # Dumping the TodoItemUpdate Model as dict
        db_todo_item = completed.model_dump(exclude_unset=True)

        # Update the value
        todo_item.sqlmodel_update(db_todo_item)
        session.add(todo_item)
        session.commit()
        session.refresh(todo_item)
        return todo_item
