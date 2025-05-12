import cv2
import sympy as sp
import locale
import matplotlib.pyplot as plt
from transformers import TrOCRProcessor, VisionEncoderDecoderModel, logging

locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")


def extract_expression(image_path):
    image = cv2.imread(image_path)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    processor = TrOCRProcessor.from_pretrained("fhswf/TrOCR_Math_handwritten")
    model = VisionEncoderDecoderModel.from_pretrained(
        "fhswf/TrOCR_Math_handwritten"
    ).to("cpu")
    pixel_values = processor(images=image_rgb, return_tensors="pt").pixel_values
    generated_ids = model.generate(pixel_values)
    generated_formula = processor.batch_decode(generated_ids, skip_special_tokens=True)[
        0
    ]

    return generated_formula, image_rgb  # Placeholder for OCR result


def preprocess_expression(expression: str) -> str:
    expression = expression.strip()
    expression = expression.replace(" ", "")
    expression = expression.split("=")[0]

    return expression


def evaluate_expression(expression):
    try:
        sympy_exp = sp.sympify(expression)
        result = sympy_exp.evalf()
        return result
    except Exception as e:
        return f"Error: {str(e)}"


def format_brazilian_number(number):
    number = float(number)
    if number.is_integer():
        return f"{int(number):,}".replace(",", ".")  # 1234 -> 1.234
    else:
        formatted = f"{number:,.2f}"  # 1234.56 -> 1,234.56
        return formatted.replace(",", "v").replace(".", ",").replace("v", ".")


def visualize(image_rgb, expression, result):
    plt.imshow(image_rgb)
    plt.axis("off")
    plt.title(f"Extracted: {expression}\nResult: {format_brazilian_number(result)}")
    plt.show()


def main():
    image_path = "./numbers.png"  # <-- Replace with your image path
    expression, image = extract_expression(image_path)
    expression = preprocess_expression(expression)

    if expression:
        print(f"Extracted Expression: {expression}")
        result = evaluate_expression(expression)
        print(f"Evaluation Result: {result}")
        visualize(image, expression, result)
    else:
        print("No valid arithmetic expression was found!")


if __name__ == "__main__":
    main()
