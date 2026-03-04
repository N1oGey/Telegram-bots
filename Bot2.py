import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "8779392218:AAHj1ULGLLVr50yo_NXfEfzW_V5PBEEuQl0"
PASTEBIN_API_KEY = "y7uWfuOF05e_GrL96ScpehIT5vMY94Bo"

waiting_for_file = set()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome to Loadstring converter TELEGRAM.\n"
        "Send a command /makeloadstring for converting code to loadstring"
    )


async def makeloadstring(update: Update, context: ContextTypes.DEFAULT_TYPE):
    waiting_for_file.add(update.effective_user.id)
    await update.message.reply_text("Okay, send a your lua or txt file")


async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id not in waiting_for_file:
        await update.message.reply_text("Send /makeloadstring first")
        return

    document = update.message.document

    if not document:
        return

    if not document.file_name.endswith((".lua", ".txt")):
        await update.message.reply_text("Send only .lua or .txt file")
        return

    await update.message.reply_text("Uploading to Pastebin...")

    try:
        file = await document.get_file()
        file_bytes = await file.download_as_bytearray()
        code_text = file_bytes.decode("utf-8")

        paste_data = {
            "api_dev_key": PASTEBIN_API_KEY,
            "api_option": "paste",
            "api_paste_code": code_text,
            "api_paste_private": 1,
            "api_paste_expire_date": "N",
        }

        response = requests.post(
            "https://pastebin.com/api/api_post.php",
            data=paste_data,
            timeout=15
        )

        if response.status_code == 200 and "pastebin.com" in response.text:
            paste_link = response.text.strip()
            raw_link = paste_link.replace("pastebin.com/", "pastebin.com/raw/")

            await update.message.reply_text(
                f'`loadstring(game:HttpGet("{raw_link}"))()`',
                parse_mode="Markdown",
                reply_to_message_id=update.message.message_id
            )

            waiting_for_file.remove(user_id)

        else:
            await update.message.reply_text(f"Pastebin error:\n{response.text}")

    except Exception as e:
        await update.message.reply_text(f"Error:\n{e}")


def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("makeloadstring", makeloadstring))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_file))

    print("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()