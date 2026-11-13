import cv2
from config import VIDEO_SOURCE

def calibrar_rois():
    cap = cv2.VideoCapture(VIDEO_SOURCE)
    ret, frame = cap.read()
    cap.release()

    if not ret:
        print(f"Error: No se pudo leer la fuente de video ({VIDEO_SOURCE}).")
        return

    print("\n=== HERRAMIENTA DE CALIBRACIÓN DE ROIs ===")
    print("1. Arrastra el mouse para seleccionar la ZONA DE PEDIDOS (Mostrador) y presiona ENTER.")
    roi_pedidos = cv2.selectROI("Calibrador SmartCafe - Selecciona ZONA PEDIDOS", frame, showCrosshair=True)
    cv2.destroyWindow("Calibrador SmartCafe - Selecciona ZONA PEDIDOS")

    print("2. Arrastra el mouse para seleccionar la ZONA DE ESPERA / MESAS y presiona ENTER.")
    roi_espera = cv2.selectROI("Calibrador SmartCafe - Selecciona ZONA ESPERA", frame, showCrosshair=True)
    cv2.destroyWindow("Calibrador SmartCafe - Selecciona ZONA ESPERA")

    # Convertir de formato (x, y, w, h) a (x1, y1, x2, y2)
    p_coords = [int(roi_pedidos[0]), int(roi_pedidos[1]), 
                int(roi_pedidos[0] + roi_pedidos[2]), int(roi_pedidos[1] + roi_pedidos[3])]
    
    e_coords = [int(roi_espera[0]), int(roi_espera[1]), 
                int(roi_espera[0] + roi_espera[2]), int(roi_espera[1] + roi_espera[3])]

    print("\nCopia y pega este diccionario en tu archivo src/config.py:\n")
    print("ROIS = {")
    print(f'    "ZONA_PEDIDOS": {p_coords},')
    print(f'    "ZONA_ESPERA":  {e_coords}')
    print("}\n")

if __name__ == "__main__":
    calibrar_rois()