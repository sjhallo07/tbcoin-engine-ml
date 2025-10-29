"""Coin management endpoints"""
from fastapi import APIRouter, HTTPException, Query
from typing import Dict
from app.models.schemas import CoinBalance
from app.services.coin_service import coin_service

router = APIRouter()


@router.get("/coins/balance/{user_id}", response_model=CoinBalance)
async def get_balance(user_id: str):
    """
    Get user's coin balance
    
    Args:
        user_id: User identifier
        
    Returns:
        User's coin balance
    """
    try:
        balance = await coin_service.get_balance(user_id)
        return balance
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/coins/stake/{user_id}")
async def stake_coins(
    user_id: str,
    amount: float = Query(gt=0, description="Amount to stake")
):
    """
    Stake coins for a user
    
    Args:
        user_id: User identifier
        amount: Amount to stake
        
    Returns:
        Updated balance
    """
    try:
        balance = await coin_service.stake_coins(user_id, amount)
        return {
            "success": True,
            "message": f"Successfully staked {amount} coins",
            "balance": balance
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/coins/unstake/{user_id}")
async def unstake_coins(
    user_id: str,
    amount: float = Query(gt=0, description="Amount to unstake")
):
    """
    Unstake coins for a user
    
    Args:
        user_id: User identifier
        amount: Amount to unstake
        
    Returns:
        Updated balance
    """
    try:
        balance = await coin_service.unstake_coins(user_id, amount)
        return {
            "success": True,
            "message": f"Successfully unstaked {amount} coins",
            "balance": balance
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/coins/mint/{user_id}")
async def mint_coins(
    user_id: str,
    amount: float = Query(gt=0, description="Amount to mint")
):
    """
    Mint new coins to a user (admin operation)
    
    Args:
        user_id: User identifier
        amount: Amount to mint
        
    Returns:
        Updated balance
    """
    try:
        balance = await coin_service.mint_coins(user_id, amount)
        return {
            "success": True,
            "message": f"Successfully minted {amount} coins",
            "balance": balance
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/coins/burn/{user_id}")
async def burn_coins(
    user_id: str,
    amount: float = Query(gt=0, description="Amount to burn")
):
    """
    Burn coins from a user
    
    Args:
        user_id: User identifier
        amount: Amount to burn
        
    Returns:
        Updated balance
    """
    try:
        balance = await coin_service.burn_coins(user_id, amount)
        return {
            "success": True,
            "message": f"Successfully burned {amount} coins",
            "balance": balance
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/coins/balances", response_model=Dict[str, CoinBalance])
async def get_all_balances():
    """
    Get all user balances (admin operation)
    
    Returns:
        Dictionary of all user balances
    """
    try:
        balances = await coin_service.get_all_balances()
        return balances
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
