from fastapi import APIRouter

from app.database.db_Helper import Commute

router = APIRouter(prefix="/employees", tags=["employees"], responses={404: {"description": "Not found"}})


@router.get('')
def get_employees():
    commute = Commute.select(Commute.username, Commute.come_at, Commute.leave_at).dicts().get()
    return commute
