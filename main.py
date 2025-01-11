import asyncio
from functions.api import DuckDuckGoChatAPI

async def main():
    api = DuckDuckGoChatAPI("2222")
    await api.get_status()  # Get the x-vqd value
    a = await api.send_chat("اسم من علیه و به زبان فارسی صحبت میکنم")  # Send a chat message
    print(a)
    b = await api.send_chat("من برنامه نویس هستم")  # Send another chat message
    print(b)
    c = await api.send_chat("هر چیزی درباره من میدونی رو خلاصه و تیتر وار بیان کن")  # Send another chat message
    print(c)

async def main1():
    api = DuckDuckGoChatAPI("2222")
    a = await api.send_chat("tell me some intresting thing about iran.")  # Send a chat message
    print(a)



if __name__ == "__main__":
    asyncio.run(main1())
    