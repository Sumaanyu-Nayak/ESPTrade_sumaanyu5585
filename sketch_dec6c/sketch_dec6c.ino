#include <WiFi.h>
#include <HTTPClient.h>
#include <Arduino_JSON.h>

// WiFi credentials
const char* ssid = "Your_SSID";
const char* password = "Your_PASSWORD";

// API URLs
const char* alphaVantageUrl = "https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=AAPL&interval=1min&apikey=your_api_key";
const char* serverUrl = "http://<your-python-server-ip>:3300/process-data";

// Simulation Variables
float cash = 10000.00; // Starting cash balance
int holdings = 0;      // Number of shares owned
float stockPrice = 0.00; // Latest stock price

// Timing Variables
unsigned long previousMillis = 0;
const long interval = 60000; // Fetch data every minute

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi");
}

void loop() {
  unsigned long currentMillis = millis();
  if (currentMillis - previousMillis >= interval) {
    previousMillis = currentMillis;
    fetchStockData();
  }
}

void fetchStockData() {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    WiFiClientSecure client;
    client.setInsecure(); // Disable SSL certificate validation for simplicity

    http.begin(client, alphaVantageUrl);

    int httpResponseCode = http.GET();
    if (httpResponseCode == 200) {
      String response = http.getString();
      Serial.println("Stock data fetched successfully:");
      Serial.println(response);

      // Parse and send data to Python server
      sendDataToServer(response);
    } else {
      Serial.printf("Error fetching stock data: %d\n", httpResponseCode);
    }
    http.end();
  } else {
    Serial.println("WiFi not connected");
  }
}

void sendDataToServer(String stockData) {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    WiFiClient client;

    http.begin(client, serverUrl);
    http.addHeader("Content-Type", "application/json");

    int httpResponseCode = http.POST(stockData);
    if (httpResponseCode > 0) {
      String response = http.getString();
      Serial.println("Decision received from server:");
      Serial.println(response);

      // Execute trade based on server's decision
      executeTrade(response);
    } else {
      Serial.printf("Error sending data to server: %d\n", httpResponseCode);
    }
    http.end();
  } else {
    Serial.println("WiFi not connected");
  }
}

void executeTrade(String response) {
  JSONVar jsonResponse = JSON.parse(response);
  if (JSON.typeof(jsonResponse) == "undefined") {
    Serial.println("Parsing error");
    return;
  }

  String signal = jsonResponse["signal"];
  String reason = jsonResponse["reason"];
  stockPrice = jsonResponse["status"]["stock_price"]; // Update stock price if included
  Serial.println("Trade Signal: " + signal);
  Serial.println("Reason: " + reason);

  // Execute trade based on the signal
  if (signal == "BUY" && cash >= stockPrice) {
    holdings += 1;
    cash -= stockPrice;
    Serial.printf("Executed BUY: New Cash = $%.2f, Holdings = %d\n", cash, holdings);
  } else if (signal == "SELL" && holdings > 0) {
    holdings -= 1;
    cash += stockPrice;
    Serial.printf("Executed SELL: New Cash = $%.2f, Holdings = %d\n", cash, holdings);
  } else {
    Serial.println("No trade executed (HOLD or insufficient funds/holdings)");
  }
}
