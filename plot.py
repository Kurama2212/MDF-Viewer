
import plotly.express as px


def plot_line(df,Name):

    fig = px.line(df, x = df.index, y = Name, title = f'{Name} vs Time')

    plot_html = fig.to_html(include_plotlyjs='cdn', full_html=True)
    return plot_html
