# ESP32-CAM · Detección de Personas en Tiempo Real

Sistema de detección de personas usando una ESP32-CAM y MobileNetSSD. Cuando se detecta una persona, el sistema guarda automáticamente una imagen con timestamp y registra el evento en una base de datos SQLite local.

> Proyecto académico — Integración Tecnológica · Escuela Da Vinci 2025  
> Agustín Agüero · Daniel Fernández · Tomás Roma

---

## Cómo funciona

1. La **ESP32-CAM** transmite video por WiFi vía HTTP
2. **Python + OpenCV** lee cada frame del stream
3. **MobileNetSSD** analiza el frame buscando la clase `person` (confianza > 60%)
4. Al detectar: guarda una imagen `.jpg` e inserta un registro con timestamp en SQLite

---

## Stack tecnológico

| Capa | Tecnología |
|------|-----------|
| Firmware | Arduino IDE / ESP32 CameraWebServer |
| Visión artificial | Python, OpenCV, MobileNetSSD |
| Base de datos | SQLite |
| Hardware | ESP32-CAM (OV2640), FTDI FT232RL, protoboard |

---

## Requisitos

### Hardware
- ESP32-CAM (OV2640)
- Módulo FTDI FT232RL (para flashear el firmware)
- Protoboard + cables Dupont
- Fuente de alimentación 5V 2A

### Software
```
Python 3.x
opencv-python
numpy
```

Instalación de dependencias:
```bash
pip install opencv-python numpy
```

También necesitás los archivos del modelo MobileNetSSD:
- `MobileNetSSD_deploy.prototxt.txt`
- `MobileNetSSD_deploy.caffemodel`

Disponibles en el [Caffe Model Zoo oficial](https://github.com/chuanqi305/MobileNet-SSD).

---

## Configuración

### 1. Flashear la ESP32-CAM

Abrí Arduino IDE, cargá el ejemplo **CameraWebServer** y configurá:

```cpp
#define CAMERA_MODEL_AI_THINKER
const char* ssid = "TU_SSID_WIFI";
const char* password = "TU_CONTRASEÑA_WIFI";
```

Conectá por FTDI, flasheá y abrí el Monitor Serie a 115200 baudios para obtener la IP asignada.

### 2. Actualizá la URL del stream

En `detection.py`, reemplazá la IP por la que aparece en el Monitor Serie:

```python
URL = "http://192.168.0.90:81/stream"  # cambiar por la IP de tu ESP32-CAM
```

### 3. Ejecutar el script de detección

```bash
python detection.py
```

El script va a:
- Abrir una ventana con el stream en vivo y los bounding boxes
- Guardar las imágenes detectadas en `./fotos/`
- Registrar cada detección en `detecciones.db`
- Imprimir `[INFO] Persona detectada - Imagen guardada: ...` en cada evento

Presioná `q` para salir.

---

## Estructura del proyecto

```
ESP32CAM-Integracion/
├── arduino/
│   └── CameraWebServer/     # Firmware del ESP32
├── detection.py             # Script principal de detección
├── MobileNetSSD_deploy.prototxt.txt
├── MobileNetSSD_deploy.caffemodel
├── fotos/                   # Se crea automáticamente, guarda las imágenes
└── detecciones.db           # Base de datos SQLite (se crea automáticamente)
```

---

## Esquema de la base de datos

```sql
CREATE TABLE detecciones (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    ruta_imagen TEXT,
    timestamp   TEXT
);
```

---

## Resultados de pruebas

| Escenario | Esperado | Resultado |
|-----------|----------|-----------|
| Sin personas en campo visual | No se guarda imagen | ✅ Sin falsos positivos |
| Persona centrada y cercana | Detección + imagen guardada | ✅ Menos de 1 segundo |
| Vista parcial o de espaldas | Detección parcial o nula | ⚠️ Menor confiabilidad |
| Objeto grande no humano | No se guarda imagen | ✅ Correcto |

---

## Limitaciones conocidas

- Menor precisión con iluminación deficiente
- Una sola imagen por frame aunque haya múltiples personas
- Sin lógica de seguimiento por ID ni conteo simultáneo

---

## Mejoras futuras

- Dashboard web para visualización remota de capturas
- Lógica anti-duplicados para presencia continua
- Alertas automáticas por WhatsApp o email
- Integración con almacenamiento en la nube

---

## Demo

[▶ Ver video de funcionamiento](https://drive.google.com/file/d/1WqUNKyCy_fsNr-WHfrOON-O9C9V0U4ru/view?usp=sharing)

---

## Costo del hardware (Argentina, junio 2025)

| Componente | Precio (ARS) |
|------------|-------------|
| ESP32-CAM | $12.350 |
| FTDI FT232RL | $5.652 |
| Protoboard 830 puntos | $2.732 |
| Kit cables Dupont | $6.380 |
| **Total** | **$26.980** |
