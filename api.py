from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import numpy as np
import cv2
from PIL import Image
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
from sympy.parsing.latex import parse_latex

# Load models
processor = TrOCRProcessor.from_pretrained(
    "fhswf/TrOCR_Math_handwritten",
    cache_dir="./trocr_handwritten",
    local_files_only=True,
    device_map="cuda",
)
model = VisionEncoderDecoderModel.from_pretrained(
    "fhswf/TrOCR_Math_handwritten",
    cache_dir="./trocr_handwritten",
    local_files_only=True,
    device_map="cuda",
)

# FastAPI app
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ExpressionRequest(BaseModel):
    source: str
    image: list  # Expecting a 2D or 3D list representing the image


def remover_ruido(imagem: np.ndarray) -> np.ndarray:
    return cv2.medianBlur(imagem, 3)


def corrigir_inclinacao(image: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.bitwise_not(gray)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    coords = np.column_stack(np.where(thresh > 0))
    angle = cv2.minAreaRect(coords)[-1]
    angle = -(90 + angle) if angle < -45 else -angle
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)

    return cv2.warpAffine(
        image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE
    )


def aplicar_binarizacao(imagem: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)
    _, binarizada = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    return cv2.cvtColor(binarizada, cv2.COLOR_GRAY2RGB)


def evaluate_expression(expression):
    try:
        sympy_exp = parse_latex(expression)
        result = sympy_exp.evalf()

        return sympy_exp, result
    except Exception as e:
        raise ValueError(f"Erro: {str(e)}")


def format_brazilian_number(number):
    try:
        number = float(number)

        if number.is_integer():
            return f"{int(number):,}".replace(",", ".")
        else:
            formatted = f"{number:,.2f}"
            return formatted.replace(",", "v").replace(".", ",").replace("v", ".")
    except:
        return str(number)


def format_detected_expression(expression: str):
    return (
        expression.split("=")[0]
        .replace("...", "")
        .replace("X", "*")
        .replace("x", "*")
        .replace(" ", "")
    )


@app.post("/predict_expression")
def predict_expression(request: ExpressionRequest):
    try:
        image = np.array(request.image, dtype=np.uint8)
        if request.source == "Imagem":
            image = remover_ruido(image)
            # image = corrigir_inclinacao(image)
            image = aplicar_binarizacao(image)

        pil_image = Image.fromarray(image)
        pixel_values = processor(images=pil_image, return_tensors="pt").pixel_values
        generated_ids = model.generate(pixel_values)
        original_expression = processor.batch_decode(
            generated_ids, skip_special_tokens=True
        )[0]
        detected_expression = format_detected_expression(original_expression)

        sympy_exp, result = evaluate_expression(detected_expression)
        formatted_result = format_brazilian_number(result)

        return {"expression": detected_expression, "result": formatted_result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
