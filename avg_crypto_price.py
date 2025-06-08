import requests
import time
import signal
import argparse
import logging
from collections import deque
from datetime import datetime, timezone
from tenacity import retry, wait_exponential, retry_if_exception_type, RetryError, RetryCallState

current_retry = 0
current_exception = None
shutdown_requested = False
URL = "https://api.coingecko.com/api/v3"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

class ShutdownRequested(Exception):
    pass

def update_retry_info(retry_state: RetryCallState):
    """Update retry data from retry decorator.
    Args:
        retry_state (RetryCallState): retry state
    """

    current_retry = retry_state.attempt_number
    current_exception = retry_state.outcome.exception()
    if current_retry != 0 and current_retry % 5 == 0:
        try:
            error_msg = current_exception.response.json().get("status", {}).get("error_message", str(current_exception))
            logging.error(error_msg)
        except Exception:
            raise

def signal_handler(sig, frame):
    global shutdown_requested
    shutdown_requested = True
    logging.info("Shutting down…")

@retry(wait=wait_exponential(multiplier=1, min=1, max=900), retry=retry_if_exception_type((requests.RequestException,)), before_sleep=update_retry_info)
def get_coin_symbol(coin_name: str, session: requests.Session):
    """Get coin name and return its symbol.
    Args:
        coin_name (str): name of crypto coin such as bitcoin, solana, ethereum
        session (requests.Session): Requests session for HTTP calls.
    Raises:
        Exception:  If the coin is not found (404) shutdown process else continue to retry.
    Returns:
        str: Coin symbol
    """

    if shutdown_requested:
        raise ShutdownRequested("Shutdown requested, aborting fetch.")

    url = f"{URL}/coins/{coin_name}"
    response = session.get(url)
    if response.status_code == 404:
        raise Exception(response.text)
    response.raise_for_status()
    coin_data = response.json()
    return coin_data["symbol"].upper()

@retry(wait=wait_exponential(multiplier=1, min=1, max=900), retry=retry_if_exception_type((requests.RequestException,)), before_sleep=update_retry_info)
def fetch_price(coin: str, session: requests.Session):
    """Get Price of coin
    Args:
        coin (str): coin name
        session (requests.Session): Requests session for HTTP calls.
    Raises:
        Exception: log Network exception every 5 retries else break
    Returns:
        price, formatted_timestamp: return price of coin and timestamp
    """
    if shutdown_requested:
        raise ShutdownRequested("Shutdown requested, aborting fetch.")
    url = f"{URL}/simple/price"
    params = {
        "ids": coin,
        "vs_currencies": "usd",
        "include_last_updated_at": "true"
    }
    response = session.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    price = data[coin]["usd"]
    ts_unix = data[coin]["last_updated_at"]
    timestamp = datetime.fromtimestamp(ts_unix, tz=timezone.utc)
    formatted_timestamp = timestamp.replace(tzinfo=None).strftime("%Y-%m-%dT%H:%M:%S")
    return price, formatted_timestamp


def main(coin: str, max_price_storage: int, session: requests.Session):
    """Main function that will print price and avg
    Args:
        coin (str): coin name
        max_price_storage (int): how much price to store
        session (requests.Session): Requests session for HTTP calls.
    """

    prices = deque(maxlen=max_price_storage)
    coin_symbol = get_coin_symbol(coin, session)
    while not shutdown_requested:
        try:      
            price, timestamp = fetch_price(coin, session)
        except Exception as e:
            logging.error(str(e))
            break
        prices.append(price)
        sma = sum(prices) / len(prices) if prices else 0
        print(f"[{timestamp}] {coin_symbol} → USD: ${price:,.2f}: SMA({len(prices)}): ${sma:,.2f}")
        time.sleep(1)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler) 
    # Note: CoinGecko may return identical timestamps due to update rates.
    # To reflect real-time execution, consider using local PC time instead.
    parser = argparse.ArgumentParser(description="Track live crypto price with SMA.")
    parser.add_argument(
        "--coin", 
        type=str, 
        default="bitcoin", 
        help="CoinGecko coin name ('solana','bitcoin', 'ethereum' and etc)"
    )
    parser.add_argument(
        "--sma", 
        type=int, 
        default=10, 
        help="Number of prices to use for SMA (default: 10)"
    )
    args = parser.parse_args()
    logging.info("Script is starting...")
    with requests.Session() as session:
        main(coin=args.coin.lower(), max_price_storage=args.sma, session=session)
