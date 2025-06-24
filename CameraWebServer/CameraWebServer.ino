#include "esp_camera.h"
#include <WiFi.h>

#define CAMERA_MODEL_AI_THINKER 

#include "camera_pins.h"

// ===========================
// CREDENCIALES WIFI
// ===========================
const char* ssid = "Personal Wifi611 2.4-2.4GHz";
const char* password = "00421551236";

void startCameraServer();

void setup() {
  Serial.begin(115200);
  Serial.setDebugOutput(true);
  Serial.println();

  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sscb_sda = SIOD_GPIO_NUM;
  config.pin_sscb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  
  // Ajuste de calidad y búfer para mejor streaming
  config.pixel_format = PIXFORMAT_JPEG;  
  if (psramFound()) {
    config.frame_size = FRAMESIZE_SVGA;   // 800x600,  resolución equilibrada
    config.jpeg_quality = 10;              
    config.fb_count = 2;                   
    config.grab_mode = CAMERA_GRAB_LATEST; 
    config.fb_location = CAMERA_FB_IN_PSRAM;
  } else {
    config.frame_size = FRAMESIZE_VGA;    
    config.jpeg_quality = 12;
    config.fb_count = 1;
    config.grab_mode = CAMERA_GRAB_WHEN_EMPTY;
    config.fb_location = CAMERA_FB_IN_DRAM;
  }

  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed with error 0x%x\n", err);
    return;
  }

  sensor_t * s = esp_camera_sensor_get();

  if (psramFound()) {
    s->set_framesize(s, FRAMESIZE_SVGA);
  } else {
    s->set_framesize(s, FRAMESIZE_VGA);
  }

  s->set_vflip(s, 0);       
  s->set_hmirror(s, 1);    
  s->set_brightness(s, 1);  
  s->set_saturation(s, 0);

  // Conexión WiFi
  WiFi.begin(ssid, password);
  WiFi.setSleep(false);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("WiFi connected");

  startCameraServer();

  Serial.print("Camera Ready! Use 'http://");
  Serial.print(WiFi.localIP());
  Serial.println("' to connect");
}

void loop() {
  delay(10000);
}
