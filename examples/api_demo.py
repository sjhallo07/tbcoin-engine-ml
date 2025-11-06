#!/usr/bin/env python3
"""
Example script demonstrating TB Coin Engine ML API usage
"""
import asyncio
import httpx

API_BASE_URL = "http://localhost:8000/api/v1"


async def check_health():
    """Check API health"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_BASE_URL}/health")
        print("🏥 Health Check:", response.json())
        return response.json()


async def get_balance(user_id: str):
    """Get user balance"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_BASE_URL}/coins/balance/{user_id}")
        print(f"💰 Balance for {user_id}:", response.json())
        return response.json()


async def mint_coins(user_id: str, amount: float):
    """Mint coins to user"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{API_BASE_URL}/coins/mint/{user_id}",
            params={"amount": amount}
        )
        print(f"🪙 Minted {amount} coins to {user_id}:", response.json())
        return response.json()


async def quick_send(from_user: str, to_user: str, amount: float):
    """Quick send coins"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{API_BASE_URL}/transactions/quick-send",
            params={
                "from_user": from_user,
                "to_user": to_user,
                "amount": amount
            }
        )
        print(f"💸 Sent {amount} from {from_user} to {to_user}:", response.json())
        return response.json()


async def get_recommendations(user_id: str, context: str = ""):
    """Get ML recommendations"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{API_BASE_URL}/ml/recommend",
            params={
                "user_id": user_id,
                "context": context
            }
        )
        print(f"🤖 Recommendations for {user_id}:", response.json())
        return response.json()


async def main():
    """Main demonstration"""
    print("=" * 60)
    print("TB Coin Engine ML - API Demo")
    print("=" * 60)
    
    print("\n1️⃣ Checking API Health...")
    await check_health()
    
    print("\n2️⃣ Minting Coins...")
    await mint_coins("alice", 1000)
    await mint_coins("bob", 500)
    
    print("\n3️⃣ Checking Balances...")
    await get_balance("alice")
    await get_balance("bob")
    
    print("\n4️⃣ Getting AI Recommendations...")
    await get_recommendations("alice", "I want to optimize my coin holdings")
    
    print("\n5️⃣ Quick Send Transaction...")
    await quick_send("alice", "bob", 50)
    
    print("\n6️⃣ Updated Balances...")
    await get_balance("alice")
    await get_balance("bob")
    
    print("\n" + "=" * 60)
    print("✅ Demo Complete!")
    print("=" * 60)


if __name__ == "__main__":
    print("Make sure the API server is running on http://localhost:8000")
    print("Start it with: python main.py\n")
    
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Make sure the API server is running!")
