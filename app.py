from pathlib import Path
import pandas as pd
import dash
from dash import html

BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "05_unified_services_2018_2024.csv"

print("Trying to load:", CSV_PATH)

df = pd.read_csv(CSV_PATH)

print("CSV loaded")
print(df.head())

dash_app = dash.Dash(__name__)
dash_app.layout = html.Div("CSV LOADED SUCCESSFULLY")

app = dash_app.server
