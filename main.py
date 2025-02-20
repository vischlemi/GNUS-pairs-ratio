import json
import os

# Function to create an empty JSON file if it doesn't exist
def initialize_json_file():
    if not os.path.exists("data.json"):
        with open("data.json", "w") as file:
            json.dump({}, file)  # Save an empty dictionary in JSON file

# Call function at startup
initialize_json_file()








import requests
import time
import os
import json  # ✅ Use JSON instead of Replit db
from decimal import Decimal, getcontext

# Set high precision for calculations
getcontext().prec = 10

# Define the trading pairs (Ethereum & Polygon)
PAIR_1 = {
    "blockchain": "ethereum",
    "address": "0xF10E8cCdb3F065BF24AFA14d08cc6336d4a9A281"
}

PAIR_2 = {
    "blockchain": "polygon",
    "address": "0x45126b956401DAaec92aFba2a9953E14B16fb83f"
}

# Threshold for notification
THRESHOLD = Decimal("3")

# Load Telegram Bot Credentials securely
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  # ✅ Use environment variables
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Function to send a Telegram message
def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    requests.post(url, json=payload)

# Function to fetch price from DexScreener API
def get_price(blockchain, pair_address):
    url = f"https://api.dexscreener.com/latest/dex/pairs/{blockchain}/{pair_address}"
    response = requests.get(url).json()

    try:
        price = Decimal(str(response["pairs"][0]["priceUsd"]))
        return price
    except (KeyError, IndexError, TypeError):
        print(f"⚠️ Error fetching price for {pair_address}")
        return None

# Function to save price to a JSON file instead of Replit db
def save_price_to_file(pair_key, price):
    data = load_prices()
    data[pair_key] = str(price)  # Store as string to avoid JSON serialization issues

    with open("data.json", "w") as file:
        json.dump(data, file)

# Function to get last stored price from JSON file
def get_last_price(pair_key):
    data = load_prices()
    return Decimal(data.get(pair_key, "0"))  # Default to 0 if no previous price

# Function to load stored prices from the JSON file
def load_prices():
    try:
        with open("data.json", "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

# Track price changes
while True:
    # Get current prices
    price_1 = get_price(PAIR_1["blockchain"], PAIR_1["address"])
    price_2 = get_price(PAIR_2["blockchain"], PAIR_2["address"])

    # Get last stored prices
    last_price_1 = get_last_price("PAIR_1")
    last_price_2 = get_last_price("PAIR_2")

    # Check if price has changed before updating
    if price_1 and price_2 and (price_1 != last_price_1 or price_2 != last_price_2):
        ratio = price_1 / price_2
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

        # Print live data
        print(f"[{timestamp}] ✅ Ratio: {ratio:.10f} (ETH Pair: {price_1}, MATIC Pair: {price_2})")

        update = f"✅ Ratio: {ratio:.2f}\nETH Pair: {price_1}\nMATIC Pair: {price_2}"
        send_telegram_alert(update)
        print(f"📲 Telegram updated")

        # Save new prices to JSON file
        save_price_to_file("PAIR_1", price_1)
        save_price_to_file("PAIR_2", price_2)

        # 🚨 Send Telegram alert if ratio exceeds threshold
        if ratio > THRESHOLD:
            alert_message = f"🚨 ALERT! Ratio exceeded {THRESHOLD}: {ratio:.4f} 🚀"
            send_telegram_alert(alert_message)
            print(f"📲 Telegram alert sent: {alert_message}")

    time.sleep(9)  # Check for updates every 9 seconds
