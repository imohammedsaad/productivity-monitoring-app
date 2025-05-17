import streamlit as st
import matplotlib.pyplot as plt

def plot_bar_chart(data, title="Bar Chart"):
    fig, ax = plt.subplots()
    ax.bar([d['zone'] for d in data], [d['count'] for d in data])
    ax.set_title(title)
    st.pyplot(fig)

def plot_line_chart(data, title="Line Chart"):
    fig, ax = plt.subplots()
    ax.plot([d['timestamp'] for d in data], [d['count'] for d in data])
    ax.set_title(title)
    st.pyplot(fig)

if __name__ == "__main__":
    plot_bar_chart([{'zone': 'A', 'count': 5}, {'zone': 'B', 'count': 3}])
