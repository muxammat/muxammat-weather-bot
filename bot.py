import requests
import telebot
from datetime import datetime
import pytz
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import threading

# 🔑 TOKENLARNI O'RNATING
BOT_TOKEN = '8266304877:AAG1wxIG1aCg2oHRMg85ckbz_o1h8ddUGiI'
WEATHER_API_KEY = 'ae380cd9153ca59445270bc98a32c532'

bot = telebot.TeleBot(BOT_TOKEN)

# Foydalanuvchilar: {chat_id: {'lang': 'uz', 'city': 'Tashkent', 'timezone': 'Asia/Tashkent'}}
users = {}

# Til lug'atlari — 8 ta til
LANG = {
    'uz': {
        'start': "👋 Salom! Ob-havo botiga xush kelibsiz!\n\n📌 Shahar nomini yozing — hozirgi ob-havo\n📅 /forecast shahar — 5 kunlik bashorat\n📍 Lokatsiya yuboring — GPS orqali ob-havo\n⚙️ /language — Tilni o'zgartirish\n🏙️ /cities — Tez shaharlar\n🔔 Avtomatik xabarlar: 08:00 (kunduzi) va 20:00 (kechqurun)",
        'lang_set': "✅ Til o'zgartirildi: O'zbekcha",
        'city_set': "✅ Shahar tanlandi: {}",
        'city_not_found': "❌ Shahar topilmadi.",
        'weather_in': "📍 {} ob-havosi:",
        'time_morning': "🌅 Kunduzi (08:00)",
        'time_evening': "🌙 Kechqurun (20:00)",
        'temp': "Harorat",
        'feels_like': "His qilinadi",
        'night': "Kechasi",
        'sunrise': "Quyosh chiqishi",
        'sunset': "Quyosh botishi",
        'humidity': "Namlik",
        'wind': "Shamol",
        'pressure': "Bosim",
        'forecast_title': "📅 {} — 5 kunlik ob-havo bashorati",
        'choose_lang': "Tilni tanlang:",
        'choose_city': "Tez-tez ishlatiladigan shaharlardan tanlang:"
    },
    'en': {
        'start': "👋 Hello! Welcome to Weather Bot!\n\n📌 Type city name — current weather\n📅 /forecast city — 5-day forecast\n📍 Send location — weather by GPS\n⚙️ /language — Change language\n🏙️ /cities — Quick cities\n🔔 Auto messages: 08:00 (morning) & 20:00 (evening)",
        'lang_set': "✅ Language changed: English",
        'city_set': "✅ City set: {}",
        'city_not_found': "❌ City not found.",
        'weather_in': "📍 Weather in {}:",
        'time_morning': "🌅 Morning (08:00)",
        'time_evening': "🌙 Evening (20:00)",
        'temp': "Temperature",
        'feels_like': "Feels like",
        'night': "Night",
        'sunrise': "Sunrise",
        'sunset': "Sunset",
        'humidity': "Humidity",
        'wind': "Wind",
        'pressure': "Pressure",
        'forecast_title': "📅 {} — 5-day weather forecast",
        'choose_lang': "Choose language:",
        'choose_city': "Choose from quick cities:"
    },
    'ru': {
        'start': "👋 Привет! Добро пожаловать в бот погоды!\n\n📌 Введите название города — текущая погода\n📅 /forecast город — прогноз на 5 дней\n📍 Отправьте местоположение — погода по GPS\n⚙️ /language — Сменить язык\n🏙️ /cities — Быстрые города\n🔔 Авто сообщения: 08:00 (утром) и 20:00 (вечером)",
        'lang_set': "✅ Язык изменен: Русский",
        'city_set': "✅ Город выбран: {}",
        'city_not_found': "❌ Город не найден.",
        'weather_in': "📍 Погода в {}:",
        'time_morning': "🌅 Утром (08:00)",
        'time_evening': "🌙 Вечером (20:00)",
        'temp': "Температура",
        'feels_like': "Ощущается как",
        'night': "Ночью",
        'sunrise': "Восход",
        'sunset': "Закат",
        'humidity': "Влажность",
        'wind': "Ветер",
        'pressure': "Давление",
        'forecast_title': "📅 {} — прогноз погоды на 5 дней",
        'choose_lang': "Выберите язык:",
        'choose_city': "Выберите из быстрых городов:"
    },
    'ky': {
        'start': "👋 Салам! Об-абыр ботуна кош келиңиз!\n\n📌 Шаардын атын жазыңыз — азыркы об-абыр\n📅 /forecast шаар — 5 күндүк башорот\n📍 GPS аркылуу жайгашууну жөнөтүңүз\n⚙️ /language — Тилди өзгөртүү\n🏙️ /cities — Тез шаарлар\n🔔 Авто билдирүүлөр: 08:00 (түштөн мурда) жана 20:00 (кечинде)",
        'lang_set': "✅ Тил өзгөрдү: Кыргызча",
        'city_set': "✅ Шаар тандалды: {}",
        'city_not_found': "❌ Шаар табылган жок.",
        'weather_in': "📍 {} об-абыры:",
        'time_morning': "🌅 Түштөн мурда (08:00)",
        'time_evening': "🌙 Кечинде (20:00)",
        'temp': "Температура",
        'feels_like': "Туюлган температура",
        'night': "Түнкүсүн",
        'sunrise': "Күн чыгышы",
        'sunset': "Күн батышы",
        'humidity': "Ылгалдуулук",
        'wind': "Шамал",
        'pressure': "Басым",
        'forecast_title': "📅 {} — 5 күндүк об-абыр башороту",
        'choose_lang': "Тилди тандаңыз:",
        'choose_city': "Тез шаарлардан тандаңыз:"
    },
    'kk': {
        'start': "👋 Сәлем! Ауа райы ботына қош келдіңіз!\n\n📌 Қаланың атын жазыңыз — ағымдағы ауа райы\n📅 /forecast қала — 5 күндік болжам\n📍 GPS арқылы орналасуын жіберіңіз\n⚙️ /language — Тілді өзгерту\n🏙️ /cities — Жылдам қалалар\n🔔 Авто хабарламалар: 08:00 (таңертең) және 20:00 (кешке)",
        'lang_set': "✅ Тіл өзгертілді: Қазақша",
        'city_set': "✅ Қала таңдалды: {}",
        'city_not_found': "❌ Қала табылмады.",
        'weather_in': "📍 {} ауа райы:",
        'time_morning': "🌅 Таңертең (08:00)",
        'time_evening': "🌙 Кешке (20:00)",
        'temp': "Температура",
        'feels_like': "Сезілетін температура",
        'night': "Түнде",
        'sunrise': "Күн шығу",
        'sunset': "Күн бату",
        'humidity': "Ылғалдылық",
        'wind': "Жел",
        'pressure': "Қысым",
        'forecast_title': "📅 {} — 5 күндік ауа райы болжамы",
        'choose_lang': "Тілді таңдаңыз:",
        'choose_city': "Жылдам қалалардан таңдаңыз:"
    },
    'hi': {
        'start': "👋 नमस्ते! मौसम बॉट में आपका स्वागत है!\n\n📌 शहर का नाम टाइप करें — वर्तमान मौसम\n📅 /forecast शहर — 5 दिन का पूर्वानुमान\n📍 स्थान भेजें — GPS द्वारा मौसम\n⚙️ /language — भाषा बदलें\n🏙️ /cities — त्वरित शहर\n🔔 ऑटो संदेश: 08:00 (सुबह) और 20:00 (शाम)",
        'lang_set': "✅ भाषा बदल गई: हिंदी",
        'city_set': "✅ शहर सेट: {}",
        'city_not_found': "❌ शहर नहीं मिला।",
        'weather_in': "📍 {} में मौसम:",
        'time_morning': "🌅 सुबह (08:00)",
        'time_evening': "🌙 शाम (20:00)",
        'temp': "तापमान",
        'feels_like': "महसूस होता है",
        'night': "रात",
        'sunrise': "सूर्योदय",
        'sunset': "सूर्यास्त",
        'humidity': "आर्द्रता",
        'wind': "हवा",
        'pressure': "दबाव",
        'forecast_title': "📅 {} — 5 दिन का मौसम पूर्वानुमान",
        'choose_lang': "भाषा चुनें:",
        'choose_city': "त्वरित शहरों में से चुनें:"
    },
    'de': {
        'start': "👋 Hallo! Willkommen beim Wetter-Bot!\n\n📌 Stadtname eingeben — aktuelles Wetter\n📅 /forecast Stadt — 5-Tage-Vorhersage\n📍 Standort senden — Wetter per GPS\n⚙️ /language — Sprache ändern\n🏙️ /cities — Schnellstädte\n🔔 Auto-Nachrichten: 08:00 (morgens) & 20:00 (abends)",
        'lang_set': "✅ Sprache geändert: Deutsch",
        'city_set': "✅ Stadt festgelegt: {}",
        'city_not_found': "❌ Stadt nicht gefunden.",
        'weather_in': "📍 Wetter in {}:",
        'time_morning': "🌅 Morgens (08:00)",
        'time_evening': "🌙 Abends (20:00)",
        'temp': "Temperatur",
        'feels_like': "Fühlt sich an wie",
        'night': "Nacht",
        'sunrise': "Sonnenaufgang",
        'sunset': "Sonnenuntergang",
        'humidity': "Luftfeuchtigkeit",
        'wind': "Wind",
        'pressure': "Druck",
        'forecast_title': "📅 {} — 5-Tage-Wettervorhersage",
        'choose_lang': "Sprache wählen:",
        'choose_city': "Aus Schnellstädten wählen:"
    },
    'ja': {
        'start': "👋 こんにちは！天気ボットへようこそ！\n\n📌 都市名を入力 — 現在の天気\n📅 /forecast 都市 — 5日間予報\n📍 位置情報を送信 — GPSによる天気\n⚙️ /language — 言語を変更\n🏙️ /cities — クイック都市\n🔔 自動メッセージ: 08:00 (朝) & 20:00 (夜)",
        'lang_set': "✅ 言語が変更されました: 日本語",
        'city_set': "✅ 都市設定: {}",
        'city_not_found': "❌ 都市が見つかりません。",
        'weather_in': "📍 {} の天気:",
        'time_morning': "🌅 朝 (08:00)",
        'time_evening': "🌙 夜 (20:00)",
        'temp': "気温",
        'feels_like': "体感温度",
        'night': "夜間",
        'sunrise': "日の出",
        'sunset': "日の入り",
        'humidity': "湿度",
        'wind': "風",
        'pressure': "気圧",
        'forecast_title': "📅 {} — 5日間天気予報",
        'choose_lang': "言語を選択:",
        'choose_city': "クイック都市から選択:"
    }
}

# Ob-havo rasmlari
ICON_URL = "http://openweathermap.org/img/wn/{}@2x.png"

# Scheduler
scheduler = BackgroundScheduler(timezone="UTC")
scheduler.start()

# /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    uid = message.chat.id
    if uid not in users:
        users[uid] = {'lang': 'uz', 'city': 'Tashkent', 'timezone': 'Asia/Tashkent'}
    lang = users[uid]['lang']
    bot.reply_to(message, LANG[lang]['start'])

# /language
@bot.message_handler(commands=['language'])
def choose_language(message):
    markup = telebot.types.InlineKeyboardMarkup()
    langs = [
        ("🇺🇿 O'zbekcha", "uz"),
        ("🇬🇧 English", "en"),
        ("🇷🇺 Русский", "ru"),
        ("🇰🇬 Кыргызча", "ky"),
        ("🇰🇿 Қазақша", "kk"),
        ("🇮🇳 हिंदी", "hi"),
        ("🇩🇪 Deutsch", "de"),
        ("🇯🇵 日本語", "ja")
    ]
    buttons = [telebot.types.InlineKeyboardButton(text, callback_data=f"lang_{code}") for text, code in langs]
    markup.add(*buttons)
    bot.send_message(message.chat.id, "🌍 " + LANG['uz']['choose_lang'], reply_markup=markup)

# Callback — tilni o'zgartirish
@bot.callback_query_handler(func=lambda call: call.data.startswith('lang_'))
def set_language(call):
    lang_code = call.data.split('_')[1]
    uid = call.message.chat.id
    if uid not in users:
        users[uid] = {'lang': 'uz', 'city': 'Tashkent', 'timezone': 'Asia/Tashkent'}
    users[uid]['lang'] = lang_code
    bot.answer_callback_query(call.id, "✅ " + LANG[lang_code]['lang_set'])
    bot.edit_message_text(
        chat_id=uid,
        message_id=call.message.message_id,
        text="✅ " + LANG[lang_code]['lang_set']
    )

# /cities
@bot.message_handler(commands=['cities'])
def quick_cities(message):
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    cities = ["Tashkent", "Bishkek", "Almaty", "Delhi", "Berlin", "Tokyo", "Moscow", "London"]
    buttons = [telebot.types.InlineKeyboardButton(city, callback_data=f"city_{city}") for city in cities]
    markup.add(*buttons)
    lang = users.get(message.chat.id, {}).get('lang', 'uz')
    bot.send_message(message.chat.id, LANG[lang]['choose_city'], reply_markup=markup)

# Callback — shahar tanlash
@bot.callback_query_handler(func=lambda call: call.data.startswith('city_'))
def quick_city_weather(call):
    city = call.data.split('_', 1)[1]
    uid = call.message.chat.id
    if uid not in users:
        users[uid] = {'lang': 'uz', 'city': 'Tashkent', 'timezone': 'Asia/Tashkent'}
    users[uid]['city'] = city
    tz_map = {
        "Tashkent": "Asia/Tashkent",
        "Bishkek": "Asia/Bishkek",
        "Almaty": "Asia/Almaty",
        "Delhi": "Asia/Kolkata",
        "Berlin": "Europe/Berlin",
        "Tokyo": "Asia/Tokyo",
        "Moscow": "Europe/Moscow",
        "London": "Europe/London"
    }
    users[uid]['timezone'] = tz_map.get(city, "UTC")
    lang = users[uid]['lang']
    bot.answer_callback_query(call.id, LANG[lang]['city_set'].format(city))
    bot.edit_message_text(
        chat_id=uid,
        message_id=call.message.message_id,
        text=LANG[lang]['city_set'].format(city)
    )

# /forecast
@bot.message_handler(commands=['forecast'])
def forecast(message):
    try:
        parts = message.text.split(' ', 1)
        if len(parts) < 2:
            lang = users.get(message.chat.id, {}).get('lang', 'uz')
            bot.reply_to(message, f"ℹ️ {LANG[lang]['forecast_title'].format('')} — /forecast Tashkent")
            return
        city = parts[1].strip()
        show_forecast(message, city)
    except Exception as e:
        print("Forecast xato:", e)

def show_forecast(message, city):
    try:
        url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=en"
        res = requests.get(url)
        data = res.json()
        if data["cod"] != "200":
            lang = users.get(message.chat.id, {}).get('lang', 'uz')
            bot.reply_to(message, LANG[lang]['city_not_found'])
            return

        city_name = data["city"]["name"]
        lang = users.get(message.chat.id, {}).get('lang', 'uz')
        msg = f"📅 <b>{LANG[lang]['forecast_title'].format(city_name)}</b>\n\n"

        seen_days = set()
        temps = []
        days = []
        for item in data["list"]:
            dt = datetime.fromtimestamp(item["dt"])
            day_str = dt.strftime("%Y-%m-%d")
            if day_str in seen_days:
                continue
            seen_days.add(day_str)
            if len(seen_days) > 5:
                break
            temp = item["main"]["temp"]
            temps.append(temp)
            days.append(dt.strftime('%a'))

        max_temp = max(temps) if temps else 25
        for i, temp in enumerate(temps):
            bar = "█" * int(temp / max_temp * 10)
            msg += f"<b>{days[i]}</b>: {bar} {temp}°C\n"

        msg += "\n" + get_forecast_emoji_summary(data)
        bot.send_message(message.chat.id, msg, parse_mode="HTML")

    except Exception as e:
        print("show_forecast xato:", e)

def get_forecast_emoji_summary(data):
    desc_set = set()
    for item in data["list"][:8]:
        desc = item["weather"][0]["description"]
        if "rain" in desc: desc_set.add("🌧️")
        elif "snow" in desc: desc_set.add("❄️")
        elif "cloud" in desc: desc_set.add("☁️")
        elif "sun" in desc: desc_set.add("☀️")
    return " ".join(desc_set) if desc_set else "⛅"

# Asosiy ob-havo
@bot.message_handler(func=lambda msg: True)
def get_weather(message):
    city = message.text.strip()
    uid = message.chat.id
    if uid not in users:
        users[uid] = {'lang': 'uz', 'city': 'Tashkent', 'timezone': 'Asia/Tashkent'}
    users[uid]['city'] = city
    show_weather_by_city(message, city)

def show_weather_by_city(message, city):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=en"
        res = requests.get(url)
        data = res.json()
        if data.get("cod") != 200:
            lang = users.get(message.chat.id, {}).get('lang', 'uz')
            bot.reply_to(message, LANG[lang]['city_not_found'])
            return
        show_weather(message, data)
    except Exception as e:
        print("show_weather_by_city xato:", e)

def show_weather(message, data):
    uid = message.chat.id
    lang = users.get(uid, {}).get('lang', 'uz')
    L = LANG[lang]

    temp = data["main"]["temp"]
    feels_like = data["main"]["feels_like"]
    humidity = data["main"]["humidity"]
    pressure = data["main"]["pressure"]
    wind = data["wind"]["speed"]
    desc = data["weather"][0]["description"].capitalize()
    city_name = data.get("name", "???")
    icon_code = data["weather"][0]["icon"]

    sunrise = datetime.fromtimestamp(data["sys"]["sunrise"]).strftime('%H:%M')
    sunset = datetime.fromtimestamp(data["sys"]["sunset"]).strftime('%H:%M')

    emoji = "🌡️" if temp > 25 else "❄️" if temp < 0 else "🌤️"

    msg = (
        f"{emoji} <b>{L['weather_in'].format(city_name)}</b>\n\n"
        f"🌡️ <b>{L['temp']}</b>: {temp}°C ({L['feels_like']}: {feels_like}°C)\n"
        f"🌙 <b>{L['night']}</b>: {data['main']['temp_min']}°C\n"
        f"🌅 <b>{L['sunrise']}</b>: {sunrise} | <b>{L['sunset']}</b>: {sunset}\n"
        f"💧 <b>{L['humidity']}</b>: {humidity}%\n"
        f"🌬️ <b>{L['wind']}</b>: {wind} m/s\n"
        f"🔽 <b>{L['pressure']}</b>: {pressure} hPa\n"
        f"☁️ <b>{desc}</b>"
    )

    photo_url = ICON_URL.format(icon_code)
    try:
        bot.send_photo(message.chat.id, photo_url, caption=msg, parse_mode="HTML")
    except:
        bot.send_message(message.chat.id, msg, parse_mode="HTML")

# 🌅 Kunduzgi avtomatik xabar — 08:00
def send_morning_reports():
    for uid, user_data in users.items():
        try:
            city = user_data['city']
            lang = user_data['lang']
            L = LANG[lang]
            tz = pytz.timezone(user_data['timezone'])

            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=en"
            res = requests.get(url)
            data = res.json()
            if data.get("cod") != 200:
                continue

            temp = data["main"]["temp"]
            desc = data["weather"][0]["description"].capitalize()
            icon_code = data["weather"][0]["icon"]

            msg = f"🌅 <b>{L['time_morning']}</b>\n\n"
            msg += f"📍 {city}\n🌡️ {L['temp']}: {temp}°C\n☁️ {desc}"

            photo_url = ICON_URL.format(icon_code)
            try:
                bot.send_photo(uid, photo_url, caption=msg, parse_mode="HTML")
            except:
                bot.send_message(uid, msg, parse_mode="HTML")
        except Exception as e:
            print(f"Morning report xato {uid}: {e}")

# 🌙 Kechki avtomatik xabar — 20:00
def send_evening_reports():
    for uid, user_data in users.items():
        try:
            city = user_data['city']
            lang = user_data['lang']
            L = LANG[lang]
            tz = pytz.timezone(user_data['timezone'])

            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=en"
            res = requests.get(url)
            data = res.json()
            if data.get("cod") != 200:
                continue

            temp = data["main"]["temp"]
            desc = data["weather"][0]["description"].capitalize()
            icon_code = data["weather"][0]["icon"]

            msg = f"🌙 <b>{L['time_evening']}</b>\n\n"
            msg += f"📍 {city}\n🌡️ {L['temp']}: {temp}°C\n☁️ {desc}"

            photo_url = ICON_URL.format(icon_code)
            try:
                bot.send_photo(uid, photo_url, caption=msg, parse_mode="HTML")
            except:
                bot.send_message(uid, msg, parse_mode="HTML")
        except Exception as e:
            print(f"Evening report xato {uid}: {e}")

# Scheduler — 08:00 va 20:00 da xabar (Toshkent vaqtiga mos)
scheduler.add_job(send_morning_reports, CronTrigger(hour=3, minute=0, timezone='UTC'))   # 08:00 Toshkent
scheduler.add_job(send_evening_reports, CronTrigger(hour=15, minute=0, timezone='UTC'))  # 20:00 Toshkent

print("✅ Bot ishga tushdi! Telegramda sinab ko‘ring.")
bot.polling()


