import cv2
import numpy as np
from cnstd import LayoutAnalyzer
from typing import List
from ultralytics import YOLO


def remover_ruido(imagem: np.ndarray) -> np.ndarray:
    """
    Remove o ruído (pequenos pontos) de uma imagem usando um filtro de mediana.
    :param imagem: Imagem de entrada (numpy array).
    :return: Imagem sem ruído (numpy array).
    """
    return cv2.medianBlur(imagem, 5)


def corrigir_inclinacao(image: np.ndarray) -> np.ndarray:
    """
    Corrige a inclinação de uma imagem. (Deskew)
    :param image: Imagem de entrada (numpy array).
    :return: Imagem corrigida (numpy array).
    """

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.bitwise_not(gray)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

    coords = np.column_stack(np.where(thresh > 0))
    angle = cv2.minAreaRect(coords)[-1]

    if angle < -45:
        angle = -(90 + angle)
    elif angle > 45:
        angle = -(angle - 90)
    else:
        angle = -angle

    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)

    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(
        image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE
    )

    return rotated


def aplicar_binarizacao(imagem: np.ndarray) -> np.ndarray:
    """
    Aplica binarização a uma imagem.
    :param imagem: Imagem de entrada (numpy array).
    :return: Imagem binarizada (numpy array).
    """
    gray = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)
    _, binarizada = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    binarizada = cv2.cvtColor(binarizada, cv2.COLOR_GRAY2RGB)

    return binarizada


def extract_expressions(img, min_area=5000):
    # 1. read & binarise
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # robust to lighting: adaptive threshold + Otsu fallback
    _, bin_ = cv2.threshold(
        cv2.GaussianBlur(gray, (5, 5), 0),
        0,
        255,
        cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU,
    )

    # 2. dilate so symbols in one line touch
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (35, 7))
    dil = cv2.dilate(bin_, kernel, iterations=2)

    # 3. find external contours (each ≈ one formula line)
    cnts, _ = cv2.findContours(dil, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    crops = []
    for i, c in enumerate(cnts):
        x, y, w, h = cv2.boundingRect(c)
        if w * h < min_area:  # filter noise
            continue
        pad = 10
        crop = img[max(y - pad, 0) : y + h + pad, max(x - pad, 0) : x + w + pad]
        crops.append(crop)

    return crops


# Remoção de ruído
sample = cv2.imread("./teste/sample5.png")
sample = remover_ruido(sample)
sample = corrigir_inclinacao(sample)
sample = aplicar_binarizacao(sample)

cv2.imwrite("outputs/sample.png", sample)

# expressions = extract_expressions(sample, min_area=5000)
# for i in range(len(expressions)):
#     cv2.imwrite(f"outputs/expr_{i:02d}.png", expressions[i])
