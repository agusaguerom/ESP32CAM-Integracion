import cv2
import time
import sqlite3
import numpy as np
import os
from datetime import datetime


# Se cargan los modelos de reconocimiento
print("[INFO] Cargando modelo...")
net = cv2.dnn.readNetFromCaffe("MobileNetSSD_deploy.prototxt.txt", "MobileNetSSD_deploy.caffemodel")
print("[INFO] Modelo cargado correctamente.")


# Se declaran las clases del modelo (en este proyecto unicamente se utilizara PERSON)
CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
           "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
           "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
           "sofa", "train", "tvmonitor"]

# Declaracion de variables globales a utilizar
ultima_deteccion = 0 
cooldown = 5  # Segundos entre fotos
deteccion_total = 0 # Cantidad de detecciones

# Se conecta o crea la base de datos junto a la tabla detecciones
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

# Se crea la carpeta fotos si no existe
os.makedirs("fotos", exist_ok=True)
print(f"[INFO] Carpeta 'fotos' creada en: {os.path.abspath('fotos')}")


# Se Captura el video del ESP32-CAM
URL = "http://192.168.0.90:81/stream" # Es necesario cambiar la direccion IP por la proporcionada en ARDUINO IDE
cap = cv2.VideoCapture(URL)



while True:
    ret, frame = cap.read() # Se lee el frame de la imagen
    if not ret: # Condicional en caso de no poder leer el frame
        print("Error al leer frame")
        continue

    (h, w) = frame.shape[:2] # Se obtiene el alto y el ancho del fram

    # Agregar fecha y hora actual en el frame
    now_dt = datetime.now()
    timestamp_str = now_dt.strftime("%Y-%m-%d %H:%M:%S")
    cv2.putText(frame, timestamp_str, (10, h - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    # Mostrar cantidad total de detecciones arriba a la izquierda
    cv2.putText(frame, f"Detecciones: {deteccion_total}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    # Procesamiento con MobileNet SSD
    #Se redimensiona el frame y se convierte en blob para mayor entendimiento en python
    blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)),
                                 0.007843, (300, 300), 127.5)
    net.setInput(blob)
    detections = net.forward() # Realiza la deteccion y sus resultados

    now = time.time() #Variable con el tiempo actual

    #Se recorre cada deteccion 
    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2] # Confianzaz o probabilidad de la deteccion
        if confidence > 0.6: # Se muestran las detecciones con probabilidad mayor a 60%
            idx = int(detections[0, 0, i, 1]) #indice de la clase detectada
            if CLASSES[idx] == "person": # Condicional cuando se encuentra una persona 
                #Coordenadas de las personas para que sean marcadas en el rectangulo verde (bounding box)
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h]) 
                (startX, startY, endX, endY) = box.astype("int")

                #Texto mostrado en el bounding box
                label = f"{CLASSES[idx]}: {confidence:.2f}"

                # Dibujar cuadro y etiqueta
                cv2.rectangle(frame, (startX, startY), (endX, endY), (0, 255, 0), 2)
                cv2.putText(frame, label, (startX, startY - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                # Verificar cooldown
                if now - ultima_deteccion > cooldown:
                    deteccion_total += 1  # Contador total de las detecciones


                    #Codigo para nombrar y guardar la imagen en la carpeta foros
                    nombre_img = now_dt.strftime("foto_%Y%m%d_%H%M%S.jpg")
                    ruta = f"./fotos/{nombre_img}"
                    cv2.imwrite(ruta, frame)

                    # Inserta en la base de datos la ruta de la imagen y horario de la detección.
                    cursor.execute("INSERT INTO detecciones (ruta_imagen, timestamp) VALUES (?, ?)",
                                   (ruta, now_dt.strftime("%Y-%m-%d %H:%M:%S")))
                    conn.commit()

                    ultima_deteccion = now # Se Actualiza la última detección guardada.
                    print(f"[INFO] Persona detectada - Imagen guardada: {ruta}")
                break # Sale del bucle for después de detectar y guardar una persona para evitar múltiples detecciones a la vez.

    # Se Muestra el video en una nueva Ventana
    cv2.imshow("ESP32-CAM Stream", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'): # Si el usuario presiona la letra q, termina el programa.
        break

cap.release()
cv2.destroyAllWindows()
conn.close()
