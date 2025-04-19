import numpy as np
from shapely.geometry import Polygon
from shapely.affinity import translate, rotate, scale as shapely_scale
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go

# 1) Centered gadget polygon coordinates
gadget_coords = [
    [-137.5630841121495, -198.642523364486],
    [111.43691588785049, 102.35747663551399],
    [120.43691588785049, 95.35747663551399],
    [140.4369158878505, 132.357476635514],
    [8.436915887850489, -111.64252336448601],
    [-27.56308411214951, -75.64252336448601],
    [-82.56308411214951, -141.642523364486],
    [10.436915887850489, -213.642523364486],
    [-82.56308411214951, -141.642523364486],
    [-28.56308411214951, -75.64252336448601],
    [10.436915887850489, -110.64252336448601],
    [119.43691588785049, 93.35747663551399],
    [113.43691588785049, 102.35747663551399]
]

# Create a Shapely polygon for the gadget
gadget_centered = Polygon(gadget_coords)

# Initialize the Dash app
app = dash.Dash(__name__)

# App layout
app.layout = html.Div([
    html.H2("Geometric Assembly Shuriken Design Generator", style={'textAlign': 'center'}),
    html.P("Adjust the sliders to explore unique geometric patterns.", style={'textAlign': 'center'}),
    dcc.Graph(id='shuriken-graph'),

    html.Div([
        # First row of sliders
        html.Div([
            html.Label('n: Number of gadgets'),
            dcc.Slider(
                id='n-slider', min=1, max=128, step=1, value=32,
                marks={1: '1', 128: '128'},
                tooltip={'placement': 'bottom', 'always_visible': True},
                updatemode='drag'
            )
        ], style={'flex': '1', 'margin': '0 10px 20px', 'display': 'flex', 'flexDirection': 'column'}),

        html.Div([
            html.Label('R: Radius'),
            dcc.Slider(
                id='R-slider', min=50, max=400, step=10, value=200,
                marks={50: '50', 400: '400'},
                tooltip={'placement': 'bottom', 'always_visible': True},
                updatemode='drag'
            )
        ], style={'flex': '1', 'margin': '0 10px 20px', 'display': 'flex', 'flexDirection': 'column'})
    ], style={'display': 'flex', 'marginTop': '20px'}),

    html.Div([
        # Second row of sliders
        html.Div([
            html.Label('s₁: Primary scale'),
            dcc.Slider(
                id='s1-slider', min=0.1, max=3.0, step=0.1, value=1.0,
                marks={0.1: '0.1', 3.0: '3.0'},
                tooltip={'placement': 'bottom', 'always_visible': True},
                updatemode='drag'
            )
        ], style={'flex': '1', 'margin': '0 10px 20px', 'display': 'flex', 'flexDirection': 'column'}),

        html.Div([
            html.Label('s₂: Secondary scale'),
            dcc.Slider(
                id='s2-slider', min=0.1, max=3.0, step=0.1, value=1.0,
                marks={0.1: '0.1', 3.0: '3.0'},
                tooltip={'placement': 'bottom', 'always_visible': True},
                updatemode='drag'
            )
        ], style={'flex': '1', 'margin': '0 10px 20px', 'display': 'flex', 'flexDirection': 'column'}),

        html.Div([
            html.Label('cells: Gadget count'),
            dcc.Slider(
                id='cells-slider', min=1, max=2, step=1, value=1,
                marks={1: '1', 2: '2'},
                tooltip={'placement': 'bottom', 'always_visible': True},
                updatemode='drag'
            )
        ], style={'flex': '1', 'margin': '0 10px 20px', 'display': 'flex', 'flexDirection': 'column'}),

        html.Div([
            html.Label('ΔR: Radius offset'),
            dcc.Slider(
                id='delta-slider', min=-100, max=100, step=5, value=0,
                marks={-100: '-100', 100: '100'},
                tooltip={'placement': 'bottom', 'always_visible': True},
                updatemode='drag'
            )
        ], style={'flex': '1', 'margin': '0 10px 20px', 'display': 'flex', 'flexDirection': 'column'})
    ], style={'display': 'flex', 'marginTop': '10px', 'marginBottom': '40px'}),

    # Footer note
    html.P(
        "Interactive geometric assembly shuriken design generator, inspired by computational geometry",
        style={'textAlign': 'center', 'fontStyle': 'italic', 'marginTop': '20px'}
    )
], style={'maxWidth': '900px', 'margin': 'auto'})


def make_traces(n, R, s1, s2, cells, delta):
    angle_step = 360.0 / n
    traces = []
    for i in range(n):
        base_angle = i * angle_step
        θ = np.deg2rad(base_angle)
        p1 = shapely_scale(gadget_centered, xfact=s1, yfact=s1, origin=(0, 0))
        px, py = R * np.cos(θ), R * np.sin(θ)
        p1 = translate(p1, xoff=px, yoff=py)
        p1 = rotate(p1, base_angle, origin=(px, py))
        x1_arr, y1_arr = p1.exterior.xy
        x1, y1 = list(x1_arr), list(y1_arr)
        traces.append(go.Scatter(x=x1, y=y1, fill='toself', fillcolor='black', line=dict(color='black'), mode='lines'))

        if cells == 2:
            half_angle = base_angle + angle_step / 2
            θ2 = np.deg2rad(half_angle)
            r2 = R + delta
            px2, py2 = r2 * np.cos(θ2), r2 * np.sin(θ2)
            p2 = shapely_scale(gadget_centered, xfact=s2, yfact=s2, origin=(0, 0))
            p2 = translate(p2, xoff=px2, yoff=py2)
            p2 = rotate(p2, half_angle, origin=(px2, py2))
            x2_arr, y2_arr = p2.exterior.xy
            x2, y2 = list(x2_arr), list(y2_arr)
            traces.append(go.Scatter(x=x2, y=y2, fill='toself', fillcolor='gray', line=dict(color='gray'), mode='lines'))
    return traces


@app.callback(
    Output('shuriken-graph', 'figure'),
    Input('n-slider', 'value'),
    Input('R-slider', 'value'),
    Input('s1-slider', 'value'),
    Input('s2-slider', 'value'),
    Input('cells-slider', 'value'),
    Input('delta-slider', 'value')
)
def update_graph(n, R, s1, s2, cells, delta):
    fig = go.Figure()
    for trace in make_traces(n, R, s1, s2, cells, delta):
        fig.add_trace(trace)
    fig.update_layout(
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        margin=dict(l=0, r=0, t=0, b=0),
        plot_bgcolor='white',
        paper_bgcolor='white',
        dragmode='pan',
        height=700
    )
    fig.update_yaxes(scaleanchor="x", scaleratio=1)
    return fig


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8050, debug=True)