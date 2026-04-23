import dash
from dash import html

dash_app = dash.Dash(__name__)
dash_app.layout = html.Div("Hello from Dash on Vercel")

app = dash_app.server

if __name__ == "__main__":
    dash_app.run(debug=True)
