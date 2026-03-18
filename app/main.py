import logging
from fastapi import FastAPI
from app.schemas.user import UserCreateSchema

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Dynamic Validation Pipeline - Modular")


@app.post("/users", response_model=UserCreateSchema)
async def create_user(user: UserCreateSchema):
    """
    POST route accepting the UserCreateSchema payload.
    Will execute the dynamic validation pipeline upon receipt.
    """
    return user
