# save_win/endpoints.py

from fastapi import APIRouter
from .db import update_wallet

router = APIRouter(prefix="/save_win", tags=["Save&Win"])


@router.post("/deposit/{user_id}")
def deposit_money(user_id: str, amount: float):
    """
    User deposits money → we save it in Save&Win DB → award tokens.
    This is the ENTRY POINT for the simulator.
    """
    awarded = update_wallet(user_id, amount)

    return {
        "message": "Deposit recorded",
        "userId": user_id,
        "amount": amount,
        "tokens_awarded": awarded
    }
