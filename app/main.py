import logging
from fastapi import BackgroundTasks, FastAPI
from app.schemas.user import UserCreateSchema
from app.services.elastic import send_to_elastic

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Dynamic Validation Pipeline - Modular")


@app.post("/users", response_model=UserCreateSchema)
async def create_user(user: UserCreateSchema, background_tasks: BackgroundTasks):
    """
    POST route accepting the UserCreateSchema payload.
    Will execute the dynamic validation pipeline upon receipt.
    """
    if user._soft_launch_report:
        background_tasks.add_task(
            send_to_elastic,
            user._soft_launch_report["schema"],
            user._soft_launch_report["errors"],
        )
    return user
