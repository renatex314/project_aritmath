import gradio as gr
import cv2
import numpy as np
import sympy as sp
import locale
from PIL import Image
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
from sympy.parsing.latex import parse_latex

locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")

processor = TrOCRProcessor.from_pretrained("fhswf/TrOCR_Math_handwritten")
model = VisionEncoderDecoderModel.from_pretrained("fhswf/TrOCR_Math_handwritten").to(
    "cpu"
)


def remover_ruido(imagem: np.ndarray) -> np.ndarray:
    """
    Remove o ruído (pequenos pontos) de uma imagem usando um filtro de mediana.
    :param imagem: Imagem de entrada (numpy array).
    :return: Imagem sem ruído (numpy array).
    """
    return cv2.medianBlur(imagem, 3)


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


def evaluate_expression(expression):
    try:
        print(f"Expressão: {expression}")
        sympy_exp = parse_latex(expression)
        result = sympy_exp.evalf()

        return sympy_exp, result
    except Exception as e:
        return f"Erro: {str(e)}"


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
    return expression.replace("...", "")


def predict_expression(source, sketch, uploaded_img):
    # Escolhe a imagem correta
    image = sketch if source == "Desenhar" else uploaded_img

    if image is None:
        return "Nenhuma imagem fornecida."

    # Se for um dicionário (Sketchpad), extrai o array real
    if isinstance(image, dict) and "composite" in image:
        image = image["composite"]
        image = np.array(image).astype(np.uint8)

    image = remover_ruido(image)
    image = corrigir_inclinacao(image)
    image = aplicar_binarizacao(image)
    pil_image = Image.fromarray(image)

    cv2.imwrite("processed_image.png", image)

    # TrOCR + avaliação
    pixel_values = processor(images=pil_image, return_tensors="pt").pixel_values
    generated_ids = model.generate(pixel_values)
    original_expression = processor.batch_decode(
        generated_ids, skip_special_tokens=True
    )[0]

    detected_expression = format_detected_expression(original_expression)

    _, result = evaluate_expression(detected_expression)
    formatted_result = format_brazilian_number(result)

    return f"$${detected_expression}$$", f"Resultado: {formatted_result}"


with gr.Blocks() as demo:
    gr.Markdown("# 🧠 Reconhecimento de Expressões Matemáticas Escritas")
    gr.Markdown("Escolha entre desenhar ou enviar uma imagem da expressão.")

    with gr.Row():
        source = gr.Radio(
            ["Desenhar", "Imagem"], value="Desenhar", label="Fonte da expressão"
        )

    with gr.Row():
        sketch = gr.Sketchpad(
            image_mode="RGB",
            brush=gr.Brush(colors=["#000000"], default_size=3),
            label="Desenhe a expressão",
            canvas_size=(400, 200),
            visible=True,
        )
        uploaded_img = gr.Image(
            label="Envie uma imagem",
            type="numpy",
            visible=False,
            value=Image.open("numbers.png"),
        )

    # Atualiza a visibilidade dos componentes com base na seleção
    def update_source(source):
        if source == "Desenhar":
            sketch.visible = True
            uploaded_img.visible = False
        else:
            sketch.visible = False
            uploaded_img.visible = True

        return gr.update(visible=sketch.visible), gr.update(
            visible=uploaded_img.visible
        )

    source.change(
        fn=update_source,
        inputs=source,
        outputs=[sketch, uploaded_img],
    )

    btn = gr.Button("Reconhecer e Resolver")
    outputs = [gr.Markdown(label="Expressão"), gr.Textbox(label="Resultado")]

    btn.click(
        fn=predict_expression, inputs=[source, sketch, uploaded_img], outputs=outputs
    )

if __name__ == "__main__":
    demo.launch()
