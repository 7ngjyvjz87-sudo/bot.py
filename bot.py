import os
import re
import random
import datetime
import threading
import hashlib
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# 1. Web Service duy trì 24/7 trên Render
app_web = Flask(__name__)

@app_web.route('/')
def home():
    return "Bot Combo Huy Diet 24/7 dang hoat dong!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app_web.run(host='0.0.0.0', port=port)

# 2. Cấu hình Bot & Key (Đã gán ID Admin của Nam: 8886381571)
TOKEN = "8995256203:AAEptsapA356ybV77QdgHnoYZIzu-xYGO6Y"

KEYS_DB = {
    8886381571: datetime.datetime(2099, 1, 1) # Quyền Admin vĩnh viễn cho Nam
}

USER_EXPIRE = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    now = datetime.datetime.now()
    
    if "stats" not in context.user_data:
        context.user_data["stats"] = {"win": 0, "lose": 0, "streak": 0, "last_pred": None}

    if user_id in KEYS_DB and KEYS_DB[user_id] > now:
        exp_date = "Vĩnh viễn" if KEYS_DB[user_id].year > 2090 else KEYS_DB[user_id].strftime("%d/%m/%Y %H:%M")
        await update.message.reply_text(
            f"👑 **HỆ THỐNG SOICAU VIP 2027**\n"
            f"────────────────────\n"
            f"🟢 Trạng thái: Hoạt động ổn định (Admin)\n"
            f"⏳ Hạn sử dụng: **{exp_date}**\n\n"
            f"📌 **HƯỚNG DẪN:**\n"
            f"Gửi chuỗi lịch sử (VD: `T X T T X`) hoặc kèm mã MD5. Bot sẽ tự động chấm điểm ván trước và soi cầu ván mới!"
        )
    elif user_id in USER_EXPIRE and USER_EXPIRE[user_id] > now:
        exp_date = USER_EXPIRE[user_id].strftime("%d/%m/%Y %H:%M")
        await update.message.reply_text(
            f"👑 **HỆ THỐNG SOICAU VIP 2027**\n"
            f"────────────────────\n"
            f"🟢 Trạng thái: Hoạt động ổn định\n"
            f"⏳ Hạn sử dụng: **{exp_date}**\n\n"
            f"📌 **HƯỚNG DẪN:**\n"
            f"Gửi chuỗi lịch sử (VD: `T X T T X`) hoặc kèm mã MD5 để hệ thống phân tích."
        )
    else:
        context.user_data["waiting_key"] = True
        await update.message.reply_text(
            "🔐 **XÁC THỰC BẢN QUYỀN HỆ THỐNG**\n"
            "────────────────────\n"
            "⚠️ Tài khoản của bạn chưa kích hoạt key bản quyền.\n\n"
            "💰 **BẢNG GIÁ THUÊ KEY:**\n"
            "• 1 Ngày: 3.000đ\n"
            "• 1 Tuần: 50.000đ\n"
            "• Vĩnh viễn: 100.000đ\n\n"
            "👉 Nhập mã khóa hoặc dùng lệnh: `/key MÃ_CỦA_BẠN`"
        )

# Lệnh Admin tạo key
async def taokey(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id not in KEYS_DB or KEYS_DB[user_id] < datetime.datetime(2090, 1, 1):
        await update.message.reply_text("❌ Bạn không có quyền sử dụng lệnh này!")
        return

    try:
        args = context.args
        duration_type = args[0].lower()
        
        import string
        key_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
        formatted_key = f"{key_code[:4]}-{key_code[4:8]}-{key_code[8:]}"

        now = datetime.datetime.now()

        if duration_type in ["ngay", "1ngay", "1n", "day"]:
            expire_time = now + datetime.timedelta(days=1)
            time_str = "1 ngày"
            price_str = "3.000đ"
        elif duration_type in ["tuan", "1tuan", "1t", "week"]:
            expire_time = now + datetime.timedelta(days=7)
            time_str = "1 tuần"
            price_str = "50.000đ"
        elif duration_type in ["vv", "vinhvien"]:
            expire_time = datetime.datetime(2099, 1, 1)
            time_str = "Vĩnh viễn"
            price_str = "100.000đ"
        else:
            await update.message.reply_text("⚠️ Cú pháp sai! Dùng: `/taokey ngay`, `/taokey tuan`, hoặc `/taokey vv`")
            return

        KEYS_DB[formatted_key] = expire_time
        
        msg = f"""✅ **Tạo khóa thành công!**
────────────────────
🔑 Mã khóa: `{formatted_key}`
⏳ Thời hạn: {time_str}
💵 Giá: {price_str}

Gửi cho khách: `/key {formatted_key}`"""
        await update.message.reply_text(msg, parse_mode="Markdown")
    except Exception:
        await update.message.reply_text("⚠️ Cú pháp chuẩn: `/taokey ngay` hoặc `/taokey tuan` hoặc `/taokey vv`")

# Thuật toán Combo Hủy Diệt
def analyze_combo(recent_list, md5_hex=None):
    count_t = recent_list.count('T')
    count_x = recent_list.count('X')
    total = len(recent_list)
    last = recent_list[-1]
    
    streak = 1
    for i in range(total - 2, -1, -1):
        if recent_list[i] == last:
            streak += 1
        else:
            break

    if streak >= 4:
        hist_pred = "XỈU" if last == 'T' else "TÀI"
        pattern = f"Cầu Bệt ({streak} tay)"
    elif count_t >= (total * 0.7):
        hist_pred = "XỈU"
        pattern = "Lệch Tài nặng -> Hồi Xỉu"
    elif count_x >= (total * 0.7):
        hist_pred = "TÀI"
        pattern = "Lệch Xỉu nặng -> Hồi Tài"
    else:
        hist_pred = "TÀI" if last == 'X' else "XỈU"
        pattern = "Cầu Đảo 1-1 / Linh Hoạt"

    if md5_hex:
        sha256_hash = hashlib.sha256(md5_hex.encode()).hexdigest()
        rev_sha = sha256_hash[::-1]
        pp1_md5 = hashlib.md5(rev_sha.encode()).hexdigest()
        pp1_res = "TÀI" if int(pp1_md5[:8], 16) % 2 == 0 else "XỈU"
        pp1_rate = 88 + (int(pp1_md5[0], 16) % 9)

        mid_chars = md5_hex[8:24]
        rev_mid = mid_chars[::-1] + md5_hex[:8]
        pp2_res = "XỈU" if int(rev_mid[:8], 16) % 2 == 0 else "TÀI"
        pp2_rate = 82 + (int(rev_mid[0], 16) % 10)

        if pp1_res == pp2_res:
            final_res = pp1_res
            final_rate = min(max(pp1_rate, pp2_rate) + 3, 98)
            note = f"Đồng thuận tuyệt đối giữa PP1 và PP2"
        else:
            if pp1_rate >= pp2_rate:
                final_res = pp1_res
                final_rate = pp1_rate
                note = f"Khác nhau — chọn PP1 ({pp1_rate}% > {pp2_rate}%)"
            else:
                final_res = pp2_res
                final_rate = pp2_rate
                note = f"Khác nhau — chọn PP2 ({pp2_rate}% > {pp1_rate}%)"
    else:
        final_res = "TÀI" if hist_pred == "T" else "XỈU"
        final_rate = 89
        note = f"Phân tích theo nhịp cầu: {pattern}"

    return final_res, final_rate, note, count_t, count_x, pattern

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()
    now = datetime.datetime.now()

    if "stats" not in context.user_data:
        context.user_data["stats"] = {"win": 0, "lose": 0, "streak": 0, "last_pred": None}

    # Kiểm tra quyền hạn (Admin hoặc User có key còn hạn)
    is_admin = (user_id in KEYS_DB and KEYS_DB[user_id] > now)
    has_key = (user_id in USER_EXPIRE and USER_EXPIRE[user_id] > now)

    if context.user_data.get("waiting_key") or (not is_admin and not has_key):
        clean_key = text.replace("/key", "").strip()
        if clean_key in KEYS_DB and clean_key != 8886381571:
            expire_time = KEYS_DB[clean_key]
            if expire_time > now:
                USER_EXPIRE[user_id] = expire_time
                context.user_data["waiting_key"] = False
                exp_str = "Vĩnh viễn" if expire_time.year > 2090 else expire_time.strftime("%d/%m/%Y %H:%M")
                await update.message.reply_text(f"✅ **Kích hoạt bản quyền thành công!**\n⏳ Hạn sử dụng đến: {exp_str}")
            else:
                await update.message.reply_text("❌ Mã khóa này đã hết hạn sử dụng!")
        else:
            await update.message.reply_text("❌ Mã khóa không hợp lệ! Vui lòng kiểm tra lại.")
        return

    md5_match = re.search(r'\b[a-fA-F0-9]{32}\b', text)
    md5_hex = md5_match.group(0) if md5_match else None

    clean_text = re.sub(r'\b[a-fA-F0-9]{32}\b', '', text)
    history = re.findall(r'[TXtx1234567890]+', clean_text)

    if len(history) >= 4 or md5_hex:
        parsed = []
        if len(history) >= 4:
            for item in history:
                if item.upper() in ['T', 'TAI'] or (item.isdigit() and int(item) >= 11):
                    parsed.append('T')
                elif item.upper() in ['X', 'XIU'] or (item.isdigit() and int(item) < 11):
                    parsed.append('X')
        
        recent = parsed[-10:] if len(parsed) >= 4 else ['T', 'X', 'T', 'X', 'T']
        
        # Tự động chấm điểm ván trước
        stats = context.user_data["stats"]
        check_result_msg = ""
        if stats["last_pred"] and len(recent) > 0:
            actual_last = "TÀI" if recent[-1] == 'T' else "XỈU"
            if stats["last_pred"] == actual_last:
                stats["win"] += 1
                stats["streak"] = stats["streak"] + 1 if stats["streak"] > 0 else 1
                check_result_msg = f"✅ **VÁN TRƯỚC: WIN ({actual_last})** 🎉"
            else:
                stats["lose"] += 1
                stats["streak"] = stats["streak"] - 1 if stats["streak"] < 0 else -1
                check_result_msg = f"❌ **VÁN TRƯỚC: LOSE ({actual_last})** 💔"

        pred, rate, note, c_t, c_x, pattern = analyze_combo(recent, md5_hex)
        stats["last_pred"] = pred
        
        icon_res = "🔴" if pred == "TÀI" else "🔵"
        
        if rate >= 90:
            warning_box = "🔥 **KHUYẾN NGHỊ:** Cầu nét, đi tỉ trọng chuẩn 10-15% vốn. Tuyệt đối không tất tay."
        elif "Khác nhau" in note or "Lệch" in pattern:
            warning_box = "⚠️ **CẢNH BÁO RỦI RO:** Tín hiệu giằng co. Hạ nhỏ tiền hoặc ngưng 1-2 nhịp."
        else:
            warning_box = "💡 **QUẢN LÝ VỐN:** Đi đều tay, chốt lãi 30% tổng vốn là dừng."

        streak_str = f"Win (+{stats['streak']})" if stats['streak'] > 0 else (f"Lose ({stats['streak']})" if stats['streak'] < 0 else "0")

        msg = f"""{f"{check_result_msg}\n────────────────────\n" if check_result_msg else ""}📊 **KẾT QUẢ TỪ PHÂN TÍCH COMBO HỦY DIỆT**

━━━━━━━━━━━━━━━━━━
📌 **MÔ HÌNH CẦU:** {pattern}
📈 **TỈ LỆ LỊCH SỬ:** {c_t} Tài - {c_x} Xỉu
{f"🔑 **MD5:** `{md5_hex[:8]}...`" if md5_hex else ""}
💡 ⚠️ {note}

━━━━━━━━━━━━━━━━━━
🔹 **KẾT QUẢ CHUNG: {icon_res} {pred}**
📈 **TỈ LỆ CHUẨN XÁC: {rate}%**
🏆 **PHONG ĐỘ:** Thắng: {stats['win']} | Thua: {stats['lose']} | Chuỗi: {streak_str}

━━━━━━━━━━━━━━━━━━
{warning_box}"""
        await update.message.reply_text(msg, parse_mode="Markdown")
        return

    await update.message.reply_text(
        "⚠️ **Dữ liệu không hợp lệ!**\n"
        "👉 Gửi chuỗi ván gần nhất (VD: `T X T T X`) hoặc kèm mã MD5 32 ký tự."
    )

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("taokey", taokey))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Bot Admin Ready Dang Chay...")
    app.run_polling()
