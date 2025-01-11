import aiohttp
import json
import logging
import os

# Configure logging
logging.basicConfig(
    filename='logs.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


class DuckDuckGoChatAPI:
 
    def __init__(self, user_id : str , model = "gpt-4o-mini"):
        self.base_url = "https://duckduckgo.com/duckchat/v1"
        self.x_vqd = None
        self.user_id = user_id
        self.model = model
        self.data = self.load_user_data()


    def load_user_data(self):
        """Load user data from users.json."""
        with open("users.json", "r") as file:
            users = json.load(file)
            return users


    def save_user_data(self):
        """Save user data to users.json."""
        with open("users.json", "r+") as file:
            json.dump(self.data, file, indent=4)
            file.truncate()


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
                    self.data[self.user_id]["x_vqd"] = self.x_vqd  # ذخیره x_vqd در داده‌های کاربر
                    self.save_user_data()  # ذخیره داده‌های کاربر در فایل JSON
                    logging.info(f"Received x-vqd: {self.x_vqd}")
                else:
                    logging.error("Failed to get status: %s", response.status)


    async def send_chat(self, user_message):
        """Send a chat message to the API and return the response as a single string."""
        if not self.x_vqd:
            # اگر x_vqd ذخیره‌شده وجود دارد، از آن استفاده کنید
            if self.data[self.user_id].get("x_vqd"):
                self.x_vqd = self.data[self.user_id]["x_vqd"]
            else:
                logging.warning("x-vqd is not set. Please call get_status() first.")
                return

        if self.data[self.user_id]["memory"]:
            self.data[self.user_id]["messages"].append({"role": "user", "content": user_message})
            payload = {
            "model": self.data[self.user_id]["selected_model"],
            "messages": self.data[self.user_id]["messages"]
            }
        else:
            payload = {
                "model": self.data[self.user_id]["selected_model"],
                "messages": [{"role": "user", "content": user_message}]
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
                    self.data[self.user_id]["x_vqd"] = self.x_vqd  # به‌روزرسانی x_vqd در داده‌های کاربر
                    full_response = ""
                    async for line in response.content:
                        decoded_line = line.decode('utf-8')
                        if decoded_line.startswith("data:"):
                            json_data = decoded_line[5:].strip()
                            try:
                                if json_data == "[DONE][LIMIT_CONVERSATION]":
                                    full_response += "\n\n\n the limit of this conversation has been reached. please start a new one."
                                else:
                                    message_data = json.loads(json_data)
                                    if "message" in message_data:
                                        full_response += message_data["message"]
                            except json.JSONDecodeError:
                                logging.error("Failed to decode JSON: %s", json_data)
                    self.data[self.user_id]["messages"].append({"role": "assistant", "content": full_response.strip()})
                    self.save_user_data()  # ذخیره‌سازی داده‌های کاربر
                    return full_response.strip()
                else:
                    logging.error("Failed to send chat: %s", response.status)