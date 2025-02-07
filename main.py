from telegram.ext import Application
from tg.handlers import CommandHandlers, MessageHandlers, CallbackHandlers

ptb = (
    Application.builder()
    .token("")
    .build()
)
def main():
    CommandHandler = CommandHandlers()
    MessageHandler = MessageHandlers()
    CallbackHandler = CallbackHandlers()

    for handler in CommandHandler.get_handlers():
        ptb.add_handler(handler)
    for handler in MessageHandler.get_handlers():
        ptb.add_handler(handler)
    for handler in CallbackHandler.get_handlers():
        ptb.add_handler(handler)
    
    ptb.run_polling()

if __name__ == '__main__':
    main()