import asyncio
from api import DuckDuckGoChatAPI

async def main():
    api = DuckDuckGoChatAPI()
    api.model = "claude-3-haiku-20240307"
    await api.get_status()  # Get the x-vqd value
    a = await api.send_chat("hello . my name is alex.")  # Send a chat message
    print(a)
    b = await api.send_chat("i am programmer. ")  # Send another chat message
    print(b)
    c = await api.send_chat("do you know what is my job and name?")  # Send another chat message
    print(c)

if __name__ == "__main__":
    asyncio.run(main())