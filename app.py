from pathlib import Path
import pandas as pd
import dash
from dash import dcc, html, Input, Output
import plotly.graph_objects as go

# =========================
# LOAD DATA
# =========================
BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "05_unified_services_2018_2024.csv"

df = pd.read_csv(CSV_PATH)

# =========================
# CLEAN DATA
# =========================
df = df.dropna(subset=["ICT_Exp-Imp", "Cloud_Revenue_pC", "Cloud_companies_pP", "Year"]).copy()
df["Year"] = df["Year"].astype(int)
df = df[df["Year"].between(2018, 2024)]

# =========================
# REGION DEFINITIONS
# =========================
EUROPE = [
    "Germany", "France", "Italy", "Spain", "Netherlands", "Belgium", "Austria",
    "Sweden", "Norway", "Denmark", "Finland", "Poland", "Czech Republic",
    "Portugal", "Greece", "Ireland", "Hungary", "Romania", "Bulgaria",
    "Slovakia", "Slovenia", "Croatia", "Estonia", "Latvia", "Lithuania",
    "Switzerland", "United Kingdom"
]

LATAM = [
    "Argentina", "Brazil", "Chile", "Colombia", "Peru", "Ecuador", "Mexico",
    "Uruguay", "Paraguay", "Bolivia", "Costa Rica", "Panama", "Guatemala",
    "El Salvador", "Honduras", "Nicaragua", "Dominican Republic"
]

ASIA = [
    "Japan", "South Korea", "Indonesia", "Thailand", "Vietnam", "Malaysia",
    "Philippines", "Pakistan", "Bangladesh", "Singapore"
]

AFRICA = [
    "Nigeria", "Kenya", "South Africa", "Egypt", "Morocco", "Algeria",
    "Ghana", "Ethiopia", "Tunisia"
]

# =========================
# COLOR LOGIC
# =========================
def assign_color(country):
    if country in ["United States", "USA", "United States of America"]:
        return "blue"
    elif country == "China":
        return "red"
    elif country == "India":
        return "yellow"
    elif country in EUROPE:
        return "white"
    elif country in LATAM:
        return "purple"
    elif country in ASIA:
        return "orange"
    elif country in AFRICA:
        return "lightgray"
    else:
        return "turquoise"

df["color"] = df["Country Name"].apply(assign_color)

# =========================
# YEARS + FIXED AXIS RANGES
# =========================
years = sorted([int(y) for y in df["Year"].dropna().unique()])

x_min = df["ICT_Exp-Imp"].min()
x_max = df["ICT_Exp-Imp"].max()
y_min = df["Cloud_Revenue_pC"].min()
y_max = df["Cloud_Revenue_pC"].max()
z_min = df["Cloud_companies_pP"].min()
z_max = df["Cloud_companies_pP"].max()

x_pad = (x_max - x_min) * 0.05
y_pad = (y_max - y_min) * 0.05
z_pad = (z_max - z_min) * 0.05

# =========================
# DASH APP
# =========================
dash_app = dash.Dash(__name__)

dash_app.layout = html.Div(
    style={
        "backgroundColor": "black",
        "minHeight": "100vh",
        "padding": "20px"
    },
    children=[
        html.H1(
            "3D ICT_Exp-Imp vs Cloud Revenue vs Cloud Companies (with Traces)",
            style={"color": "white"}
        ),

        html.Div(
            id="year-label",
            style={"color": "white", "fontSize": "20px", "marginBottom": "10px"}
        ),

        dcc.Slider(
            id="year-slider",
            min=int(min(years)),
            max=int(max(years)),
            step=1,
            value=int(max(years)),
            marks={int(year): str(year) for year in years},
            updatemode="drag"
        ),

        dcc.Graph(id="scatter-3d-plot", style={"height": "85vh"})
    ]
)

# =========================
# CALLBACK
# =========================
@dash_app.callback(
    Output("scatter-3d-plot", "figure"),
    Output("year-label", "children"),
    Input("year-slider", "value")
)
def update_plot(selected_year):
    selected_year = int(selected_year)

    dff_current = df[df["Year"] == selected_year]
    dff_trail = df[df["Year"] <= selected_year].sort_values(["Country Name", "Year"])

    fig = go.Figure()

    # Trails
    for country in dff_trail["Country Name"].unique():
        country_data = dff_trail[dff_trail["Country Name"] == country]

        if len(country_data) > 1:
            fig.add_trace(
                go.Scatter3d(
                    x=country_data["ICT_Exp-Imp"],
                    y=country_data["Cloud_Revenue_pC"],
                    z=country_data["Cloud_companies_pP"],
                    mode="lines",
                    line=dict(color=country_data["color"].iloc[0], width=3),
                    opacity=0.35,
                    hoverinfo="skip",
                    showlegend=False
                )
            )

    # Current dots
    fig.add_trace(
        go.Scatter3d(
            x=dff_current["ICT_Exp-Imp"],
            y=dff_current["Cloud_Revenue_pC"],
            z=dff_current["Cloud_companies_pP"],
            mode="markers",
            marker=dict(
                size=5,
                color=dff_current["color"],
                opacity=0.95
            ),
            text=dff_current["Country Name"],
            customdata=dff_current["Year"],
            hovertemplate=(
                "<b>%{text}</b><br>"
                "Year: %{customdata}<br>"
                "ICT_Exp-Imp: %{x}<br>"
                "Cloud Revenue pC: %{y}<br>"
                "Cloud Companies pP: %{z}<extra></extra>"
            ),
            showlegend=False
        )
    )

    fig.update_layout(
        paper_bgcolor="black",
        font=dict(color="white"),
        scene=dict(
            bgcolor="black",
            xaxis=dict(
                title="ICT_Exp-Imp",
                range=[x_min - x_pad, x_max + x_pad],
                backgroundcolor="black",
                color="white",
                gridcolor="gray"
            ),
            yaxis=dict(
                title="Cloud Revenue per Capita",
                range=[y_min - y_pad, y_max + y_pad],
                backgroundcolor="black",
                color="white",
                gridcolor="gray"
            ),
            zaxis=dict(
                title="Cloud Companies pP",
                range=[z_min - z_pad, z_max + z_pad],
                backgroundcolor="black",
                color="white",
                gridcolor="gray"
            )
        ),
        margin=dict(l=0, r=0, b=0, t=40)
    )

    return fig, f"Year: {selected_year}"

app = dash_app.server

if __name__ == "__main__":
    dash_app.run(debug=True)
