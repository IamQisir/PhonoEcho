import gradio as gr
import matplotlib.pyplot as plt
import numpy as np

def plot_function():
    # Create a sample image
    """Handle plot function."""
    x = np.linspace(0, 2 * np.pi, 100)
    y = np.sin(x)

    fig, ax = plt.subplots()
    ax.plot(x, y)
    
    return fig

# Display the Matplotlib image directly with the gr.Plot component
demo = gr.Interface(fn=plot_function, inputs=[], outputs=gr.Plot())

demo.launch()
