# ☕ SmartCafé Analytics — Monitoreo Inteligente con Visión Artificial

Prototipo de sistema de análisis operativo para cafeterías y negocios gastronómicos desarrollado con **Python, OpenCV y YOLOv8**. Permite automatizar el conteo de flujo de clientes, cronometrar tiempos de atención en barra mediante Regiones de Interés (ROI) y visualizar alertas en tiempo real.

## 🚀 Funcionalidades Principales
1. **Detección y Seguimiento Multi-Objeto (Tracking):** Identificación de clientes con ID único persistente mediante `YOLOv8 + ByteTrack`, contabilizando personas presentes y flujo acumulado.
2. **Cronometraje Automático en Barra (ROI):** Detección espacial basada en el punto de apoyo (centro inferior del *bounding box*) al ingresar y salir de la zona de atención, registrando tiempos en `data/registro_atenciones.csv`.
3. **Dashboard HUD en Tiempo Real:** Superposición gráfica con métricas en vivo (aforo actual, flujo total, tiempo promedio de atención y alertas visuales por exceso de demora).

## 🛠️ Instalación y Dependencias

1. Clonar el repositorio:
   ```bash
   git clone https://github.com/MarcosGonzalo/smartcafe-analitycs.git
   cd smartcafe-analytics
