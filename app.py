import os
import json
from flask import Flask, request, jsonify
from telebot import TeleBot, types
from flask_cors import CORS

BOT_TOKEN = "8133185900:AAHVHTArbMIGbiQi6QKy2cvJArm9Vti8InU"
SUPER_ADMIN_ID = 5899057322

# Bot obyektini yaratish
bot = TeleBot(BOT_TOKEN)
app = Flask(__name__)
CORS(app)

# Til matnlari (soddalashtirilgan, texts.py faylini import qilish shart emas)
TEXTS = {
    'uz': {
        "new_application_admin": "Yangi Ariza Keldi!",
        "application_received_user_confirmation": "✅ Arizangiz muvaffaqiyatli qabul qilindi! 🎉\n\nSizning arizangiz mutaxassislarimiz tomonidan ko'rib chiqiladi. Iltimos, javobni kuting. Tez orada siz bilan bog'lanamiz!\n\nRahmat! 😊",
        "error_occurred_try_again": "❌ Kechirasiz, arizani qayta ishlashda kutilmagan xato yuz berdi.\nIltimos, qayta urinib ko'ring yoki bot adminiga murojaat qiling.\n\nUzr so'raymiz! 😔",
    },
    'ru': {
        "new_application_admin": "Поступила новая заявка!",
        "application_received_user_confirmation": "✅ Ваша заявка успешно принята! 🎉\n\nВаша заявка будет рассмотрена нашими специалистами. Пожалуйста, ожидайте ответа. Вскоре мы свяжемся с вами!\n\nСпасибо! 😊",
        "error_occurred_try_again": "❌ Извините, при обработке заявке произошла непредвиденная ошибка.\nПожалуйста, попробуйте еще раз или обратитесь к администратору бота.\n\nПриносим извинения! 😔",
    }
}

# Asosiy URL manziliga so'rov kelganda
@app.route('/')
def home():
    return "Flask backend ishlamoqda. Web App arizalarini kutmoqda."

# Web App'dan kelgan arizalarni qabul qilish uchun API endpoint
@app.route('/submit_application', methods=['POST'])
def submit_application():
    if not request.is_json:
        return jsonify({"status": "error", "message": "Request must be JSON"}), 400

    data = request.json
    print(f"Received data from Web App: {data}")

    user_id = data.get('userId')
    if not user_id:
        return jsonify({"status": "error", "message": "User ID not provided"}), 400

    try:
        
        lang = 'uz' # Standart til
        # Agar 'lang' keyi data ichida bo'lsa, undan foydalanamiz
        if data.get('lang') in TEXTS:
            lang = data.get('lang')

        txt = TEXTS.get(lang, TEXTS['uz']) # Tanlangan til yoki standart O'zbek tili

        # Adminlarga yuboriladigan xabar matnini shakllantirish
        admin_message_text = (
            f"🔔 <b>{txt['new_application_admin']}</b> 🔔\n\n"
            f"--- <b>Foydalanuvchi Ma'lumotlari</b> ---\n"
            f"🆔 <b>Foydalanuvchi ID:</b> <code>{user_id}</code>\n\n"
            f"--- <b>Ariza Tafsilotlari</b> ---\n"
            f"1️⃣ <b>Yechish usuli:</b> <i>{data.get('withdrawalMethod', 'Kiritilmagan')}</i>\n"
            f"2️⃣ <b>Valyuta:</b> <i>{data.get('currency', 'Kiritilmagan')}</i>\n"
            f"3️⃣ <b>Kurator Likee ID:</b> <i>{data.get('curatorLikeeId', 'Kiritilmagan')}</i>\n"
            f"4️⃣ <b>Sizning Likee ID:</b> <i>{data.get('userLikeeId', 'Kiritilmagan')}</i>\n"
            f"5️⃣ <b>Miqdor ($):</b> <i>{data.get('amount', 'Kiritilmagan')}</i>\n"
            f"6️⃣ <b>Bank karta raqami:</b> <code>{data.get('bankCard', 'Kiritilmagan')}</code>\n"
            f"7️⃣ <b>Aloqa raqami:</b> <i>{data.get('contact', 'Kiritilmagan')}</i>\n\n"
            f"✨ **Tezda ko'rib chiqing!** ✨"
        )

        # Admin ID'lari (faqat Super Admin ID'si)
        admin_ids_to_send = [SUPER_ADMIN_ID]

        for admin_id in admin_ids_to_send:
            try:
                bot.send_message(admin_id, admin_message_text, parse_mode="HTML")
                print(f"[{user_id}] Application sent to admin: {admin_id}")
            except Exception as e:
                print(f"[{user_id}] Failed to send application to admin {admin_id}: {e}")

        # Foydalanuvchiga tasdiqlash xabari
        try:
            bot.send_message(
                chat_id=user_id,
                text=txt['application_received_user_confirmation'],
                reply_markup=types.ReplyKeyboardRemove()
            )
            print(f"[{user_id}] User: Application completed and confirmation sent.")
        except Exception as e:
            print(f"[{user_id}] Failed to send confirmation to user {user_id}: {e}")

        return jsonify({"status": "success", "message": "Application submitted successfully"}), 200

    except Exception as e:
        print(f"Error processing application: {e}")
        if user_id:
            try:
                bot.send_message(user_id, txt['error_occurred_try_again'])
            except Exception as tg_e:
                print(f"Failed to send error message to user {user_id}: {tg_e}")
        return jsonify({"status": "error", "message": "Internal server error: " + str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
