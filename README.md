
  

# 📈 PricePulse – Live Crypto Price Tracker with SMA

  

**Track live cryptocurrency prices and calculate Simple Moving Average (SMA)** with automatic retries, graceful shutdown, and error logging.

  

## 🚀 Getting Started

### ✅ Prerequisites

  

1.  **Install Python 3.12 or higher (if not already installed)**

Download: [https://www.python.org/downloads/](https://www.python.org/downloads/)

2.  **Install Poetry (if not already installed)**

Run in Command Prompt:

`pip install poetry`

3.  **Install Dependencies**

In your terminal, navigate to the project root and run:

`poetry install`

This sets up a virtual environment and installs all required packages.

## ⚙️ How to Run

  

### Option 1: Run via IDE

  

Open `avg_crypto_price.py` in your IDE and execute it directly.

You can pass optional arguments for the coin and SMA .

  

### Option 2: Run from Terminal

Navigate to the project folder and run:

`poetry run python avg_crypto_price.py`

  

**Default:**

- Coin: `bitcoin`

- SMA window: `10`

  

**Example with arguments:**

`poetry run python avg_crypto_price.py --coin solana --sma 10`

  

## 🧠 Features

  

- ✅ Track any crypto coin supported by CoinGecko.

- ✅ Customizable SMA window (default: 10 prices).

- ✅ Fetch and display coin symbol automatically.

- ✅ Graceful shutdown with Ctrl+C (SIGINT).

- ✅ Robust retry logic with exponential backoff (up to 15 minutes).

- ✅ Every 5th retry logs error details.

  

----------

  

## 📊 Performance & Limitations

  

- Script is lightweight (~100 lines).

- Rapid requests (e.g. every 1s).

- Retry intervals grow exponentially: 1s → 2s → 4s → ... → max 900s (15min).

- After exceeding the rate limit, the script continues retrying every 15 minutes until success.

----------

  

## 🛠 Improvements (Planned)

  

- Accept **coin symbol** instead of full name (e.g., `xrp` instead of `ripple`).

- Log to a file (already implemented with rotation support).
- Do not save same result if already exist (sametimestamp)
- Add more filters.
- Export price and SMA history to CSV or a database.
- Control Maximum Exponential Wait Growth
- Proxy and Header Random Rotation
- Because of the update rate from CoinGecko, we sometimes see the same timestamp multiple times, this can be changed to use the PC time if we need the exact time of execution.