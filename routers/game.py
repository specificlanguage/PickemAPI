from fastapi import APIRouter, Depends, HTTPException

router = APIRouter(
    prefix="/games",
    tags=["games"],
    dependencies=[],
    responses={404: {"message": "Not found"}}
)

@router.get("/{id}")
async def get_game(id: str):
    int(id)