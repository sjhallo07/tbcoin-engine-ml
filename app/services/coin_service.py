"""Coin management service"""
from typing import Dict, Optional
from datetime import datetime
from app.models.schemas import CoinBalance
from app.core.config import settings


class CoinService:
    """Service for managing coin balances and operations"""
    
    def __init__(self):
        # In-memory storage (replace with database in production)
        self.balances: Dict[str, CoinBalance] = {}
        self._initialize_system_account()
    
    def _initialize_system_account(self):
        """Initialize system account with initial supply"""
        self.balances["system"] = CoinBalance(
            user_id="system",
            balance=settings.INITIAL_COIN_SUPPLY,
            staked_balance=0,
            last_updated=datetime.utcnow()
        )
    
    async def get_balance(self, user_id: str) -> CoinBalance:
        """Get user's coin balance"""
        if user_id not in self.balances:
            # Create new account with zero balance
            self.balances[user_id] = CoinBalance(
                user_id=user_id,
                balance=0,
                staked_balance=0
            )
        
        return self.balances[user_id]
    
    async def update_balance(
        self, 
        user_id: str, 
        amount: float, 
        operation: str = "add"
    ) -> CoinBalance:
        """
        Update user's coin balance
        
        Args:
            user_id: User identifier
            amount: Amount to add or subtract
            operation: 'add' or 'subtract'
            
        Returns:
            Updated balance
        """
        balance = await self.get_balance(user_id)
        
        if operation == "add":
            balance.balance += amount
        elif operation == "subtract":
            if balance.balance < amount:
                raise ValueError(f"Insufficient balance. Available: {balance.balance}, Required: {amount}")
            balance.balance -= amount
        else:
            raise ValueError(f"Invalid operation: {operation}")
        
        balance.last_updated = datetime.utcnow()
        self.balances[user_id] = balance
        
        return balance
    
    async def stake_coins(self, user_id: str, amount: float) -> CoinBalance:
        """
        Stake coins for the user
        
        Args:
            user_id: User identifier
            amount: Amount to stake
            
        Returns:
            Updated balance
        """
        balance = await self.get_balance(user_id)
        
        if balance.balance < amount:
            raise ValueError(f"Insufficient balance for staking. Available: {balance.balance}")
        
        balance.balance -= amount
        balance.staked_balance += amount
        balance.last_updated = datetime.utcnow()
        
        self.balances[user_id] = balance
        return balance
    
    async def unstake_coins(self, user_id: str, amount: float) -> CoinBalance:
        """
        Unstake coins for the user
        
        Args:
            user_id: User identifier
            amount: Amount to unstake
            
        Returns:
            Updated balance
        """
        balance = await self.get_balance(user_id)
        
        if balance.staked_balance < amount:
            raise ValueError(f"Insufficient staked balance. Available: {balance.staked_balance}")
        
        balance.staked_balance -= amount
        balance.balance += amount
        balance.last_updated = datetime.utcnow()
        
        self.balances[user_id] = balance
        return balance
    
    async def mint_coins(self, user_id: str, amount: float) -> CoinBalance:
        """
        Mint new coins to a user (admin operation)
        
        Args:
            user_id: User identifier
            amount: Amount to mint
            
        Returns:
            Updated balance
        """
        # Check system supply
        system_balance = await self.get_balance("system")
        
        if system_balance.balance < amount:
            raise ValueError("Insufficient system supply for minting")
        
        # Transfer from system to user
        await self.update_balance("system", amount, "subtract")
        return await self.update_balance(user_id, amount, "add")
    
    async def burn_coins(self, user_id: str, amount: float) -> CoinBalance:
        """
        Burn coins from a user
        
        Args:
            user_id: User identifier
            amount: Amount to burn
            
        Returns:
            Updated balance
        """
        balance = await self.get_balance(user_id)
        
        if balance.balance < amount:
            raise ValueError(f"Insufficient balance for burning. Available: {balance.balance}")
        
        # Remove from circulation
        await self.update_balance(user_id, amount, "subtract")
        
        # Return to system (optional, depending on tokenomics)
        # await self.update_balance("system", amount, "add")
        
        return await self.get_balance(user_id)
    
    async def transfer_coins(
        self, 
        from_user: str, 
        to_user: str, 
        amount: float,
        fee: float = 0
    ) -> tuple[CoinBalance, CoinBalance]:
        """
        Transfer coins between users
        
        Args:
            from_user: Sender user ID
            to_user: Receiver user ID
            amount: Amount to transfer
            fee: Transaction fee
            
        Returns:
            Tuple of (sender_balance, receiver_balance)
        """
        # Validate sender balance
        sender_balance = await self.get_balance(from_user)
        total_deduction = amount + fee
        
        if sender_balance.balance < total_deduction:
            raise ValueError(
                f"Insufficient balance. Available: {sender_balance.balance}, "
                f"Required: {total_deduction} (amount: {amount}, fee: {fee})"
            )
        
        # Perform transfer
        await self.update_balance(from_user, total_deduction, "subtract")
        await self.update_balance(to_user, amount, "add")
        
        # Fee goes to system
        if fee > 0:
            await self.update_balance("system", fee, "add")
        
        return (
            await self.get_balance(from_user),
            await self.get_balance(to_user)
        )
    
    async def get_all_balances(self) -> Dict[str, CoinBalance]:
        """Get all user balances (admin operation)"""
        return self.balances.copy()


# Singleton instance
coin_service = CoinService()
