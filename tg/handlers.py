from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from texts import START_MESSAGE, HELP_MESSAGE
from functions.api import DuckDuckGoChatAPI


MODEL_SYNONYMS = {
    "model_gpt4o": "gpt-4o-mini",
    "model_claude3": "claude-3-haiku-20240307",
    "model_llama31": "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
    "model_mixtral": "mistralai/Mixtral-8x7B-Instruct-v0.1",
}


class CommandHandlers:

    def __init__(self):
        self.handlers = [
            CommandHandler('start', self.start),
            CommandHandler('help', self.help),
            CommandHandler('setting', self.setting)
        ]


    async def start(self, update: Update, context: CallbackContext):
        user_id = str(update.effective_user.id)
        api = DuckDuckGoChatAPI(user_id=user_id)

        if user_id not in api.data:
            print("User not found")
            api.data[user_id] = {
                "selected_model": "gpt-4o-mini",
                "messages": [],
                "memory": True,
                "x_vqd": None
            }
            api.save_user_data()

        await update.message.reply_text(START_MESSAGE)


    async def help(self, update: Update, context: CallbackContext):
        await update.message.reply_text(HELP_MESSAGE)


    async def setting(self, update: Update, context: CallbackContext):
        user_id = str(update.effective_user.id)
        api = DuckDuckGoChatAPI(user_id=user_id)
    
        # بررسی وضعیت مموری
        memory_status = api.data[user_id].get(user_id, {}).get("memory", True)
        memory_text = "Memory: Enabled✅" if memory_status else "Memory: Disabled❌"
    
        # ایجاد اینلاین کیبورد
        keyboard = [
            [
                InlineKeyboardButton("GPT-4o", callback_data="model_gpt4o"),
                InlineKeyboardButton("Claude 3", callback_data="model_claude3"),
            ],
            [
                InlineKeyboardButton("Llama 3.1", callback_data="model_llama31"),
                InlineKeyboardButton("Mixtral", callback_data="model_mixtral"),
            ],
            [
                InlineKeyboardButton(memory_text, callback_data="toggle_memory"),
            ],
        ]
    
        reply_markup = InlineKeyboardMarkup(keyboard)
    
        # ارسال پیام با اینلاین کیبورد
        await update.message.reply_text("Please choose a model or toggle memory:", reply_markup=reply_markup)

    def get_handlers(self):
        return self.handlers


class MessageHandlers:

    def __init__(self):
        self.handlers = [
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.chat)
        ]


    async def chat(self, update: Update, context: CallbackContext):
        message = update.message.text
        if message.startswith('gpt'):
            message = message[3:].strip()
            user_id = str(update.effective_user.id)
            api = DuckDuckGoChatAPI(user_id=user_id)
            
            # بررسی وجود کاربر در داده‌ها
            if user_id not in api.data:
                print("User not found")
                api.data[user_id] = {
                    "selected_model": "gpt-4o-mini",
                    "messages": [],
                    "memory": True,
                    "x_vqd": None
                }
                api.save_user_data()


            if not api.data[user_id].get("memory", True):
                print("Memory is disabled")
                await api.get_status()

            else:
                print("Memory is enabled")
                if not api.data[user_id].get("x_vqd"):
                    print("x_vqd is not available")
                    await api.get_status()
    
            # ارسال پیام و دریافت پاسخ
            response = await api.send_chat(message)
            await update.message.reply_text(response)


    def get_handlers(self):
        return self.handlers


class CallbackHandlers:
    def __init__(self):
        self.handlers = [
            CallbackQueryHandler(self.model_callback_handler, pattern="^model_.+$"),
            CallbackQueryHandler(self.memory_callback_handler, pattern="^toggle_memory$")
        ]


    async def model_callback_handler(self, update: Update, context: CallbackContext):
        query = update.callback_query
        user_id = str(update.effective_user.id)
        api = DuckDuckGoChatAPI(user_id=user_id)

        # بررسی داده‌ی کالبک در دیکشنری مترادف‌ها
        selected_model = MODEL_SYNONYMS.get(query.data, None)

        if selected_model:
            # به‌روزرسانی مدل کاربر
            api.data[user_id]["selected_model"] = selected_model
            api.save_user_data()

            # پاسخ به کاربر
            await query.answer(f"Model changed to {selected_model}.")
        else:
            await query.answer("Invalid selection.")

        # بستن پیام کالبک
        await query.edit_message_text(f"Selected Model: {selected_model}")


    async def memory_callback_handler(self, update: Update, context: CallbackContext):
        query = update.callback_query
        user_id = str(update.effective_user.id)
        api = DuckDuckGoChatAPI(user_id=user_id)
    
        # تغییر وضعیت مموری
        current_memory_status = api.data[user_id].get("memory", True)
        new_memory_status = not current_memory_status
        api.data[user_id]["memory"] = new_memory_status

        api.save_user_data()

        memory_status_text = "Memory: Enabled✅" if new_memory_status else "Memory: Disabled❌"

        # ساخت مجدد اینلاین کیبورد
        keyboard = [
            [
                InlineKeyboardButton("GPT-4o", callback_data="model_gpt4o"),
                InlineKeyboardButton("Claude 3", callback_data="model_claude3"),
            ],
            [
                InlineKeyboardButton("Llama 3.1", callback_data="model_llama31"),
                InlineKeyboardButton("Mixtral", callback_data="model_mixtral"),
            ],
            [
                InlineKeyboardButton(memory_status_text, callback_data="toggle_memory"),
            ],
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        # به‌روزرسانی اینلاین کیبورد
        await query.edit_message_reply_markup(reply_markup=reply_markup)

        # پاسخ به کاربر
        await query.answer(f"Memory is now {memory_status_text}.")


    def get_handlers(self):
        return self.handlers
