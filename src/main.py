import os
import csv
import time
import cv2
import numpy as np
from datetime import datetime
from ultralytics import YOLO
from config import (
    VIDEO_SOURCE, MODEL_PATH, CONFIDENCE_THRESHOLD,
    MAX_WAIT_TIME_SECONDS, ROIS, LOG_CSV_PATH, COLORS
)

def punto_en_roi(punto, roi):
    """Verifica si un punto (cx, cy) está dentro de un rectángulo [x1, y1, x2, y2]."""
    x, y = punto
    x1, y1, x2, y2 = roi
    return x1 <= x <= x2 and y1 <= y <= y2

def inicializar_csv(ruta):
    """Crea el archivo CSV con encabezados si no existe."""
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    if not os.path.exists(ruta):
        with open(ruta, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Fecha_Hora", "ID_Cliente", "Zona", "Tiempo_Atencion_Seg"])

def registrar_evento_csv(ruta, track_id, zona, duracion):
    """Guarda un registro de atención completada."""
    with open(ruta, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            track_id,
            zona,
            round(duracion, 2)
        ])

def dibujar_dashboard(frame, clientes_actuales, flujo_total, promedio_espera, alerta_activa):
    """Superpone un panel informativo (HUD) semitransparente en la parte superior."""
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (frame.shape[1], 85), COLORS["PANEL_BG"], -1)
    cv2.addWeighted(overlay, 0.78, frame, 0.22, 0, frame)

    # Título y métricas
    cv2.putText(frame, "SMARTCAFE ANALYTICS | MONITOREO EN VIVO", (15, 25),
                cv2.FONT_HERSHEY_SIMPLEX, 0.65, COLORS["PEDIDOS"], 2)
    
    metricas_texto = (
        f"En Establecimiento: {clientes_actuales}   |   "
        f"Flujo Total Detectado: {flujo_total}   |   "
        f"Tiempo Promedio: {promedio_espera:.1f}s"
    )
    cv2.putText(frame, metricas_texto, (15, 58),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, COLORS["TEXT"], 1)

    # Indicador de Alerta Visual
    if alerta_activa:
        cv2.rectangle(frame, (frame.shape[1] - 260, 15), (frame.shape[1] - 15, 65), COLORS["ALERT"], -1)
        cv2.putText(frame, "! DEMORA EN BARRA !", (frame.shape[1] - 245, 47),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, COLORS["TEXT"], 2)

def main():
    inicializar_csv(LOG_CSV_PATH)
    print("Cargando modelo YOLOv8...")
    model = YOLO(MODEL_PATH)

    cap = cv2.VideoCapture(VIDEO_SOURCE)
    if not cap.isOpened():
        print(f"Error al abrir fuente de video: {VIDEO_SOURCE}")
        return

    # Estructuras de estado para seguimiento y cronometraje
    ids_historicos = set()
    tiempos_inicio_pedidos = {}   # {track_id: timestamp_entrada}
    tiempos_completados = []      # Lista de duraciones en segundos

    print("Sistema iniciado. Presiona 'q' o 'ESC' para salir.")

    while True:
        ret, frame = cap.read()
        if not ret:
            # Si es un video pregrabado y llega al final, reinicia en bucle para demos
            if isinstance(VIDEO_SOURCE, str):
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue
            break

        # Ejecutar detección + seguimiento solo para la clase 0 (person en COCO)
        results = model.track(frame, persist=True, classes=[0], conf=CONFIDENCE_THRESHOLD, verbose=False)

        # Dibujar las ROIs en pantalla
        roi_p = ROIS["ZONA_PEDIDOS"]
        roi_e = ROIS["ZONA_ESPERA"]
        cv2.rectangle(frame, (roi_p[0], roi_p[1]), (roi_p[2], roi_p[3]), COLORS["PEDIDOS"], 2)
        cv2.putText(frame, "ZONA PEDIDOS (BARRA)", (roi_p[0], roi_p[1] - 8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLORS["PEDIDOS"], 2)

        cv2.rectangle(frame, (roi_e[0], roi_e[1]), (roi_e[2], roi_e[3]), COLORS["ESPERA"], 2)
        cv2.putText(frame, "ZONA ESPERA / MESAS", (roi_e[0], roi_e[1] - 8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLORS["ESPERA"], 2)

        clientes_en_frame = 0
        ids_activos_en_pedidos = set()
        alerta_demora = False

        if results[0].boxes is not None and results[0].boxes.id is not None:
            boxes = results[0].boxes.xyxy.cpu().numpy()
            track_ids = results[0].boxes.id.int().cpu().tolist()
            clientes_en_frame = len(track_ids)

            for box, track_id in zip(boxes, track_ids):
                ids_historicos.add(track_id)
                x1, y1, x2, y2 = map(int, box)

                # Punto de referencia: centro inferior (posición de los pies de la persona)
                centro_pies = (int((x1 + x2) / 2), y2)
                cv2.circle(frame, centro_pies, 5, (255, 0, 255), -1)

                color_caja = COLORS["OK"]
                etiqueta = f"ID:{track_id}"

                # Lógica de cronometraje en ZONA_PEDIDOS
                if punto_en_roi(centro_pies, roi_p):
                    ids_activos_en_pedidos.add(track_id)
                    if track_id not in tiempos_inicio_pedidos:
                        tiempos_inicio_pedidos[track_id] = time.time()

                    tiempo_actual = time.time() - tiempos_inicio_pedidos[track_id]
                    etiqueta += f" | Atencion: {tiempo_actual:.1f}s"

                    if tiempo_actual > MAX_WAIT_TIME_SECONDS:
                        color_caja = COLORS["ALERT"]
                        alerta_demora = True
                    else:
                        color_caja = COLORS["PEDIDOS"]

                elif punto_en_roi(centro_pies, roi_e):
                    color_caja = COLORS["ESPERA"]
                    etiqueta += " | Esperando"

                # Dibujar bounding box y etiqueta del cliente
                cv2.rectangle(frame, (x1, y1), (x2, y2), color_caja, 2)
                cv2.putText(frame, etiqueta, (x1, y1 - 8),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color_caja, 2)

        # Verificar clientes que salieron de la zona de pedidos para cerrar su cronómetro
        ids_salientes = [tid for tid in tiempos_inicio_pedidos if tid not in ids_activos_en_pedidos]
        for tid in ids_salientes:
            duracion_total = time.time() - tiempos_inicio_pedidos.pop(tid)
            # Filtrar micro-detecciones accidentales menores a 1.5 segundos
            if duracion_total >= 1.5:
                tiempos_completados.append(duracion_total)
                registrar_evento_csv(LOG_CSV_PATH, tid, "ZONA_PEDIDOS", duracion_total)

        # Calcular promedio de atención (incluyendo tiempos completados y activos)
        todos_los_tiempos = tiempos_completados + [
            time.time() - inicio for inicio in tiempos_inicio_pedidos.values()
        ]
        promedio = np.mean(todos_los_tiempos) if todos_los_tiempos else 0.0

        # Renderizar Dashboard
        dibujar_dashboard(frame, clientes_en_frame, len(ids_historicos), promedio, alerta_demora)

        cv2.imshow("SmartCafe Analytics - Vision Artificial", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()