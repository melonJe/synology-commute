from dotenv import load_dotenv
from fastapi import APIRouter

from ..database.db_Helper import Commute

load_dotenv()

router = APIRouter(prefix="/users", tags=["users"], responses={404: {"description": "Not found"}})


@router.get('')
def get_users():
    commute = Commute.select(Commute.username, Commute.come_at, Commute.leave_at).dicts().get()
    return commute
