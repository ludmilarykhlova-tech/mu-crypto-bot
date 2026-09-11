import time
import threading
import requests
import telebot
from telebot import types

# ВСТАВЬ СВОЙ ТОКЕН ОТ @BotFather
TELEGRAM_BOT_TOKEN = '8463298964:AAHBdkyysGktadTs-zrR5dxHzLU-5ZtzBKg'

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

authorized_users = set()
processed_tokens = set()
alerts_enabled = True

# Краткая история/описание популярных монет
COIN_DESCRIPTIONS = {
    "BTC": "👑 *Bitcoin (BTC)* — первая и самая известная криптовалюта в мире, созданная в 2009 году человеком (или группой) под псевдонимом Сатоши Накамото. Основа всей криптоиндустрии.",
    "ETH": "💎 *Ethereum (ETH)* — крупнейшая платформа для смарт-контрактов и децентрализованных приложений (dApps), созданная Виталиком Бутериным в 2015 году.",
    "SOL": "🔥 *Solana (SOL)* — высокоскоростной блокчейн с практически нулевыми комиссиями. Главная площадка для запуска современных мемкоинов и NFT.",
    "BNB": "🟡 *BNB (BNB)* — нативный токен экосистемы Binance и сети BNB Chain. Используется для скидок на комиссии и участия в Launchpool.",
    "TON": "✈️ *Toncoin (TON)* — блокчейн, изначально разработанный командой Telegram. Интегрирован прямо в экосистему мессенджера.",
    "DOGE": "🐕 *Dogecoin (DOGE)* — легендарный мемкоин с собакой Сиба-ину, созданный в 2013 году ради шутки, но ставший культовым благодаря Илону Маску.",
    "XRP": "⚡ *XRP (Ripple)* — токен, созданный для быстрых и дешевых международных банковских переводов."
}

def get_main_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn_top = types.KeyboardButton("🔝 Топ Монеты")
    btn_trends = types.KeyboardButton("🚀 Тренды DexScreener")
    btn_alerts = types.KeyboardButton("⚙️ Статус сигналов")
    btn_help = types.KeyboardButton("❓ Помощь")
    
    btn_btc = types.KeyboardButton("👑 BTC")
    btn_sol = types.KeyboardButton("🔥 SOL")
    btn_eth = types.KeyboardButton("💎 ETH")
    btn_ton = types.KeyboardButton("✈️ TON")
    
    keyboard.add(btn_top, btn_trends)
    keyboard.add(btn_btc, btn_sol, btn_eth, btn_ton)
    keyboard.add(btn_alerts, btn_help)
    return keyboard

@bot.message_handler(commands=['start'])
def start_message(message):
    chat_id = message.chat.id
    if chat_id in authorized_users:
        bot.send_message(
            chat_id, 
            "👋 Добро пожаловать обратно!\n\n"
            "Выбирай монету из меню ниже или напиши любой тикер/контракт токена:",
            reply_markup=get_main_keyboard(),
            parse_mode="Markdown"
        )
    else:
        bot.send_message(chat_id, "Привет! Введи пароль для доступа к боту:")

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    chat_id = message.chat.id
    text = message.text.strip()

    # Авторизация
    if chat_id not in authorized_users:
        if text.lower() == PASSWORD:
            authorized_users.add(chat_id)
            bot.send_message(
                chat_id, 
                "✅ Пароль верный! Доступ разрешен.\n\nПользуйся кнопками меню или отправляй любой тикер монеты:",
                reply_markup=get_main_keyboard()
            )
        else:
            bot.send_message(chat_id, "❌ Неверный пароль!")
        return

    # Кнопки меню
    if text == "⚙️ Статус сигналов":
        status = "ВКЛЮЧЕНЫ 🔔" if alerts_enabled else "ВЫКЛЮЧЕНЫ 🔕"
        bot.send_message(
            chat_id, 
            f"⚙️ *Настройки авто-сканера мемкоинов*\n\n"
            f"Текущий статус: *{status}*\n\n"
            f"Команды управления:\n"
            f"• /alerts_on — включить сигналы\n"
            f"• /alerts_off — выключить сигналы", 
            parse_mode="Markdown"
        )
        return

    if text == "❓ Помощь":
        bot.send_message(
            chat_id,
            "💡 *Как пользоваться ботом:*\n\n"
            "1. Нажимай на любую кнопку в меню для быстрого просмотра.\n""2. Введи любой тикер (например: PEPE, DOGE, SUI, AVAX, SHIB).\n"
            "3. Бот автоматически пришлет карточку монеты с логотипом, ценой, изменением за 24 часа и историей/описанием!\n"
            "4. Сканер автоматически находит свежие мемкоины на Solana и отправляет сигналы с логотипом.",
            parse_mode="Markdown"
        )
        return

    if text == "🔝 Топ Монеты":
        bot.send_message(
            chat_id,
            "🏆 *Главные монеты рынка:*\nНажимай на кнопки BTC, SOL, ETH, TON ниже или отправляй их названия!",
            parse_mode="Markdown"
        )
        return

    if text == "🚀 Тренды DexScreener":
        try:
            res = requests.get("https://api.dexscreener.com/latest/dex/search?q=solana")
            pairs = res.json().get("pairs", [])[:5]
            msg = "🔥 *Топ-5 горячих мемкоинов Solana прямо сейчас:*\n\n"
            for p in pairs:
                name = p.get("baseToken", {}).get("name", "Unknown")
                sym = p.get("baseToken", {}).get("symbol", "???")
                price = p.get("priceUsd", "0")
                url = p.get("url", "")
                msg += f"• *{name}* (${sym}) — ${float(price):,.6f} | [DexScreener]({url})\n"
            bot.send_message(chat_id, msg, parse_mode="Markdown", disable_web_page_preview=True)
        except Exception:
            bot.send_message(chat_id, "Ошибка при получении трендов.")
        return

    # Очистка введенного тикера
    clean_ticker = text.replace("👑 ", "").replace("🔥 ", "").replace("💎 ", "").replace("✈️ ", "").strip().upper()
    
    # 1. Поиск в DexScreener (находит ВСЕ монеты, новые/старые, с фото и сетями)
    try:
        res = requests.get(f"https://api.dexscreener.com/latest/dex/search?q={clean_ticker}")
        if res.status_code == 200:
            pairs = res.json().get("pairs", [])
            if pairs:
                pair = pairs[0]
                price = float(pair.get("priceUsd", 0))
                token_name = pair.get("baseToken", {}).get("name", clean_ticker)
                token_sym = pair.get("baseToken", {}).get("symbol", clean_ticker)
                chain = pair.get("chainId", "crypto").upper()
                change_24h = pair.get("priceChange", {}).get("h24", 0)
                liquidity = pair.get("liquidity", {}).get("usd", 0)
                fdv = pair.get("fdv", 0)
                url = pair.get("url", "")
                
                info = pair.get("info", {})
                photo_url = info.get("imageUrl") if info else None

                direction = "🟢" if change_24h >= 0 else "🔴"
                
                # Подтягиваем описание если есть в базе или генерируем стандартное
                desc = COIN_DESCRIPTIONS.get(token_sym, f"ℹ️ *Описание:* Монета {token_name} торгуется в сети *{chain}*.")
                
                caption = (f"📊 *{token_name}* (${token_sym})\n"
                           f"🌐 Сеть: *{chain}*\n\n"
                           f"💰 Цена: *${price:,.6f}*\n"
                           f"{direction} Изменение 24ч: *{change_24h:+.2f}%*\n"
                           f"💧 Ликвидность: *${liquidity:,.0f}*\n"
                           f"💎 Капитализация (FDV): *${fdv:,.0f}*\n\n"
                           f"{desc}\n\n"
                           f"🔗 [График на DexScreener]({url})")
                
                if photo_url:
                    try:
                        bot.send_photo(chat_id, photo_url, caption=caption, parse_mode="Markdown", reply_markup=get_main_keyboard())
                        return
                    except Exception:
                        pass
                
                bot.send_message(chat_id, caption, parse_mode="Markdown", reply_markup=get_main_keyboard())
                return
    except Exception as e:
        print("Ошибка поиска:", e)

    bot.send_message(chat_id, f"❌ Монета {clean_ticker} не найдена. Проверь правильность написания тикера.", parse_mode="Markdown")def broadcast_signal(msg, photo_url):
    for user_id in list(authorized_users):
        try:
            if photo_url:
                bot.send_photo(user_id, photo_url, caption=msg, parse_mode="Markdown")
            else:
                bot.send_message(user_id, msg, parse_mode="Markdown")
        except Exception:
            pass

def check_market():
    while True:
        if alerts_enabled and authorized_users:
            try:
                res = requests.get("https://api.dexscreener.com/latest/dex/search?q=solana")
                data = res.json()
                pairs = data.get("pairs", [])
                
                for pair in pairs:
                    if pair.get("chainId") != "solana":
                        continue
                    
                    liquidity = pair.get("liquidity", {}).get("usd", 0)
                    volume5m = pair.get("volume", {}).get("m5", 0)
                    pair_addr = pair.get("pairAddress")
                    
                    if liquidity > 1000 and volume5m > 100 and pair_addr not in processed_tokens:
                        processed_tokens.add(pair_addr)
                        
                        token_name = pair.get("baseToken", {}).get("name", "Unknown")
                        token_symbol = pair.get("baseToken", {}).get("symbol", "UNKNOWN")
                        fdv = pair.get("fdv", 0)
                        url = pair.get("url", "")
                        info = pair.get("info", {})
                        photo_url = info.get("imageUrl") if info else None
                        
                        msg = (f"🚀 *Новый мемкоин на Solana!*\n\n"
                               f"📌 Имя: *{token_name}* (${token_symbol})\n"
                               f"💧 Ликвидность: *${liquidity:,.0f}*\n"
                               f"📊 Объем 5м: *${volume5m:,.0f}*\n"
                               f"💎 FDV: *${fdv:,.0f}*\n\n"
                               f"🔗 [Открыть на DexScreener]({url})")
                        
                        broadcast_signal(msg, photo_url)
            except Exception as e:
                print("Ошибка сканирования:", e)
        
        time.sleep(15)

if __name__ == '__main__':
    threading.Thread(target=check_market, daemon=True).start()
    print("Бот запущен и ждет пользователей...")
    bot.polling(none_stop=True)
