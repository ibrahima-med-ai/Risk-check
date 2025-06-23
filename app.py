import gradio as gr
import os

# Exemple simple d'interface
def dummy_function(text):
    return f"Tu as entré : {text}"

iface = gr.Interface(fn=dummy_function, inputs="text", outputs="text")

port = int(os.environ.get("PORT", 7860))

iface.launch(server_name="0.0.0.0", server_port=port)
