import cv2
import time
import sqlite3
import numpy as np
import os
from datetime import datetime

print("[INFO] Cargando modelo...")
net = cv2.dnn.readNetFromCaffe("MobileNetSSD_deploy.prototxt.txt", "MobileNetSSD_deploy.caffemodel")
print("[INFO] Modelo cargado correctamente.")

CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
           "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
           "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
           "sofa", "train", "tvmonitor"]

conn = sqlite3.connect("detecciones.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS detecciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ruta_imagen TEXT,
    timestamp TEXT
)
""")
conn.commit()

# Crear carpeta fotos si no existe
os.makedirs("fotos", exist_ok=True)
print(f"[INFO] Carpeta 'fotos' creada en: {os.path.abspath('fotos')}")

URL = "http://192.168.0.90:81/stream" 
cap = cv2.VideoCapture(URL)

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error al leer frame")
        continue

    (h, w) = frame.shape[:2]
    blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)),
                                 0.007843, (300, 300), 127.5)
    net.setInput(blob)
    detections = net.forward()

    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > 0.6:
            idx = int(detections[0, 0, i, 1])
            if CLASSES[idx] == "person":
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (startX, startY, endX, endY) = box.astype("int")
                label = f"{CLASSES[idx]}: {confidence:.2f}"

                cv2.rectangle(frame, (startX, startY), (endX, endY), (0, 255, 0), 2)
                cv2.putText(frame, label, (startX, startY - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                now = datetime.now()
                nombre_img = now.strftime("foto_%Y%m%d_%H%M%S.jpg")
                ruta = f"./fotos/{nombre_img}"
                cv2.imwrite(ruta, frame)

                cursor.execute("INSERT INTO detecciones (ruta_imagen, timestamp) VALUES (?, ?)",
                               (ruta, now.strftime("%Y-%m-%d %H:%M:%S")))
                conn.commit()

                print(f"[INFO] Persona detectada - Imagen guardada: {ruta}")
                time.sleep(3)
                break

    cv2.imshow("ESP32-CAM Stream", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
conn.close()
