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

print("Trying to load:", CSV_PATH)

df = pd.read_csv(CSV_PATH)

print("CSV loaded successfully")
print(df.head())
print(df.columns.tolist())

# =========================
# CLEAN DATA
# =========================
df = df.dropna(subset=["ICT_Exp-Imp", "Cloud_Revenue_pC", "Year"]).copy()
df["Year"] = df["Year"].astype(int)
df = df[df["Year"].between(2018, 2024)]

print("Data cleaned successfully")

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
print("Years:", years)

x_min = df["ICT_Exp-Imp"].min()
x_max = df["ICT_Exp-Imp"].max()
y_min = df["Cloud_Revenue_pC"].min()
y_max = df["Cloud_Revenue_pC"].max()

x_pad = (x_max - x_min) * 0.05
y_pad = (y_max - y_min) * 0.05

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
            "ICT_Exp-Imp vs Cloud Revenue (Interactive with Traces)",
            style={"color": "white"}
        ),

        html.Div(
            id="year-label",
            style={
                "color": "white",
                "fontSize": "20px",
                "marginBottom": "10px"
            }
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

        dcc.Graph(id="scatter-plot")
    ]
)

# =========================
# CALLBACK
# =========================
@dash_app.callback(
    Output("scatter-plot", "figure"),
    Output("year-label", "children"),
    Input("year-slider", "value")
)
def update_plot(selected_year):
    selected_year = int(selected_year)

    dff_current = df[df["Year"] == selected_year]
    dff_trail = df[df["Year"] <= selected_year].sort_values(["Country Name", "Year"])

    fig = go.Figure()

    # Add trace lines for each country
    for country in dff_trail["Country Name"].unique():
        country_data = dff_trail[dff_trail["Country Name"] == country]

        if len(country_data) > 1:
            fig.add_trace(
                go.Scatter(
                    x=country_data["ICT_Exp-Imp"],
                    y=country_data["Cloud_Revenue_pC"],
                    mode="lines",
                    line=dict(color=country_data["color"].iloc[0], width=1.5),
                    opacity=0.45,
                    hoverinfo="skip",
                    showlegend=False
                )
            )

    # Add current year dots
    fig.add_trace(
        go.Scatter(
            x=dff_current["ICT_Exp-Imp"],
            y=dff_current["Cloud_Revenue_pC"],
            mode="markers",
            marker=dict(
                color=dff_current["color"],
                size=9
            ),
            text=dff_current["Country Name"],
            customdata=dff_current["Year"],
            hovertemplate=(
                "<b>%{text}</b><br>"
                "Year: %{customdata}<br>"
                "ICT_Exp-Imp: %{x}<br>"
                "Cloud Revenue pC: %{y}<extra></extra>"
            ),
            showlegend=False
        )
    )

    fig.update_layout(
        plot_bgcolor="black",
        paper_bgcolor="black",
        font=dict(color="white"),
        xaxis=dict(
            title="ICT_Exp-Imp",
            range=[x_min - x_pad, x_max + x_pad]
        ),
        yaxis=dict(
            title="Cloud Revenue per Capita",
            range=[y_min - y_pad, y_max + y_pad]
        )
    )

    return fig, f"Year: {selected_year}"

# Vercel entrypoint
app = dash_app.server

# Local testing
if __name__ == "__main__":
    dash_app.run(debug=True)
