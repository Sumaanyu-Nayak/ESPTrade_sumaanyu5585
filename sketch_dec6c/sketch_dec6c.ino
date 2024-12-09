#include <WiFi.h>
#include <HTTPClient.h>
#include <WiFiClientSecure.h>

// WiFi credentials
const char* ssid = "Sharanagati";
const char* password = "nirvana123";

// API and Backend URLs
const char* alphaVantageApiUrl = "https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=AAPL&interval=1min&apikey=TR9PI01Q7OW018TD";
const char* backendUrl = "http://192.168.1.3:3300/data-new";

unsigned long previousMillis = 0;
const long interval = 120000; // Fetch data every 2 minutes

void setup() {
  Serial.begin(115200);

  // Connect to WiFi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi");
  Serial.println(WiFi.localIP());
}

void loop() {
  unsigned long currentMillis = millis();
  // Serial.println("In loop");
  fetchAndSendData();
  delay(interval);
  // if (currentMillis - previousMillis >= interval) {
  //   previousMillis = currentMillis;
  //   Serial.println("Starting");
  //   fetchAndSendData();
  // }
}

void fetchAndSendData() {
  if (WiFi.status() == WL_CONNECTED) {
    WiFiClientSecure client;
    client.setInsecure(); // For simplicity, disable certificate validation (use CA certificates for better security)
    HTTPClient http;

    Serial.println("Fetching stock data from Alpha Vantage...");

    http.begin(client, alphaVantageApiUrl);
    int httpResponseCode = http.GET();

    if (httpResponseCode > 0) {
      Serial.printf("HTTP Response Code: %d\n", httpResponseCode);
      String response = http.getString();

      if (httpResponseCode == 200) {
        Serial.println("Data fetched successfully");
        sendDataToBackend(response);
      } else {
        Serial.println("Error in API response");
        Serial.println(response);
      }
    } else {
      Serial.printf("Error fetching data: %s\n", http.errorToString(httpResponseCode).c_str());
    }

    http.end();
  } else {
    Serial.println("WiFi not connected");
  }
}

void sendDataToBackend(String jsonData) {
  Serial.println(jsonData);
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    WiFiClient client;

    Serial.println("Sending data to backend...");

    http.begin(client, backendUrl);
    http.addHeader("Content-Type", "application/json");

    int httpResponseCode = http.POST(jsonData);
    if (httpResponseCode > 0) {
      Serial.printf("Data sent successfully. Response Code: %d\n", httpResponseCode);
      String response = http.getString();
      Serial.println("Backend Response: " + response);
    } else {
      Serial.printf("Error sending data: %s\n", http.errorToString(httpResponseCode).c_str());
    }

    http.end();
  } else {
    Serial.println("WiFi not connected");
  }
}
