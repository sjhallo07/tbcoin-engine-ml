"""Transaction management endpoints"""
from fastapi import APIRouter, HTTPException, Query
from typing import List
from app.models.schemas import Transaction, TransactionRequest
from app.services.transaction_service import transaction_service

router = APIRouter()


@router.post("/transactions", response_model=Transaction)
async def create_transaction(request: TransactionRequest):
    """
    Create a new transaction
    
    Args:
        request: Transaction request data
        
    Returns:
        Created transaction
    """
    try:
        transaction = await transaction_service.create_transaction(request)
        return transaction
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/transactions/{transaction_id}/execute", response_model=Transaction)
async def execute_transaction(transaction_id: str):
    """
    Execute a pending transaction
    
    Args:
        transaction_id: Transaction identifier
        
    Returns:
        Updated transaction
    """
    try:
        transaction = await transaction_service.execute_transaction(transaction_id)
        return transaction
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/transactions/{transaction_id}", response_model=Transaction)
async def get_transaction(transaction_id: str):
    """
    Get transaction by ID
    
    Args:
        transaction_id: Transaction identifier
        
    Returns:
        Transaction details
    """
    transaction = await transaction_service.get_transaction(transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction


@router.get("/transactions/user/{user_id}", response_model=List[Transaction])
async def get_user_transactions(
    user_id: str,
    limit: int = Query(default=100, le=1000, description="Maximum number of transactions")
):
    """
    Get all transactions for a user
    
    Args:
        user_id: User identifier
        limit: Maximum number of transactions to return
        
    Returns:
        List of user transactions
    """
    try:
        transactions = await transaction_service.get_user_transactions(user_id, limit)
        return transactions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/transactions/pending/all", response_model=List[Transaction])
async def get_pending_transactions():
    """
    Get all pending transactions
    
    Returns:
        List of pending transactions
    """
    try:
        transactions = await transaction_service.get_pending_transactions()
        return transactions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/transactions/{transaction_id}/cancel", response_model=Transaction)
async def cancel_transaction(transaction_id: str):
    """
    Cancel a pending transaction
    
    Args:
        transaction_id: Transaction identifier
        
    Returns:
        Cancelled transaction
    """
    try:
        transaction = await transaction_service.cancel_transaction(transaction_id)
        return transaction
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/transactions/stats/summary")
async def get_transaction_stats():
    """
    Get transaction statistics
    
    Returns:
        Transaction statistics
    """
    try:
        stats = await transaction_service.get_transaction_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/transactions/quick-send")
async def quick_send(
    from_user: str = Query(..., description="Sender user ID"),
    to_user: str = Query(..., description="Receiver user ID"),
    amount: float = Query(..., gt=0, description="Amount to send")
):
    """
    Quick send coins (create and execute in one call)
    
    Args:
        from_user: Sender user ID
        to_user: Receiver user ID
        amount: Amount to send
        
    Returns:
        Completed transaction
    """
    try:
        # Create transaction
        request = TransactionRequest(
            from_user=from_user,
            to_user=to_user,
            amount=amount
        )
        transaction = await transaction_service.create_transaction(request)
        
        # Execute immediately
        transaction = await transaction_service.execute_transaction(transaction.transaction_id)
        
        return {
            "success": True,
            "message": f"Successfully sent {amount} coins",
            "transaction": transaction
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
