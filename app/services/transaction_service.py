"""Transaction management service"""
from typing import Dict, List, Optional
from datetime import datetime
import uuid
from app.models.schemas import (
    Transaction, 
    TransactionRequest, 
    TransactionStatus, 
    TransactionType
)
from app.services.coin_service import coin_service
from app.core.config import settings


class TransactionService:
    """Service for managing transactions"""
    
    def __init__(self):
        # In-memory storage (replace with database in production)
        self.transactions: Dict[str, Transaction] = {}
    
    def _calculate_fee(self, amount: float) -> float:
        """Calculate transaction fee"""
        return amount * (settings.TRANSACTION_FEE_PERCENT / 100)
    
    def _generate_transaction_id(self) -> str:
        """Generate unique transaction ID"""
        return f"txn_{uuid.uuid4().hex[:12]}"
    
    async def create_transaction(
        self, 
        request: TransactionRequest
    ) -> Transaction:
        """
        Create a new transaction
        
        Args:
            request: Transaction request data
            
        Returns:
            Created transaction
        """
        # Validate amount
        if request.amount < settings.MIN_TRANSACTION_AMOUNT:
            raise ValueError(
                f"Amount below minimum. Minimum: {settings.MIN_TRANSACTION_AMOUNT}"
            )
        
        if request.amount > settings.MAX_TRANSACTION_AMOUNT:
            raise ValueError(
                f"Amount exceeds maximum. Maximum: {settings.MAX_TRANSACTION_AMOUNT}"
            )
        
        # Calculate fee
        fee = self._calculate_fee(request.amount)
        
        # Create transaction
        transaction = Transaction(
            transaction_id=self._generate_transaction_id(),
            from_user=request.from_user,
            to_user=request.to_user,
            amount=request.amount,
            transaction_type=request.transaction_type,
            status=TransactionStatus.PENDING,
            fee=fee,
            timestamp=datetime.utcnow(),
            metadata=request.metadata
        )
        
        # Store transaction
        self.transactions[transaction.transaction_id] = transaction
        
        return transaction
    
    async def execute_transaction(self, transaction_id: str) -> Transaction:
        """
        Execute a pending transaction
        
        Args:
            transaction_id: Transaction identifier
            
        Returns:
            Updated transaction
        """
        if transaction_id not in self.transactions:
            raise ValueError(f"Transaction not found: {transaction_id}")
        
        transaction = self.transactions[transaction_id]
        
        if transaction.status != TransactionStatus.PENDING:
            raise ValueError(
                f"Transaction already processed. Status: {transaction.status}"
            )
        
        try:
            # Execute based on transaction type
            if transaction.transaction_type == TransactionType.SEND:
                await coin_service.transfer_coins(
                    transaction.from_user,
                    transaction.to_user,
                    transaction.amount,
                    transaction.fee
                )
            
            elif transaction.transaction_type == TransactionType.MINT:
                await coin_service.mint_coins(
                    transaction.to_user,
                    transaction.amount
                )
            
            elif transaction.transaction_type == TransactionType.BURN:
                await coin_service.burn_coins(
                    transaction.from_user,
                    transaction.amount
                )
            
            elif transaction.transaction_type == TransactionType.STAKE:
                await coin_service.stake_coins(
                    transaction.from_user,
                    transaction.amount
                )
            
            elif transaction.transaction_type == TransactionType.UNSTAKE:
                await coin_service.unstake_coins(
                    transaction.from_user,
                    transaction.amount
                )
            
            # Mark as completed
            transaction.status = TransactionStatus.COMPLETED
            
        except Exception as e:
            # Mark as failed
            transaction.status = TransactionStatus.FAILED
            if transaction.metadata is None:
                transaction.metadata = {}
            transaction.metadata["error"] = str(e)
            raise
        
        finally:
            self.transactions[transaction_id] = transaction
        
        return transaction
    
    async def get_transaction(self, transaction_id: str) -> Optional[Transaction]:
        """Get transaction by ID"""
        return self.transactions.get(transaction_id)
    
    async def get_user_transactions(
        self, 
        user_id: str, 
        limit: int = 100
    ) -> List[Transaction]:
        """Get all transactions for a user"""
        user_transactions = [
            txn for txn in self.transactions.values()
            if txn.from_user == user_id or txn.to_user == user_id
        ]
        
        # Sort by timestamp (newest first)
        user_transactions.sort(key=lambda x: x.timestamp, reverse=True)
        
        return user_transactions[:limit]
    
    async def get_pending_transactions(self) -> List[Transaction]:
        """Get all pending transactions"""
        return [
            txn for txn in self.transactions.values()
            if txn.status == TransactionStatus.PENDING
        ]
    
    async def cancel_transaction(self, transaction_id: str) -> Transaction:
        """Cancel a pending transaction"""
        if transaction_id not in self.transactions:
            raise ValueError(f"Transaction not found: {transaction_id}")
        
        transaction = self.transactions[transaction_id]
        
        if transaction.status != TransactionStatus.PENDING:
            raise ValueError(
                f"Cannot cancel transaction with status: {transaction.status}"
            )
        
        transaction.status = TransactionStatus.CANCELLED
        self.transactions[transaction_id] = transaction
        
        return transaction
    
    async def get_transaction_stats(self) -> Dict:
        """Get transaction statistics"""
        total = len(self.transactions)
        pending = sum(
            1 for txn in self.transactions.values() 
            if txn.status == TransactionStatus.PENDING
        )
        completed = sum(
            1 for txn in self.transactions.values() 
            if txn.status == TransactionStatus.COMPLETED
        )
        failed = sum(
            1 for txn in self.transactions.values() 
            if txn.status == TransactionStatus.FAILED
        )
        
        total_volume = sum(
            txn.amount for txn in self.transactions.values()
            if txn.status == TransactionStatus.COMPLETED
        )
        
        return {
            "total_transactions": total,
            "pending": pending,
            "completed": completed,
            "failed": failed,
            "total_volume": total_volume
        }


# Singleton instance
transaction_service = TransactionService()
