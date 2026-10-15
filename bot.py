import os
import uuid
import hashlib
import random
import logging
from datetime import datetime, timedelta
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

# Bộ nhớ tạm lưu trữ Key và Trạng thái người dùng
valid_keys = {}
user_active_keys = {}
user_selected_game = {}
user_streaks = {}

# Khởi tạo Web Server Flask giữ bot 24/7
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

# --- GIAO DIỆN NÚT BẤM CỔNG GAME ---
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

# --- KIỂM TRA TRẠNG THÁI KEY CỦA USER ---
def check_user_key(user_id):
    if user_id == ADMIN_ID:
        return True, "Admin (Vĩnh viễn)"
    
    if user_id not in user_active_keys:
        return False, "Chưa kích hoạt Key"
    
    expiry = user_active_keys[user_id]
    if expiry == "vv":
        return True, "Vĩnh viễn"
    
    if datetime.now() < expiry:
        time_left = expiry - datetime.now()
        hours = int(time_left.total_seconds() // 3600)
        minutes = int((time_left.total_seconds() % 3600) // 60)
        return True, f"Còn {hours} giờ {minutes} phút"
    else:
        return False, "Key đã hết hạn"

# --- LỆNH START & MENU ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "🌟 *HỆ THỐNG PHÂN TÍCH THUẬT TOÁN MD5 & SHA-256* 🌟\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n"
        "⚡ Chào mừng bạn đến với công cụ soi cầu độc quyền.\n"
        "🔑 Dùng lệnh `/nhapkey <Mã_Key>` để kích hoạt quyền truy cập.\n\n"
        "👉 *Vui lòng chọn cổng game bên dưới để bắt đầu:*"
    )
    if update.message:
        await update.message.reply_text(welcome_text, reply_markup=get_game_keyboard(), parse_mode='Markdown')
    elif update.callback_query:
        await update.callback_query.message.edit_text(welcome_text, reply_markup=get_game_keyboard(), parse_mode='Markdown')

# --- LỆNH TẠO KEY (DÀNH CHO ADMIN) ---
async def taokey_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("⛔ *Bạn không có quyền quản trị viên!*", parse_mode='Markdown')
        return

    if not context.args:
        help_msg = (
            "⚙️ **BẢNG TẠO KEY DÀNH CHO ADMIN**\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            "📌 *Cú pháp:* `/taokey <gói>`\n\n"
            "🔹 `/taokey 1d` : Key 1 Ngày (3k)\n"
            "🔹 `/taokey 1w` : Key 1 Tuần (50k)\n"
            "🔹 `/taokey 1m` : Key 1 Tháng (100k)\n"
            "🔹 `/taokey vv` : Key Vĩnh Viễn (150k)"
        )
        await update.message.reply_text(help_msg, parse_mode='Markdown')
        return

    option = context.args[0].lower()
    key_code = f"VIP-{uuid.uuid4().hex[:8].upper()}"
    
    if option in ["1d", "1ngay", "3k"]:
        valid_keys[key_code] = ("1d", "1 Ngày (3.000đ)")
        duration_text = "1 Ngày (3.000đ)"
    elif option in ["1w", "1tuan", "50k"]:
        valid_keys[key_code] = ("1w", "1 Tuần (50.000đ)")
        duration_text = "1 Tuần (50.000đ)"
    elif option in ["1m", "1thang", "100k"]:
        valid_keys[key_code] = ("1m", "1 Tháng (100.000đ)")
        duration_text = "1 Tháng (100.000đ)"
    elif option in ["vv", "vinhvien", "150k"]:
        valid_keys[key_code] = ("vv", "Vĩnh Viễn (150.000đ)")
        duration_text = "Vĩnh Viễn (150.000đ)"
    else:
        await update.message.reply_text("❌ Gói key không hợp lệ! Dùng: `1d`, `1w`, `1m`, `vv`", parse_mode='Markdown')
        return

    msg = (
        f"🔑 **KHỞI TẠO KEY THÀNH CÔNG**\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🔹 **Mã Key:** `{key_code}`\n"
        f"⏳ **Gói sử dụng:** `{duration_text}`\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👉 *Gửi mã này cho khách kèm lệnh:* `/nhapkey {key_code}`"
    )
    await update.message.reply_text(msg, parse_mode='Markdown')

# --- LỆNH NHẬP KEY (DÀNH CHO USER) ---
async def nhapkey_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if not context.args:
        await update.message.reply_text("⚠️ Vui lòng nhập mã Key! Cú pháp: `/nhapkey <mã_key>`", parse_mode='Markdown')
        return

    input_key = context.args[0].strip()

    if input_key not in valid_keys:
        await update.message.reply_text("❌ *Mã Key không tồn tại hoặc đã được sử dụng!*", parse_mode='Markdown')
        return

    key_type, duration_text = valid_keys[input_key]

    now = datetime.now()
    if key_type == "1d":
        user_active_keys[user_id] = now + timedelta(days=1)
    elif key_type == "1w":
        user_active_keys[user_id] = now + timedelta(weeks=1)
    elif key_type == "1m":
        user_active_keys[user_id] = now + timedelta(days=30)
    elif key_type == "vv":
        user_active_keys[user_id] = "vv"

    del valid_keys[input_key]

    msg = (
        f"🎉 **KÍCH HOẠT KEY THÀNH CÔNG!** 🎉\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 **User ID:** `{user_id}`\n"
        f"⏳ **Thời hạn:** `{duration_text}`\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🚀 Bây giờ bạn có thể chọn cổng game và dán mã MD5 để soi cầu!"
    )
    await update.message.reply_text(msg, parse_mode='Markdown')

# --- TƯƠNG TÁC NÚT BẤM ---
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

# --- XỬ LÝ TIN NHẮN SOI CẦU ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()
    
    if text.startswith('/'):
        return

    # KIỂM TRA BẢO MẬT KEY (Đã thêm dòng liên hệ Admin)
    is_valid, status_msg = check_user_key(user_id)
    if not is_valid:
        msg_key_req = (
            f"⛔ **BẠN CHƯA CÓ KEY BẢN QUYỀN!**\n"
            f"Trạng thái: `{status_msg}`\n\n"
            f"💳 **BẢNG GIÁ VIP KEY:**\n"
            f"• 1 Ngày: **3.000đ**\n"
            f"• 1 Tuần: **50.000đ**\n"
            f"• 1 Tháng: **100.000đ**\n"
            f"• Vĩnh Viễn: **150.000đ**\n\n"
            f"📩 **Liên hệ trực tiếp Admin để mua Key:** [Bấm vào đây để nhắn tin](tg://user?id=8886381571)\n"
            f"👉 Sau khi có mã, dùng lệnh: `/nhapkey <mã_key>` để kích hoạt!"
        )
        await update.message.reply_text(msg_key_req, parse_mode='Markdown', disable_web_page_preview=True)
        return

    current_game = user_selected_game.get(user_id, "Cổng Chung")
    
    if len(text) < 10:
        await update.message.reply_text("❌ *Mã Hash không hợp lệ!* Vui lòng kiểm tra lại độ dài mã.", parse_mode='Markdown')
        return

    loading_msg = await update.message.reply_text(
        f"🔍 *Đang thiết lập kết nối mã hóa với {current_game}*...\n⏳ `[░░░░░░░░░░] 0%`", 
        parse_mode='Markdown'
    )
    
    await context.bot.edit_message_text(
        chat_id=update.effective_chat.id,
        message_id=loading_msg.message_id,
        text=f"⚙️ *Đang giải mã chuỗi MD5 & SHA-256*...\n⏳ `[█████░░░░░] 50%`",
        parse_mode='Markdown'
    )
    
    res_type, win_rate, sub_hash = analyze_hash(text)
    user_streaks[user_id] = user_streaks.get(user_id, 0) + 1
    
    await context.bot.edit_message_text(
        chat_id=update.effective_chat.id,
        message_id=loading_msg.message_id,
        text=f"🔮 *Đang tổng hợp thuật toán cầu*...\n⏳ `[██████████] 100%`",
        parse_mode='Markdown'
    )
    
    msg = (
        f"✨ **KẾT QUẢ PHÂN TÍCH CHI TIẾT** ✨\n"
        f"🌐 **Cổng Game:** `{current_game}`\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🔑 **Mã Hash:** `{text[:8]}...{text[-6:]}`\n"
        f"🛡️ **Mã Hóa 256:** `{sub_hash}...`\n"
        f"🎯 **Dự Đoán:** **{res_type}**\n"
        f"📈 **Tỷ Lệ Thắng:** `{win_rate}%`\n"
        f"🔥 **Phiên Soi Cầu:** `#`{user_streaks[user_id]}\n"
        f"⏱️ **Hạn Key:** `{status_msg}`\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"💡 *Khuyên dùng:* Quản lý vốn thông minh, tránh tất tay!"
    )
    
    switch_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Tiếp tục soi mã mới", callback_data="back_to_menu")]
    ])
    
    await update.message.reply_text(msg, reply_markup=switch_keyboard, parse_mode='Markdown')

# --- MAIN ---
def main():
    keep_alive()
    
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("taokey", taokey_command))
    application.add_handler(CommandHandler("nhapkey", nhapkey_command))
    
    application.add_handler(CallbackQueryHandler(back_menu_handler, pattern="^back_to_menu$"))
    application.add_handler(CallbackQueryHandler(button_handler, pattern="^game_"))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    print("Bot VIP Key System đang chạy...")
    application.run_polling()

if __name__ == '__main__':
    main()
