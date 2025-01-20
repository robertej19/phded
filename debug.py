import os
import dash
from dash import dcc, html

app = dash.Dash(__name__)
server = app.server  # Expose underlying Flask server

app.layout = html.Div("Hello from Dash on Cloud Run!")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050))
    app.run_server(debug=False, host="0.0.0.0", port=port)
