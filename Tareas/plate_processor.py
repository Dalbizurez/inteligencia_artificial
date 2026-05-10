import cv2
import pytesseract
import matplotlib.pyplot as plt
import numpy as np
import re

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
image = cv2.imread('./img/ej01-auto.jpg')


def refinar_roi_placa(roi_gray):
    h, w = roi_gray.shape
    mejor_var = 0
    mejor_y = 0
    paso = max(1, h // 10)
    for yi in range(0, h - paso, paso):
        franja = roi_gray[yi:yi + paso, :]
        var = np.var(franja)
        if var > mejor_var:
            mejor_var = var
            mejor_y = yi
    y1 = max(0, mejor_y - paso)
    y2 = min(h, mejor_y + paso * 3)
    return roi_gray[y1:y2, :], y1


def obtener_candidatos(gray, grad, w_img, h_img):
    grad = np.absolute(grad)
    grad = cv2.convertScaleAbs(grad)
    blur = cv2.GaussianBlur(grad, (5, 5), 0)
    _, thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 5))
    morph = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    contours, _ = cv2.findContours(morph, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:80]
    candidatos = []
    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        ratio = w / float(h) if h != 0 else 0
        area = w * h
        if (1.8 < ratio < 6.5 and 1500 < area < w_img * h_img * 0.15
                and w < w_img * 0.85 and y > h_img * 0.35):
            candidatos.append((x, y, w, h))
    return candidatos


def candidatos_color_blanco(image_bgr, h_img):
    offset_y = int(h_img * 0.5)
    roi = image_bgr[offset_y:, :]
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, np.array([0, 0, 180]), np.array([180, 40, 255]))
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (20, 5))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    candidatos = []
    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        ratio = w / float(h) if h != 0 else 0
        area = w * h
        if 2.0 < ratio < 6.0 and area > 2000:
            candidatos.append((x, y + offset_y, w, h))
    return candidatos


def ocr_roi(gray, x, y, w, h):
    roi = gray[y:y+h, x:x+w]
    ratio = w / float(h) if h != 0 else 0
    if ratio > 4.5 or (w * h) > 30000:
        roi, offset_y = refinar_roi_placa(roi)
        h = roi.shape[0]
    roi = cv2.resize(roi, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
    roi = cv2.equalizeHist(roi)
    roi = cv2.GaussianBlur(roi, (3, 3), 0)
    _, roi = cv2.threshold(roi, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    kernel_text = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    roi = cv2.morphologyEx(roi, cv2.MORPH_CLOSE, kernel_text)

    config_line = '--psm 7 --oem 3 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    config_word = '--psm 8 --oem 3 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    texto = pytesseract.image_to_string(roi, config=config_line).strip().replace(" ", "").replace("\n", "")
    if len(texto) < 5:
        texto = pytesseract.image_to_string(roi, config=config_word).strip().replace(" ", "").replace("\n", "")
    return texto, roi


def es_valido(texto):
    return 5 <= len(texto) <= 9


def clave_orden(texto):
    distancia_a_7 = abs(len(texto) - 7)
    letras = sum(1 for c in texto if c.isalpha())
    return (distancia_a_7, -letras)


def mejor_candidato(candidatos, gray, h_img):
    validos = []

    for (x, y, w, h) in candidatos:
        texto, roi = ocr_roi(gray, x, y, w, h)
        if not texto:
            continue
        print(f"texto='{texto}' | len={len(texto)} | valido={es_valido(texto)}")
        if es_valido(texto):
            validos.append((texto, (x, y, w, h), roi))

    if not validos:
        return "", None, None

    validos.sort(key=lambda item: clave_orden(item[0]))
    mejor_texto, mejor_box, mejor_roi = validos[0]
    return mejor_texto, mejor_box, mejor_roi

gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
h_img, w_img = gray.shape

grad_x  = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
grad_y  = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
grad_xy = cv2.addWeighted(np.absolute(grad_x), 0.5, np.absolute(grad_y), 0.5, 0)

gradientes = {"Solo X": grad_x, "Solo Y": grad_y, "X+Y": grad_xy}

resultados = {}
for nombre, grad in gradientes.items():
    print(f"\n[{nombre}]")
    candidatos = obtener_candidatos(gray, grad, w_img, h_img)
    print(f"Candidatos: {len(candidatos)}")
    texto, box, roi = mejor_candidato(candidatos, gray, h_img)
    resultados[nombre] = (texto, box, roi)
    print(f"Resultado: '{texto}'")

print(f"\n[Color Blanco]")
cands_color = candidatos_color_blanco(image, h_img)
print(f"Candidatos: {len(cands_color)}")
texto, box, roi = mejor_candidato(cands_color, gray, h_img)
resultados["Color Blanco"] = (texto, box, roi)
print(f"Resultado: '{texto}'")

candidatos_finales = [
    (nombre, texto, box, roi)
    for nombre, (texto, box, roi) in resultados.items()
    if texto
]

if candidatos_finales:
    candidatos_finales.sort(key=lambda item: clave_orden(item[1]))
    ganador, best_text, best_box, best_roi = candidatos_finales[0]
    print(f"\nGanador: {ganador} | '{best_text}' | len={len(best_text)} | dist_a_7={abs(len(best_text)-7)}")
else:
    ganador, best_text, best_box, best_roi = "", "", None, None
    print("\nNo se detecto placa valida")

nombres = list(resultados.keys())
fig, axes = plt.subplots(1, len(nombres) + 1, figsize=(5 * (len(nombres) + 1), 5))

for ax, nombre in zip(axes[:len(nombres)], nombres):
    texto, box, roi = resultados[nombre]
    img_vis = image.copy()
    if box:
        x, y, w, h = box
        color = (0, 255, 0) if nombre == ganador else (0, 165, 255)
        cv2.rectangle(img_vis, (x, y), (x+w, y+h), color, 3)
        cv2.putText(img_vis, texto, (x, y-10 if y > 25 else y+30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
    ax.imshow(cv2.cvtColor(img_vis, cv2.COLOR_BGR2RGB))
    titulo = f"[Ganador] {nombre}" if nombre == ganador else nombre
    ax.set_title(f"{titulo}\n'{texto}'")
    ax.axis('off')

ax_roi = axes[len(nombres)]
if best_roi is not None:
    ax_roi.imshow(best_roi, cmap='gray')
    ax_roi.set_title(f"ROI ganador\n'{best_text}'")
else:
    ax_roi.set_title("Sin resultado")
ax_roi.axis('off')

plt.suptitle(f"Mejor metodo: {ganador} | '{best_text}'", fontsize=13, fontweight='bold')
plt.tight_layout()
plt.show()