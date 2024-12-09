
# Stock Trading Simulation with ESP32S3 and Python

This project demonstrates a simulated stock trading system where an ESP32S3 fetches live stock data from the Alpha Vantage API and communicates with a Python server to make trading decisions. The Python server processes the data, makes decisions using technical indicators, and simulates trade execution.

---

## Project Overview

### Components
1. **ESP32S3 Firmware**:
   - Fetches live stock data from the Alpha Vantage API.
   - Sends the data to the Python server for decision-making.
   - Displays server responses and executes trades in a simulated environment.

2. **Python Server**:
   - Processes stock data using technical indicators (e.g., EMAs).
   - Simulates trade execution by updating cash and holdings.
   - Logs trades in an SQLite database.

---

## Logic

### ESP32S3 Workflow
1. Connects to Wi-Fi.
2. Fetches stock data from Alpha Vantage API.
3. Sends the data to the Python server via an HTTP POST request.
4. Receives a trade decision (`BUY`, `SELL`, or `HOLD`) from the server.
5. Simulates trade execution based on the decision.

### Python Server Workflow
1. Receives stock data from the ESP32S3.
2. Processes the data to calculate Exponential Moving Averages (EMAs).
3. Makes a trading decision based on EMA crossovers:
   - **BUY**: Short EMA crosses above Long EMA.
   - **SELL**: Short EMA crosses below Long EMA.
   - **HOLD**: No significant crossover.
4. Simulates trade execution by updating:
   - **Cash**: Adjusted for buys and sells.
   - **Holdings**: Number of stocks owned.
5. Logs the trade in an SQLite database.

---

## Installation

### 1. Requirements

#### Hardware
- ESP32S3 board
- USB cable
- Internet connection

#### Software
- Python 3.x
- Arduino IDE (configured for ESP32)
- Required Python libraries:
  ```bash
  pip install flask pandas flask-cors numpy pandas
  ```

### 2. Set Up the Python Server
1. Save the Python server code as `tradingBot2.py`.
2. Run the server:
   ```bash
   python tradingBot2.py
   ```
3. The server listens on port `3300` by default.

---

### 3. Set Up the ESP32S3

#### Alpha Vantage API Key
1. Sign up for a free Alpha Vantage API key at [https://www.alphavantage.co/](https://www.alphavantage.co/).
2. Replace `your_api_key` in the ESP32S3 code with your actual API key.

#### Wi-Fi Credentials
Replace `Your_SSID` and `Your_PASSWORD` with your Wi-Fi network's credentials in the ESP32S3 code.

#### Upload the Code
1. Open the ESP32S3 code in the Arduino IDE.
2. Install the necessary ESP32 libraries if not already installed.
3. Select the correct ESP32S3 board and COM port.
4. Upload the code to the ESP32S3.

---

## Usage

### ESP32S3
1. Monitor the ESP32S3's output via the Serial Monitor.
2. The ESP32S3 fetches stock data every minute, sends it to the Python server, and displays the server's response.

### Python Server
1. Processes stock data and logs trades in an SQLite database (`trades.db`).
2. Access trade logs via the `/get-trades` endpoint:
   ```bash
   curl http://127.0.0.1:3300/get-trades
   ```

---

## File Descriptions

### 1. `tradingBot2.py` (Python Server)
#### Purpose
- Processes stock data received from ESP32S3.
- Calculates EMAs to make trading decisions.
- Simulates trade execution by updating cash and holdings.
- Logs trades in an SQLite database.

#### Endpoints
1. **`/process-data`**:
   - Accepts stock data (JSON).
   - Returns a trading decision (`BUY`, `SELL`, or `HOLD`), stock price, cash, and holdings.
2. **`/get-trades`**:
   - Returns the trade history from the SQLite database.

---

### 2. ESP32S3 Firmware
#### Purpose
- Fetches live stock data from Alpha Vantage API.
- Sends data to the Python server.
- Simulates trade execution based on the server's decision.

#### Key Functions
1. **`fetchStockData()`**:
   - Fetches live stock data from Alpha Vantage API.
   - Logs data to the Serial Monitor.
2. **`sendDataToServer()`**:
   - Sends stock data to the Python server.
   - Logs the server's decision.
3. **`executeTrade()`**:
   - Simulates trade execution by updating cash and holdings.

---

## Example Outputs

### ESP32S3 Serial Monitor
```plaintext
Connected to WiFi
Stock data fetched successfully:
{"Meta Data": {...}, "Time Series (1min)": {...}}
Decision received from server:
{"signal": "BUY", "reason": "Short EMA crossed above Long EMA", "stock_price": 242.55, "cash": 9757.45, "holdings": 1}
Executed BUY: New Cash = $9757.45, Holdings = 1
```

### Python Server Logs
1. **Decision Response**:
   ```json
   {
       "signal": "BUY",
       "reason": "Short EMA crossed above Long EMA",
       "stock_price": 242.55,
       "cash": 9757.45,
       "holdings": 1
   }
   ```
2. **Trade History (`/get-trades`)**:
   ```json
   [
       {
           "id": 1,
           "timestamp": "2024-12-06T20:00:00",
           "signal": "BUY",
           "reason": "Short EMA crossed above Long EMA",
           "stock_price": 242.55,
           "cash": 9757.45,
           "holdings": 1
       }
   ]
   ```

---

## Enhancements

### 1. Dynamic Indicators
- Add support for more indicators like RSI, MACD, or Bollinger Bands.

### 2. Persistent Storage on ESP32
- Use SPIFFS or EEPROM to store simulation data (`cash`, `holdings`).

### 3. Error Handling
- Handle API rate limits and network failures.

### 4. Real Trade Execution
- Integrate with a trading API (e.g., Alpaca, Binance) for real trades.

---