from contextlib import asynccontextmanager
from telegram import Update
from telegram.ext import Application
from handlers import CommandHandlers, MessageHandlers
from http import HTTPStatus
from fastapi import FastAPI, Request, Response

ptb = (
    Application.builder()
    .updater(None)
    .token("<your-bot-token>")
    .read_timeout(7)
    .get_updates_read_timeout(42)
    .build()
)


@asynccontextmanager
async def lifespan(_: FastAPI):
    await ptb.bot.setWebhook("<your-webhook-url>")
    async with ptb:
        await ptb.start()
        yield
        await ptb.stop()


app = FastAPI(lifespan=lifespan)

@app.post("/")
async def process_update(request: Request):
    req = await request.json()
    update = Update.de_json(req, ptb.bot)
    await ptb.process_update(update)
    return Response(status_code=HTTPStatus.OK)


def main():
    CommandHandler = CommandHandlers()
    MessageHandler = MessageHandlers()

    for handler in CommandHandler.get_handlers():
        ptb.add_handler(handler)
    for handler in MessageHandler.get_handlers():
        ptb.add_handler(handler)

if __name__ == '__main__':
    main()