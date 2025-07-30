import os
import numpy as np
from shapely.geometry import Polygon
from shapely.affinity import translate, rotate, scale as shapely_scale
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go

# Updated centered gadget polygon
raw_coords = np.array([
    [36.54538401861909, -108.88673390224980],
    [-11.45461598138091, 2.11326609775020],
    [-44.45461598138091, 5.11326609775020],
    [-44.45461598138091, 80.11326609775020],
    [35.54538401861909, 5.11326609775020]
])
poly0 = Polygon(raw_coords)
cx, cy = poly0.centroid.coords[0]
gadget_coords = raw_coords - np.array([cx, cy])
gadget_centered = Polygon(gadget_coords)

# Initialize the Dash app
app = dash.Dash(__name__)

# App layout
app.layout = html.Div([
    html.H2("Geometric Assembly Shuriken Design Generator", style={'textAlign': 'center'}),
    html.P("Adjust the sliders to explore unique geometric patterns.", style={'textAlign': 'center'}),
    dcc.Graph(id='shuriken-graph'),

    # First row of sliders
    html.Div([
        html.Div([
            html.Label('n: Number of gadgets'),
            dcc.Slider(id='n-slider', min=1, max=128, step=1, value=32,
                marks={1: '1', 128: '128'},
                tooltip={'placement': 'bottom', 'always_visible': True},
                updatemode='drag')
        ], style={'flex': '1', 'margin': '0 10px 20px', 'display': 'flex', 'flexDirection': 'column'}),

        html.Div([
            html.Label('R: Radius'),
            dcc.Slider(id='R-slider', min=50, max=1200, step=10, value=470,
                marks={50: '50', 1200: '1200'},
                tooltip={'placement': 'bottom', 'always_visible': True},
                updatemode='drag')
        ], style={'flex': '1', 'margin': '0 10px 20px', 'display': 'flex', 'flexDirection': 'column'})
    ], style={'display': 'flex', 'marginTop': '20px'}),

    # Second row of sliders
    html.Div([
        html.Div([
            html.Label('s₁: Primary scale'),
            dcc.Slider(id='s1-slider', min=0.1, max=3.1, step=0.1, value=2.0,
                marks={0.1: '0.1', 3.1: '3.1'},
                tooltip={'placement': 'bottom', 'always_visible': True},
                updatemode='drag')
        ], style={'flex': '1', 'margin': '0 10px 20px', 'display': 'flex', 'flexDirection': 'column'}),

        html.Div([
            html.Label('s₂: Secondary scale'),
            dcc.Slider(id='s2-slider', min=0.1, max=3.0, step=0.1, value=1.0,
                marks={0.1: '0.1', 3.0: '3.0'},
                tooltip={'placement': 'bottom', 'always_visible': True},
                updatemode='drag')
        ], style={'flex': '1', 'margin': '0 10px 20px', 'display': 'flex', 'flexDirection': 'column'}),

        html.Div([
            html.Label('cells: Gadget count'),
            dcc.Slider(id='cells-slider', min=1, max=2, step=1, value=2,
                marks={1: '1', 2: '2'},
                tooltip={'placement': 'bottom', 'always_visible': True},
                updatemode='drag')
        ], style={'flex': '1', 'margin': '0 10px 20px', 'display': 'flex', 'flexDirection': 'column'}),

        html.Div([
            html.Label('ΔR: Radius offset'),
            dcc.Slider(id='delta-slider', min=-200, max=200, step=5, value=45,
                marks={-200: '-200', 200: '200'},
                tooltip={'placement': 'bottom', 'always_visible': True},
                updatemode='drag')
        ], style={'flex': '1', 'margin': '0 10px 20px', 'display': 'flex', 'flexDirection': 'column'}),

        html.Div([
            html.Label('τ (°): Angular offset'),
            dcc.Slider(id='tau-slider', min=-180, max=180, step=0.5, value=-24.5,
                marks={-180: '-180', 0: '0', 180: '180'},
                tooltip={'placement': 'bottom', 'always_visible': True},
                updatemode='drag')
        ], style={'flex': '1', 'margin': '0 10px 20px', 'display': 'flex', 'flexDirection': 'column'})
    ], style={'display': 'flex', 'marginTop': '10px', 'marginBottom': '36px'}),

    html.P("Interactive geometric assembly shuriken design generator, inspired by computational geometry.",
        style={'textAlign': 'center', 'fontStyle': 'italic', 'marginTop': '20px'})
], style={'maxWidth': '900px', 'margin': 'auto'})


# Core plotting logic
def make_traces(n, R, s1, s2, cells, tau, delta):
    angle_step = 360.0 / n
    traces = []

    for i in range(n):
        base_angle = i * angle_step
        θ1 = np.deg2rad(base_angle)

        # Primary gadget (white fill, black border)
        p1 = shapely_scale(gadget_centered, xfact=s1, yfact=s1, origin=(0, 0))
        p1 = rotate(p1, base_angle, origin=(0, 0))
        p1 = translate(p1, xoff=R * np.cos(θ1), yoff=R * np.sin(θ1))
        x1, y1 = p1.exterior.xy
        traces.append(go.Scatter(x=x1, y=y1, fill='toself', fillcolor='white', line=dict(color='black'), mode='lines'))

    if cells == 2:
        for i in range(n):
            base_angle = i * angle_step
            half_angle = base_angle + angle_step / 2 + tau
            θ2 = np.deg2rad(half_angle)
            r2 = R + delta

            p2 = shapely_scale(gadget_centered, xfact=s2, yfact=s2, origin=(0, 0))
            p2 = rotate(p2, base_angle, origin=(0, 0))
            p2 = translate(p2, xoff=r2 * np.cos(θ2), yoff=r2 * np.sin(θ2))
            x2, y2 = p2.exterior.xy
            traces.append(go.Scatter(x=x2, y=y2, fill='toself', fillcolor='black', line=dict(color='black'), mode='lines'))

    return traces


# Callback
@app.callback(
    Output('shuriken-graph', 'figure'),
    Input('n-slider', 'value'),
    Input('R-slider', 'value'),
    Input('s1-slider', 'value'),
    Input('s2-slider', 'value'),
    Input('cells-slider', 'value'),
    Input('delta-slider', 'value'),
    Input('tau-slider', 'value')
)
def update_graph(n, R, s1, s2, cells, delta, tau):
    fig = go.Figure()
    for trace in make_traces(n, R, s1, s2, cells, tau, delta):
        fig.add_trace(trace)
    fig.update_layout(
        showlegend=False,
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        margin=dict(l=0, r=0, t=0, b=0),
        plot_bgcolor='white',
        paper_bgcolor='white',
        dragmode='pan',
        height=630
    )
    fig.update_yaxes(scaleanchor="x", scaleratio=1)
    return fig


# Main
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8050))
    app.run(host='0.0.0.0', port=port, debug=False)
