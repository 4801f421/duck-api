import asyncio
from api import DuckDuckGoChatAPI

async def main():
    api = DuckDuckGoChatAPI()
    await api.get_status()  # Get the x-vqd value
    response = await api.send_chat("سلام")  # Send a chat message
    print(response)

if __name__ == "__main__":
    asyncio.run(main())
