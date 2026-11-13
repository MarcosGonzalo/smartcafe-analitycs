# Configuración general de SmartCafé Analytics

# Fuente de video: 0 para Webcam en vivo, o ruta a un video (ej. "data/cafe_demo.mp4")
VIDEO_SOURCE = "data/video_1.mp4"

# Modelo YOLOv8 (yolov8n.pt es el más ligero y rápido para correr en CPU/Laptop)
MODEL_PATH = "yolov8n.pt"
CONFIDENCE_THRESHOLD = 0.45

# Umbral de alerta en segundos (si un cliente espera más de este tiempo en barra, salta alerta)
MAX_WAIT_TIME_SECONDS = 15.0  # Ajustado a 15s para demostraciones rápidas en clase

# Coordenadas de las Regiones de Interés (ROI) en formato [x1, y1, x2, y2]
# Puedes recalibrar estos valores ejecutando: python src/calibrator.py
ROIS = {
    "ZONA_PEDIDOS": [323, 183, 594, 535],
    "ZONA_ESPERA":  [548, 161, 1066, 720]
}
# Archivo de registro histórico de atenciones
LOG_CSV_PATH = "data/registro_atenciones.csv"

# Paleta de colores BGR para OpenCV
COLORS = {
    "OK": (46, 204, 113),        # Verde
    "ALERT": (0, 0, 255),        # Rojo intenso
    "PEDIDOS": (241, 196, 15),   # Amarillo/Dorado
    "ESPERA": (52, 152, 219),    # Azul
    "PANEL_BG": (30, 30, 30),    # Gris oscuro para HUD
    "TEXT": (255, 255, 255)      # Blanco
}