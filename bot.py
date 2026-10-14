import os
import re
import hashlib
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("TOKEN")

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
        d3 = ((hash_val // 36) % 6) + 1
        total_dice = d1 + d2 + d3
        
        main_res = "🔴 TÀI" if total_dice >= 11 else "🔵 XỈU"
        rate_tai = int(50 + ((hash_val % 41) - 20))
        rate_xiu = 100 - rate_tai
        
        # Soi nhịp 3 ván kế tiếp
        n1 = "🔴 TÀI" if (hash_val % 2 == 0) else "🔵 XỈU"
        n2 = "🔵 XỈU" if n1 == "🔴 TÀI" else "🔴 TÀI"
        n3 = "🔴 TÀI" if (hash_val % 3 != 0) else "🔵 XỈU"

        msg = f"""━━━━━━━━━━━━━━━━━━━━━━━━
🎲 HỆ THỐNG SOI CẦU MD5 TỐI ƯU
━━━━━━━━━━━━━━━━━━━━━━━━
🔑 Hash: `{text[:8]}...{text[-6:]}`
🎯 Bộ xúc xắc: {d1} - {d2} - {d3} (Tổng: {total_dice})
✅ DỰ ĐOÁN VÁN NÀY: **{main_res}**
📊 Tỷ lệ thuật toán: Tài {rate_tai}% | Xỉu {rate_xiu}%

🔮 DỰ ĐOÁN CHUỖI VÁN TIẾP THEO:
────────────────────
📍 Ván +1: {n1} (Cầu chính)
📍 Ván +2: {n2} (Tín hiệu đảo)
📍 Ván +3: {n3} (Bám nhịp)

💡 Chiến thuật: Đánh {main_res}. Nếu gãy ván 1, gấp thếp nhẹ sang ván +1.
━━━━━━━━━━━━━━━━━━━━━━━━"""
        await update.message.reply_text(msg, parse_mode="Markdown")
        return

    # Xử lý phân tích chuỗi nhiều phiên (10 phiên)
    history = re.findall(r'[TXtx1234567890]+', text)
    if len(history) >= 5:
        # Quy đổi dữ liệu nhập vào thành Tài (T) hoặc Xỉu (X)
        parsed = []
        for item in history:
            if item.upper() in ['T', 'TAI'] or (item.isdigit() and int(item) >= 11):
                parsed.append('T')
            elif item.upper() in ['X', 'XIU'] or (item.isdigit() and int(item) < 11):
                parsed.append('X')
        
        if len(parsed) >= 5:
            recent_10 = parsed[-10:]
            count_t = recent_10.count('T')
            count_x = recent_10.count('X')
            
            # Thuật toán soi cầu bệt / cầu 1-1 / cầu đảo
            last_item = recent_10[-1]
            streak = 1
            for i in range(len(recent_10) - 2, -1, -1):
                if recent_10[i] == last_item:
                    streak += 1
                else:
                    break
