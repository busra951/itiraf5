#!/usr/bin/env python3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import BadRequest
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

# Bot ayarların
BOT_TOKEN      = "7674747829:AAG16zyar0AbvECH__E1Rh8uimk94UHODd0"
ADMIN_GROUP_ID = -1002607082304  # Admin grubu
CHANNEL_ID     = -1002686896561  # (istersen kullan)
KANAL_LINK     = "https://t.me/aramizda_kalsin_sohbet_muhabbet"
BOT_LINK       = "https://t.me/Aramizdakalsin_bot"

# Durum saklama
awaiting_confession = set()

async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != "private":
        return

    keyboard = [
        [InlineKeyboardButton("✅ İtiraf Et", callback_data="start_confess")],
        [InlineKeyboardButton("Hiçbir itirafı kaçırmamak için buraya tıkla", url=KANAL_LINK)],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "👋 Anonim olarak bir itiraf göndermek ister misin?\n\n"
        "Aşağıdaki butona tıkla ve itirafını yaz!\n\n"
        "Tüm itirafları görmek için sohbet kanalımıza katılabilirsin.",
        reply_markup=reply_markup
    )

async def tanitim_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("İtiraf etmek için buraya tıkla", url=BOT_LINK)],
        [InlineKeyboardButton("Hiçbir itirafı kaçırmamak için buraya tıkla", url=KANAL_LINK)],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "✨ Anonim itiraf etmek için aşağıdaki butonu kullan.\n"
        "Tüm itirafları kaçırmamak için sohbet kanalımıza katıl!",
        reply_markup=reply_markup
    )

async def start_cb_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cq = update.callback_query
    await cq.answer()
    await cq.edit_message_reply_markup(None)

    if cq.data == "start_confess":
        awaiting_confession.add(cq.from_user.id)
        await cq.message.reply_text("✍️ Lütfen itiraf metnini yazın:")
    else:
        await cq.message.reply_text(
            "❌ İtiraf etmekten vazgeçildi. Yeniden başlamak için /start komutunu kullanabilirsin."
        )

async def confession_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != "private" or not update.message.text:
        return

    user_id = update.effective_user.id
    if user_id not in awaiting_confession:
        return

    text = update.message.text.strip()
    awaiting_confession.remove(user_id)

    # Kesinlikle isim, kullanıcı adı YOK! Sadece metin gönderiliyor.
    await context.bot.send_message(
        chat_id=ADMIN_GROUP_ID,
        text=f"📢 Yeni İtiraf:\n\n{text}"
    )

    await update.message.reply_text(
        "🙌 İtirafınız yöneticilere iletildi, teşekkürler!\n\n"
        f"Hiçbir itirafı kaçırmamak için sohbet kanalımıza katıl: {KANAL_LINK}"
    )

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    error = context.error
    # Eskimiş callback-query hatasını görmezden gel
    if isinstance(error, BadRequest) and "too old" in str(error).lower():
        return
    # Diğer hataları logla
    print(f"Unhandled error: {error!r}")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CommandHandler("tanitim", tanitim_cmd))
    app.add_handler(CallbackQueryHandler(start_cb_handler, pattern="^start_"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, confession_handler))
    app.add_error_handler(error_handler)

    print("Bot çalışıyor…")
    app.run_polling()

if __name__ == "__main__":
    main()
