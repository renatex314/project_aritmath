import gradio as gr
import requests
import numpy as np

API_URL = "http://localhost:8001/predict_expression"


def predict_expression_ui(source, sketch, uploaded_img):
    # Escolhe a imagem correta
    image = sketch if source == "Desenhar" else uploaded_img
    if image is None:
        return "Nenhuma imagem fornecida.", ""

    # Se for um dicionário (Sketchpad), extrai o array real
    if isinstance(image, dict) and "composite" in image:
        image = image["composite"]

    # Converte a imagem para uma lista (JSON serializable)
    if isinstance(image, np.ndarray):
        image = image.tolist()

    # Envia a imagem para a API de reconhecimento
    response = requests.post(API_URL, json={"source": source, "image": image})
    if response.status_code == 200:
        data = response.json()

        return f'$${data.get("expression", "")}$$', f'Resultado: {data.get("result", "")}'
    else:
        return "", "Erro ao processar a expressão."


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
        uploaded_img = gr.ImageEditor(
            label="Envie uma imagem",
            type="numpy",
            interactive=True,
            visible=False,
        )

    # Atualiza a visibilidade dos componentes com base na seleção
    def update_source(source):
        return (
            gr.update(visible=source == "Desenhar"),
            gr.update(visible=source == "Imagem"),
        )

    source.change(
        fn=update_source,
        inputs=source,
        outputs=[sketch, uploaded_img],
    )

    btn = gr.Button("Reconhecer e Resolver")
    outputs = [gr.Markdown(label="Expressão"), gr.Textbox(label="Resultado")]

    btn.click(
        fn=predict_expression_ui, inputs=[source, sketch, uploaded_img], outputs=outputs
    )

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=8000)
