import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

def plot_heatmap():
    # Mock heatmap data
    data = np.random.rand(10, 10)
    fig, ax = plt.subplots()
    cax = ax.imshow(data, cmap='hot', interpolation='nearest')
    fig.colorbar(cax)
    st.pyplot(fig)

if __name__ == "__main__":
    plot_heatmap()
