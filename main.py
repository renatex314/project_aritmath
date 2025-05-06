import cv2
import pytesseract
import sympy as sp
import re
import matplotlib.pyplot as plt

# Path to Tesseract executable (only needed on Windows)
# Uncomment and change path if you're using Windows
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_expression(image_path):
    image = cv2.imread(image_path)

    # Preprocess image (optional, but improves accuracy)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Custom config to whitelist arithmetic symbols
    custom_config = r'-c tessedit_char_whitelist=0123456789+-*/().=X --psm 7'

    extracted_text = pytesseract.image_to_string(thresh, config=custom_config)

    # Clean text
    expression = extracted_text.strip().replace(' ', '').replace('\n', '')

    # Validate the expression using regex
    pattern = re.compile(r'^[\d\+\-\*\/\(\)\=\.]+$')
    if pattern.match(expression):
        return expression, image
    else:
        return None, image

def evaluate_expression(expression):
    try:
        sympy_exp = sp.sympify(expression)
        result = sympy_exp.evalf()
        return result
    except Exception as e:
        return f"Error: {str(e)}"

def visualize(image, expression, result):
    plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    plt.axis('off')
    plt.title(f'Extracted: {expression}\nResult: {result}')
    plt.show()

def main():
    image_path = 'numbers.png'  # <-- Replace with your image path
    expression, image = extract_expression(image_path)

    if expression:
        print(f'Extracted Expression: {expression}')
        result = evaluate_expression(expression)
        print(f'Evaluation Result: {result}')
        visualize(image, expression, result)
    else:
        print('No valid arithmetic expression was found!')

if __name__ == '__main__':
    main()
