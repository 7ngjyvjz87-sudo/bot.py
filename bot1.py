import os
import re
import hashlib
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Token được dán trực tiếp
TOKEN = "8995256203:AAEptsapA356ybV77QdgHnoYZIzu-xYGO6Y"

VALID_KEYS = ["VIP123", "NAMVIP2026"]
ACTIVATED_USERS = set()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in ACTIVATED_USERS:
        await update.message.reply_text(
            "✅ Bot phân tích MD5 & Soi cầu nâng cao đã sẵn sàng!\n\n"
            "👉 Hãy gửi **mã MD5** (32 ký tự) hoặc **chuỗi 10 kết quả** (ví dụ: `T T X T X X T T T X` hoặc `12 8 15 6 11...`) để bot phân tích."
        )
    else:
        context.user_data["waiting_key"] = True
        await update.message.reply_text("🔑 Vui lòng nhập Key kích hoạt bản quyền để sử dụng bot:")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()
    
    if context.user_data.get("waiting_key"):
        if text in VALID_KEYS:
            ACTIVATED_USERS.add(user_id)
            context.user_data["waiting_key"] = False
            await update.message.reply_text(
                "🎉 Kích hoạt thành công!\n\n"
                "👉 Bạn có thể dán mã MD5 hoặc chuỗi lịch sử 10 phiên vào đây để soi cầu."
            )
        else:
            await update.message.reply_text("❌ Key không chính xác! Vui lòng nhập lại:")
        return

    if user_id not in ACTIVATED_USERS:
        await update.message.reply_text("🔒 Bạn chưa nhập Key! Vui lòng gõ /start để kích hoạt.")
        return

    # Xử lý nếu người dùng dán Mã MD5 (32 ký tự Hex)
    if len(text) == 32 and all(c in '0123456789abcdefABCDEF' for c in text):
        hash_val = int(text[:8], 16)
        score = (hash_val % 16) + 3
        
        # Phân tích xúc xắc
        d1 = (hash_val % 6) + 1
        d2 = ((hash_val // 6) % 6) + 1
        d3 = ((hash_
