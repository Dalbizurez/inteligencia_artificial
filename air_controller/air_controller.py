import cv2
import mediapipe as mp
import math
import numpy as np

mp_drawing = mp.solutions.drawing_utils
mp_hands   = mp.solutions.hands

DIST_MIN  = 20    
DIST_MAX  = 200   

# ── Función: distancia euclidiana entre dos landmarks ────────────────────────
def distancia_px(p1, p2, ancho, alto):
    """Convierte landmarks normalizados a píxeles y calcula la distancia."""
    x1, y1 = int(p1.x * ancho), int(p1.y * alto)
    x2, y2 = int(p2.x * ancho), int(p2.y * alto)
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2), (x1, y1), (x2, y2)

# ── Función: mapear un valor de un rango a otro ──────────────────────────────
def mapear(valor, in_min, in_max, out_min, out_max):
    valor_clamp = max(in_min, min(in_max, valor))   # limitar al rango de entrada
    return int((valor_clamp - in_min) / (in_max - in_min) * (out_max - out_min) + out_min)

# ── Función: dibujar la barra de estado ─────────────────────────────────────
def dibujar_barra(frame, nivel, x=30, y=100, w=40, h=300):
    """
    Dibuja una barra vertical que sube según 'nivel' (0-100).
    Color: verde → amarillo → rojo a medida que sube.
    Se vuelve roja cuando los dedos casi se tocan (nivel bajo).
    """
    # Fondo de la barra
    cv2.rectangle(frame, (x, y), (x + w, y + h), (50, 50, 50), -1)
    cv2.rectangle(frame, (x, y), (x + w, y + h), (200, 200, 200), 2)

    # Altura del relleno proporcional al nivel
    fill_h = int(h * nivel / 100)
    fill_y = y + h - fill_h

    if nivel <= 10:
        color = (0, 0, 255)      
    elif nivel >= 60:
        color = (0, 255, 100)    
    else:
        color = (0, 200, 255)    

    if fill_h > 0:
        cv2.rectangle(frame, (x, fill_y), (x + w, y + h), color, -1)

    # Texto de porcentaje sobre la barra
    cv2.putText(frame, f"{nivel}%",
                (x - 5, y - 12),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.putText(frame, "CTRL",
                (x + 2, y + h + 25),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (200, 200, 200), 1)

# ── Función: dibujar línea entre pulgar e índice ─────────────────────────────
def dibujar_linea_dedos(frame, pt1, pt2, nivel):
    """Línea roja si los dedos casi se tocan, blanca si no."""
    color = (0, 0, 255) if nivel <= 10 else (255, 255, 255)
    grosor = 3 if nivel <= 10 else 2
    cv2.line(frame, pt1, pt2, color, grosor)
    # Puntos en los extremos
    cv2.circle(frame, pt1, 8, (255, 200, 0), -1)   # pulgar: dorado
    cv2.circle(frame, pt2, 8, (0, 200, 255), -1)   # índice: cian

# ── Función: dedo levantado ──────────────────────────────────────────────────
def dedo_levantado(landmarks, tip, dip, pip, mcp):
    return (landmarks[tip].y < landmarks[dip].y and
            landmarks[dip].y < landmarks[pip].y and
            landmarks[pip].y < landmarks[mcp].y)

# ── Bucle principal con webcam ───────────────────────────────────────────────
def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: no se pudo abrir la cámara.")
        return

    nivel_actual = 0   # para suavizar la barra

    with mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=1,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.6
    ) as hands:

        while cap.isOpened():
            ok, frame = cap.read()
            if not ok:
                break

            # Espejo + conversión de color
            frame = cv2.flip(frame, 1)
            alto, ancho, _ = frame.shape
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Procesar con MediaPipe
            rgb.flags.writeable = False
            resultados = hands.process(rgb)
            rgb.flags.writeable = True

            # ── Si hay mano detectada ────────────────────────────────────────
            if resultados.multi_hand_landmarks:
                for hand_lm in resultados.multi_hand_landmarks:
                    lm = hand_lm.landmark

                    # Dibujar esqueleto de la mano
                    mp_drawing.draw_landmarks(
                        frame, hand_lm, mp_hands.HAND_CONNECTIONS,
                        mp_drawing.DrawingSpec(color=(100, 255, 100), thickness=1, circle_radius=3),
                        mp_drawing.DrawingSpec(color=(200, 200, 200), thickness=1)
                    )

                    # ── Landmarks clave ──────────────────────────────────────
                    pulgar  = lm[4]   # Thumb tip
                    indice  = lm[8]   # Index finger tip

                    # Distancia en píxeles
                    dist, pt_pulgar, pt_indice = distancia_px(pulgar, indice, ancho, alto)

                    # Mapear a 0-100
                    nivel_objetivo = mapear(dist, DIST_MIN, DIST_MAX, 0, 100)

                    # Suavizado (interpolación simple para evitar parpadeo)
                    nivel_actual = int(nivel_actual * 0.7 + nivel_objetivo * 0.3)

                    # Dibujar línea entre dedos
                    dibujar_linea_dedos(frame, pt_pulgar, pt_indice, nivel_actual)

                    # Mostrar distancia en píxeles sobre la línea
                    mid = ((pt_pulgar[0] + pt_indice[0]) // 2,
                           (pt_pulgar[1] + pt_indice[1]) // 2)
                    cv2.putText(frame, f"{int(dist)}px",
                                (mid[0] + 10, mid[1] - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)

                    # ── Contador de dedos levantados (bonus) ─────────────────
                    dedos = [
                        dedo_levantado(lm, 8,  7,  6,  5),   # Índice
                        dedo_levantado(lm, 12, 11, 10,  9),   # Medio
                        dedo_levantado(lm, 16, 15, 14, 13),   # Anular
                        dedo_levantado(lm, 20, 19, 18, 17),   # Meñique
                    ]
                    n_dedos = sum(dedos)
                    cv2.putText(frame, f"Dedos: {n_dedos}",
                                (ancho - 160, 40),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 2)

            # ── Dibujar barra de estado ──────────────────────────────────────
            dibujar_barra(frame, nivel_actual)

            # ── HUD informativo ──────────────────────────────────────────────
            cv2.putText(frame, "Air Controller - MediaPipe",
                        (ancho // 2 - 180, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 200), 2)
            cv2.putText(frame, "Pulgar [4] <-> Indice [8]",
                        (ancho // 2 - 155, 58),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (180, 180, 180), 1)
            cv2.putText(frame, "Presiona 'q' para salir",
                        (10, alto - 15),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150, 150, 150), 1)

            cv2.imshow("Air Controller", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()