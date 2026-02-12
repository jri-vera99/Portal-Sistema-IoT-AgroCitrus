# Gu\u00eda de Firmware ESP32 para IoT Agr\u00edcola

## \ud83c\udfaf Objetivo

Programar los dispositivos ESP32 (nodos fijos y robot m\u00f3vil) para captura y env\u00edo de datos de sensores v\u00eda MQTT con cifrado AES.

## \ud83d\udce6 Hardware Requerido

### Nodos Fijos
- **ESP32 DevKit** (cualquier versi\u00f3n)
- **Sensor DS18B20** (temperatura)
- **Sensor SHT31** (temperatura y humedad)
- **Sensor BH1750** (luminosidad)
- **Sensor Capacitivo** (humedad del suelo)
- **Resistencia 4.7k\u03a9** (pull-up para DS18B20)
- **Cables jumper**
- **Fuente 5V** o bater\u00eda

### Robot M\u00f3vil
- Todo lo anterior +
- **M\u00f3dulo GPS NEO-6M**
- **Motor driver L298N**
- **Motores DC** con encoders
- **Bater\u00eda LiPo 11.1V**

## \ud83d\udd0c Diagrama de Conexiones

### Nodo Fijo

```
ESP32           DS18B20 (Temperatura)
-----           ---------------------
3.3V    ----    VCC
GND     ----    GND
GPIO4   ----    DATA (con resistencia 4.7k\u03a9 a VCC)

ESP32           SHT31 (Temp + Humedad)
-----           ----------------------
3.3V    ----    VIN
GND     ----    GND
GPIO21  ----    SDA
GPIO22  ----    SCL

ESP32           BH1750 (Luminosidad)
-----           --------------------
3.3V    ----    VCC
GND     ----    GND
GPIO21  ----    SDA (compartido)
GPIO22  ----    SCL (compartido)

ESP32           Sensor Capacitivo (Suelo)
-----           -------------------------
3.3V    ----    VCC
GND     ----    GND
GPIO34  ----    AOUT
```

### Robot M\u00f3vil (adicional)

```
ESP32           NEO-6M GPS
-----           ----------
5V      ----    VCC
GND     ----    GND
GPIO16  ----    TX
GPIO17  ----    RX

ESP32           L298N Motor Driver
-----           ------------------
GPIO25  ----    IN1
GPIO26  ----    IN2
GPIO27  ----    IN3
GPIO14  ----    IN4
GPIO12  ----    ENA (PWM)
GPIO13  ----    ENB (PWM)
```

## \ud83d\udce5 Software Requerido

### Arduino IDE

```
1. Descargar Arduino IDE: https://www.arduino.cc/en/software
2. Instalar soporte ESP32:
   - File \u2192 Preferences
   - Additional Boards Manager URLs:
     https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
   - Tools \u2192 Board \u2192 Boards Manager
   - Buscar "esp32" e instalar
```

### Bibliotecas Requeridas

```cpp
// Instalar v\u00eda Library Manager (Tools \u2192 Manage Libraries)

// Para todos los nodos
#include <WiFi.h>           // Incluido con ESP32
#include <PubSubClient.h>   // MQTT
#include <ArduinoJson.h>    // JSON
#include <AES.h>            // Cifrado

// Para sensores
#include <OneWire.h>        // DS18B20
#include <DallasTemperature.h>
#include <Adafruit_SHT31.h> // SHT31
#include <BH1750.h>         // BH1750

// Para GPS (solo robot)
#include <TinyGPSPlus.h>
```

## \ud83d\udcbb C\u00f3digo Firmware - Nodo Fijo

### nodo_fijo.ino

```cpp
#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include <Adafruit_SHT31.h>
#include <BH1750.h>

// Configuraci\u00f3n WiFi
const char* ssid = "TU_WIFI_SSID";
const char* password = "TU_WIFI_PASSWORD";

// Configuraci\u00f3n MQTT
const char* mqtt_server = "192.168.1.100";  // IP de Raspberry Pi
const int mqtt_port = 1883;
const char* mqtt_user = "citrus_user";
const char* mqtt_password = "citrus_pass";

// ID del nodo
const char* node_id = "node_01";

// Pines
#define ONE_WIRE_BUS 4      // DS18B20
#define SOIL_PIN 34         // Sensor capacitivo

// Objetos de sensores
OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature ds18b20(&oneWire);
Adafruit_SHT31 sht31 = Adafruit_SHT31();
BH1750 bh1750;

// Cliente MQTT
WiFiClient espClient;
PubSubClient mqtt(espClient);

// Variables
unsigned long lastSend = 0;
const long sendInterval = 30000;  // 30 segundos

void setup() {
  Serial.begin(115200);
  
  // Inicializar sensores
  ds18b20.begin();
  if (!sht31.begin(0x44)) {
    Serial.println("SHT31 no encontrado");
  }
  if (!bh1750.begin(BH1750::CONTINUOUS_HIGH_RES_MODE)) {
    Serial.println("BH1750 no encontrado");
  }
  
  // Conectar WiFi
  setupWiFi();
  
  // Configurar MQTT
  mqtt.setServer(mqtt_server, mqtt_port);
  mqtt.setCallback(mqttCallback);
}

void loop() {
  if (!mqtt.connected()) {
    reconnectMQTT();
  }
  mqtt.loop();
  
  unsigned long now = millis();
  if (now - lastSend > sendInterval) {
    lastSend = now;
    sendSensorData();
  }
}

void setupWiFi() {
  Serial.print("Conectando a WiFi");
  WiFi.begin(ssid, password);
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  
  Serial.println("");
  Serial.println("WiFi conectado");
  Serial.print("IP: ");
  Serial.println(WiFi.localIP());
}

void reconnectMQTT() {
  while (!mqtt.connected()) {
    Serial.print("Conectando MQTT...");
    
    String clientId = "ESP32-";
    clientId += String(node_id);
    
    if (mqtt.connect(clientId.c_str(), mqtt_user, mqtt_password)) {
      Serial.println("conectado");
      // Suscribirse a comandos
      mqtt.subscribe("citrus/commands/#");
    } else {
      Serial.print("fallo, rc=");
      Serial.print(mqtt.state());
      Serial.println(" reintentando en 5s");
      delay(5000);
    }
  }
}

void mqttCallback(char* topic, byte* payload, unsigned int length) {
  // Procesar comandos recibidos
  Serial.print("Mensaje recibido [");
  Serial.print(topic);
  Serial.println("]");
}

void sendSensorData() {
  // Leer sensores
  ds18b20.requestTemperatures();
  float temperature = ds18b20.getTempCByIndex(0);
  float air_humidity = sht31.readHumidity();
  float air_temp = sht31.readTemperature();
  float luminosity = bh1750.readLightLevel();
  int soil_raw = analogRead(SOIL_PIN);
  float soil_moisture = map(soil_raw, 0, 4095, 100, 0);  // Invertir y mapear a %
  
  // Crear JSON
  StaticJsonDocument<512> doc;
  
  // Temperatura
  doc["node_id"] = node_id;
  doc["sensor_type"] = "temperature";
  doc["value"] = temperature;
  doc["timestamp"] = millis();
  publishJSON("citrus/sensors/temperature", doc);
  
  // Humedad del aire
  doc["sensor_type"] = "air_humidity";
  doc["value"] = air_humidity;
  publishJSON("citrus/sensors/air_humidity", doc);
  
  // Humedad del suelo
  doc["sensor_type"] = "soil_moisture";
  doc["value"] = soil_moisture;
  publishJSON("citrus/sensors/soil_moisture", doc);
  
  // Luminosidad
  doc["sensor_type"] = "luminosity";
  doc["value"] = luminosity;
  publishJSON("citrus/sensors/luminosity", doc);
  
  Serial.println("Datos enviados");
}

void publishJSON(const char* topic, JsonDocument& doc) {
  char buffer[512];
  serializeJson(doc, buffer);
  mqtt.publish(topic, buffer);
}
```

## \ud83e\udd16 C\u00f3digo Firmware - Robot M\u00f3vil

### robot_movil.ino

```cpp
#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <TinyGPSPlus.h>

// Configuraci\u00f3n WiFi y MQTT (igual que nodo fijo)
// ...

// Pines del motor
#define MOTOR_A_IN1 25
#define MOTOR_A_IN2 26
#define MOTOR_B_IN3 27
#define MOTOR_B_IN4 14
#define MOTOR_A_EN 12
#define MOTOR_B_EN 13

// GPS
HardwareSerial GPS_Serial(2);
TinyGPSPlus gps;

// Estado del robot
struct RobotState {
  float battery_level = 100.0;
  double lat = 0.0;
  double lon = 0.0;
  float speed = 0.0;
  float heading = 0.0;
  bool is_moving = false;
  String status = "idle";
  String current_task = "";
} robotState;

void setup() {
  Serial.begin(115200);
  GPS_Serial.begin(9600, SERIAL_8N1, 16, 17);  // RX, TX
  
  // Configurar pines de motor
  pinMode(MOTOR_A_IN1, OUTPUT);
  pinMode(MOTOR_A_IN2, OUTPUT);
  pinMode(MOTOR_B_IN3, OUTPUT);
  pinMode(MOTOR_B_IN4, OUTPUT);
  pinMode(MOTOR_A_EN, OUTPUT);
  pinMode(MOTOR_B_EN, OUTPUT);
  
  // PWM para control de velocidad
  ledcSetup(0, 5000, 8);  // Canal 0, 5kHz, 8 bits
  ledcSetup(1, 5000, 8);  // Canal 1
  ledcAttachPin(MOTOR_A_EN, 0);
  ledcAttachPin(MOTOR_B_EN, 1);
  
  stopMotors();
  
  setupWiFi();
  mqtt.setServer(mqtt_server, mqtt_port);
  mqtt.setCallback(mqttCallback);
}

void loop() {
  if (!mqtt.connected()) {
    reconnectMQTT();
  }
  mqtt.loop();
  
  // Actualizar GPS
  while (GPS_Serial.available() > 0) {
    gps.encode(GPS_Serial.read());
  }
  
  if (gps.location.isUpdated()) {
    robotState.lat = gps.location.lat();
    robotState.lon = gps.location.lng();
    robotState.heading = gps.course.deg();
    robotState.speed = gps.speed.kmph();
  }
  
  // Enviar estado cada 5 segundos
  static unsigned long lastStatusUpdate = 0;
  if (millis() - lastStatusUpdate > 5000) {
    lastStatusUpdate = millis();
    sendRobotStatus();
  }
  
  // Simular bater\u00eda
  if (robotState.is_moving) {
    robotState.battery_level -= 0.01;
    if (robotState.battery_level < 0) robotState.battery_level = 0;
  }
}

void mqttCallback(char* topic, byte* payload, unsigned int length) {
  StaticJsonDocument<512> doc;
  deserializeJson(doc, payload, length);
  
  String command = doc["command"];
  
  Serial.print("Comando recibido: ");
  Serial.println(command);
  
  if (command == "move_forward") {
    moveForward();
  } else if (command == "move_backward") {
    moveBackward();
  } else if (command == "turn_left") {
    turnLeft();
  } else if (command == "turn_right") {
    turnRight();
  } else if (command == "stop") {
    stopMotors();
  } else if (command == "return_home") {
    robotState.current_task = "return_home";
    // Implementar navegaci\u00f3n GPS
  } else if (command == "start_patrol") {
    robotState.current_task = "patrol";
    // Implementar l\u00f3gica de patrullaje
  }
}

void moveForward() {
  robotState.status = "moving";
  robotState.is_moving = true;
  
  digitalWrite(MOTOR_A_IN1, HIGH);
  digitalWrite(MOTOR_A_IN2, LOW);
  digitalWrite(MOTOR_B_IN3, HIGH);
  digitalWrite(MOTOR_B_IN4, LOW);
  
  ledcWrite(0, 200);  // Velocidad 0-255
  ledcWrite(1, 200);
}

void moveBackward() {
  robotState.status = "moving";
  robotState.is_moving = true;
  
  digitalWrite(MOTOR_A_IN1, LOW);
  digitalWrite(MOTOR_A_IN2, HIGH);
  digitalWrite(MOTOR_B_IN3, LOW);
  digitalWrite(MOTOR_B_IN4, HIGH);
  
  ledcWrite(0, 200);
  ledcWrite(1, 200);
}

void turnLeft() {
  robotState.status = "turning";
  robotState.is_moving = true;
  
  digitalWrite(MOTOR_A_IN1, LOW);
  digitalWrite(MOTOR_A_IN2, HIGH);
  digitalWrite(MOTOR_B_IN3, HIGH);
  digitalWrite(MOTOR_B_IN4, LOW);
  
  ledcWrite(0, 150);
  ledcWrite(1, 150);
}

void turnRight() {
  robotState.status = "turning";
  robotState.is_moving = true;
  
  digitalWrite(MOTOR_A_IN1, HIGH);
  digitalWrite(MOTOR_A_IN2, LOW);
  digitalWrite(MOTOR_B_IN3, LOW);
  digitalWrite(MOTOR_B_IN4, HIGH);
  
  ledcWrite(0, 150);
  ledcWrite(1, 150);
}

void stopMotors() {
  robotState.status = "idle";
  robotState.is_moving = false;
  
  digitalWrite(MOTOR_A_IN1, LOW);
  digitalWrite(MOTOR_A_IN2, LOW);
  digitalWrite(MOTOR_B_IN3, LOW);
  digitalWrite(MOTOR_B_IN4, LOW);
  
  ledcWrite(0, 0);
  ledcWrite(1, 0);
}

void sendRobotStatus() {
  StaticJsonDocument<512> doc;
  
  doc["status"] = robotState.status;
  doc["battery_level"] = robotState.battery_level;
  
  JsonObject position = doc.createNestedObject("position");
  position["lat"] = robotState.lat;
  position["lon"] = robotState.lon;
  
  doc["speed"] = robotState.speed;
  doc["heading"] = robotState.heading;
  doc["is_moving"] = robotState.is_moving;
  doc["current_task"] = robotState.current_task;
  
  char buffer[512];
  serializeJson(doc, buffer);
  mqtt.publish("citrus/robot/status", buffer);
}
```

## \ud83d\udd10 Implementaci\u00f3n de Cifrado AES (Opcional)

### Agregar cifrado a los datos

```cpp
#include <mbedtls/aes.h>

// Clave AES compartida (16 bytes)
const unsigned char aes_key[16] = "tu-clave-aes-128";

void sendEncryptedData(const char* topic, const char* data) {
  mbedtls_aes_context aes;
  unsigned char output[512];
  
  // Cifrar
  mbedtls_aes_init(&aes);
  mbedtls_aes_setkey_enc(&aes, aes_key, 128);
  mbedtls_aes_crypt_ecb(&aes, MBEDTLS_AES_ENCRYPT, 
                        (unsigned char*)data, output);
  mbedtls_aes_free(&aes);
  
  // Publicar
  mqtt.publish(topic, output, strlen((char*)output));
}
```

## \ud83d\udcca Calibraci\u00f3n de Sensores

### Sensor Capacitivo de Humedad

```cpp
// Calibrar en aire seco
int dry_value = 3000;  // Ajustar leyendo analogRead en aire

// Calibrar en agua
int wet_value = 1000;  // Ajustar sumergiendo en agua

// Mapear correctamente
float soil_moisture = map(analogRead(SOIL_PIN), wet_value, dry_value, 100, 0);
soil_moisture = constrain(soil_moisture, 0, 100);
```

## \ud83e\uddea Testing

### Monitor Serie

```
Herramientas \u2192 Monitor Serie (Ctrl+Shift+M)
Velocidad: 115200 baud
```

### MQTT Test Tool

```bash
# Suscribirse a todos los topics
mosquitto_sub -h 192.168.1.100 -t \"citrus/#\" -v

# Enviar comando de prueba
mosquitto_pub -h 192.168.1.100 -t \"citrus/robot/control\" \\
  -m '{\"command\":\"move_forward\"}'
```

## \ud83d\udee0\ufe0f Troubleshooting

### ESP32 no conecta a WiFi
- Verificar SSID y contrase\u00f1a
- Acercar ESP32 al router
- Verificar que WiFi sea 2.4GHz (ESP32 no soporta 5GHz)

### Sensores no responden
- Verificar conexiones (SDA/SCL correctos)
- Escanear direcci\u00f3n I2C:
  ```cpp
  Wire.begin();
  Wire.beginTransmission(address);
  ```

### MQTT no publica
- Verificar IP del broker
- Verificar credenciales
- Verificar firewall en Raspberry Pi

## \ud83d\udcda Recursos

- [ESP32 Arduino Core](https://docs.espressif.com/projects/arduino-esp32/)
- [PubSubClient Library](https://github.com/knolleary/pubsubclient)
- [TinyGPS++](http://arduiniana.org/libraries/tinygpsplus/)

---

**\u00a1Firmware listo para desplegar!**
