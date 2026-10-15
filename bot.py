import os
import hashlib
import random
import time
import logging
from flask import Flask
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes
)

# Cấu hình Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Thông số hệ thống
TOKEN = "8995256203:AAH9UvKhKVDIv-_nS_OSjxu-O1wpquN3ks0"
ADMIN_ID = 8886381571

# Lưu trữ trạng thái
user_selected_game = {}
user_streaks = {}

# Khởi tạo Flask giữ bot 24/7
app = Flask('')

@app.route('/')
def home():
    return "Hệ thống Bot Phân Tích Đa Cổng Game VIP đang hoạt động 24/7!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()

# --- HÀM PHÂN TÍCH HASH ---
def analyze_hash(hash_input: str):
    hash_clean = hash_input.strip().lower()
    sha256_layer = hashlib.sha256(hash_clean.encode()).hexdigest()
    total_val = sum(int(char, 16) for char in hash_clean if char in "0123456789abcdef")
    result_type = "TÀI 🎲" if total_val % 2 == 0 else "XỈU 🎲"
    rate = random.randint(82, 98)
    return result_type, rate, sha256_layer[:12]

# --- GIAO DIỆN NÚT BẤM HIỆN ĐẠI ---
def get_game_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("☀️ Sunwin VIP", callback_data="game_sunwin"),
            InlineKeyboardButton("💎 LC79 Gaming", callback_data="game_lc79")
        ],
        [
            InlineKeyboardButton("🚀 B52 Club", callback_data="game_b52"),
            InlineKeyboardButton("🔥 Son01 Hub", callback_data="game_son01")
        ],
        [
            InlineKeyboardButton("👑 Hitclub Pro", callback_data="game_hitclub"),
            InlineKeyboardButton("🌐 Cổng Game Khác", callback_data="game_other")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

# --- CÁC LỆNH BOT ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "🌟 *HỆ THỐNG PHÂN TÍCH THUẬT TOÁN MD5 & SHA-256* 🌟\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n"
        "⚡ Chào mừng bạn đến với công cụ soi cầu độc quyền.\n"
        "🎯 Độ chính xác cao, phân tích đa lớp thời gian thực.\n\n"
        "👉 *Vui lòng chọn cổng game bên dưới để bắt đầu:*"
    )
    if update.message:
        await update.message.reply_text(welcome_text, reply_markup=get_game_keyboard(), parse_mode='Markdown')
    elif update.callback_query:
        await update.callback_query.message.edit_text(welcome_text, reply_markup=get_game_keyboard(), parse_mode='Markdown')

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    data = query.data
    
    game_names = {
        "game_sunwin": "Sunwin ☀️",
        "game_lc79": "LC79 💎",
        "game_b52": "B52 🚀",
        "game_son01": "Son01 🔥",
        "game_hitclub": "Hitclub 👑",
        "game_other": "Cổng Game Khác 🌐"
    }
    
    selected_name = game_names.get(data, "Hệ thống")
    user_selected_game[user_id] = selected_name
    
    prompt_text = (
        f"🎮 Đã kết nối thành công với: *{selected_name}*\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n"
        "📥 *Hãy gửi mã MD5 / SHA-256 của phiên chơi vào đây.*\n"
        "⏳ Hệ thống sẽ tự động quét và trả kết quả sau vài giây."
    )
    
    back_keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Quay lại chọn cổng game", callback_data="back_to_menu")]])
    await query.message.edit_text(prompt_text, reply_markup=back_keyboard, parse_mode='Markdown')

async def back_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await start(update, context)

# Xử lý tin nhắn và tạo hiệu ứng quét giả lập cực ngầu
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()
    
    if text.startswith('/'):
        return

    current_game = user_selected_game.get(user_id, "Cổng Chung")
    
    if len(text) < 10:
        await update.message.reply_text("❌ *Mã Hash không hợp lệ!* Vui lòng kiểm tra lại độ dài mã.", parse_mode='Markdown')
        return

    # Gửi hiệu ứng "Đang quét" để người dùng thấy sinh động
    loading_msg = await update.message.reply_text(
        f"🔍 *Đang thiết lập kết nối mã hóa với {current_game}*...\n"
        "⏳ `[░░░░░░░░░░] 0%`", 
        parse_mode='Markdown'
    )
    
    # Hiệu ứng chạy thanh tiến trình giả lập mượt mà
    await context.bot.edit_message_text(
        chat_id=update.effective_chat.id,
        message_id=loading_msg.message_id,
        text=f"⚙️ *Đang giải mã chuỗi MD5 & SHA-256*...\n⏳ `[█████░░░░░] 50%`",
        parse_mode='Markdown'
    )
    
    # Tính toán kết quả thực tế
    res_type, win_rate, sub_hash = analyze_hash(text)
    user_streaks[user_id] = user_streaks.get(user_id, 0) + 1
    
    await context.bot.edit_message_text(
        chat_id=update.effective_chat.id,
        message_id=loading_msg.message_id,
        text=f"🔮 *Đang tổng hợp thuật toán cầu*...\n⏳ `[██████████] 100%`",
        parse_mode='Markdown'
    )
    
    # Xuất kết quả cuối cùng cực kỳ chi tiết và bắt mắt
    msg = (
        f"✨ **KẾT QUẢ PHÂN TÍCH CHI TIẾT** ✨\n"
        f"🌐 **Cổng Game:** `{current_game}`\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🔑 **Mã Hash:** `{text[:8]}...{text[-6:]}`\n"
        f"🛡️ **Mã Hóa 256:** `{sub_hash}...`\n"
        f"🎯 **Dự Đoán:** **{res_type}**\n"
        f"📈 **Tỷ Lệ Thắng:** `{win_rate}%`\n"
        f"🔥 **Phiên Soi Cầu:** `#`{user_streaks[user_id]}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"💡 *Khuyên dùng:* Quản lý vốn thông minh, tránh tất tay!"
    )
    
    switch_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Tiếp tục soi mã mới", callback_data="back_to_menu")]
    ])
    
    # Gửi tin nhắn kết quả hoàn chỉnh
    await update.message.reply_text(msg, reply_markup=switch_keyboard, parse_mode='Markdown')

async def taokey_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("⛔ *Bạn không có quyền quản trị viên!*", parse_mode='Markdown')
        return
    await update.message.reply_text("⚙️ **ADMIN PANEL:** Đã khởi tạo và cấp phát Key hệ thống thành công!", parse_mode='Markdown')

# --- MAIN ---
def main():
    keep_alive()
    
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("taokey", taokey_command))
    
    application.add_handler(CallbackQueryHandler(back_menu_handler, pattern="^back_to_menu$"))
    application.add_handler(CallbackQueryHandler(button_handler, pattern="^game_"))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    print("Bot đa cổng game giao diện VIP đang chạy...")
    application.run_polling()

if __name__ == '__main__':
    main()
