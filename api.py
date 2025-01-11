import aiohttp
import asyncio
import json
import logging

# Configure logging
logging.basicConfig(
    filename='logs.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class DuckDuckGoChatAPI:
    def __init__(self):
        self.base_url = "https://duckduckgo.com/duckchat/v1"
        self.x_vqd = None
        self.messages = []
        self.model = "gpt-4o-mini" # one of these: "gpt-4o-mini", "claude-3-haiku-20240307", "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo", "mistralai/Mixtral-8x7B-Instruct-v0.1"

    async def get_status(self):
        """Send a status request to get the x-vqd value."""
        url = f"{self.base_url}/status"
        headers = {
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9,fa;q=0.8',
            'cache-control': 'no-store',
            'cookie': 'dcm=3; dcs=1',
            'priority': 'u=1, i',
            'referer': 'https://duckduckgo.com/',
            'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'x-vqd-accept': '1'
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    self.x_vqd = response.headers.get("x-vqd-4")
                    logging.info(f"Received x-vqd: {self.x_vqd}")
                else:
                    logging.error("Failed to get status: %s", response.status)

    async def send_chat(self, user_message):
        """Send a chat message to the API and return the response as a single string."""
        if not self.x_vqd:
            logging.warning("x-vqd is not set. Please call get_status() first.")
            return

        self.messages.append({"role": "user", "content": user_message})

        payload = {
            "model": self.model,
            "messages": self.messages
        }

        headers = {
            "accept": "text/event-stream",
            "accept-language": "en-US,en;q=0.9,fa;q=0.8",
            "content-type": "application/json",
            "cookie": "dcm=3; dcs=1",
            "origin": "https://duckduckgo.com",
            "priority": "u=1, i",
            "referer": "https://duckduckgo.com/",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            "x-vqd-4": self.x_vqd
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.base_url}/chat", headers=headers, json=payload) as response:
                if response.status == 200:
                    self.x_vqd = response.headers.get("x-vqd-4")
                    full_response = ""
                    async for line in response.content:
                        decoded_line = line.decode('utf-8')
                        if decoded_line.startswith("data:"):
                            json_data = decoded_line[5:].strip()
                            try:
                                if json_data == "[DONE][LIMIT_CONVERSATION]":
                                    full_response += "محدودیت مکالمه به پایان رسیده و بیشتر از این نمی‌شود ادامه داد."
                                else:
                                    message_data = json.loads(json_data)
                                    if "message" in message_data:
                                        full_response += message_data["message"] + " "
                            except json.JSONDecodeError:
                                logging.error("Failed to decode JSON: %s", json_data)
                    self.messages.append({"role": "assistant", "content": full_response.strip()})
                    return full_response.strip()
                else:
                    logging.error("Failed to send chat: %s", response.status)