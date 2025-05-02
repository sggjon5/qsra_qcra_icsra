import dash
from dash import dcc, html # graphs, sliders and html tags from this
from dash.dependencies import Input, Output # i/o for interactivity callback funcs
import plotly.graph_objs as go
import numpy as np



def serve_dashboard(proj, host: str='127.0.0.1', port: int=8050):
    """
    Launches an interactive ICSRA dashboard using Dash.

    proj: Project object with simulation results
    host: address to bind the server
    port: port number for the dashboard
    """

    # extract sim outputs
    durations = proj.durations
    costs     = proj.costs

    # summary stats, this can probably be updated to be more comprehensive as we print the full table to the console anyway
    summary   = proj.summarise()

    # percentile table
    df_pct    = proj.percentiles()

    # sensitivity analysis of top 10 tasks
    td, tc    = proj.sensitivity(top_n=10) # td = tornado duration, tc = tornado cost

    # axis bounds for sliders and charts
    #TODO round these in some capacity based on size etc
    min_dur, max_dur = float(durations.min()), float(durations.max())
    min_cost, max_cost = float(costs.min()), float(costs.max())

    # set default values to be the p50 for cost and duration
    default_time = summary['P50 Duration']
    default_cost = summary['P50 Cost']

    # slider marks to avoid overlap: only min and max
    cost_marks = {
        min_cost: f"{min_cost:.0f}",
        max_cost: f"{max_cost:.0f}"
    }

    time_marks = {
        min_dur: f"{min_dur:.0f}",
        max_dur: f"{max_dur:.0f}"
    }

    # init dash app
    app = dash.Dash(__name__)

    # layout with histograms, CDFs, joint, tornado, table
    #TODO front end stuff like fonts etc
    app.layout = html.Div([
        html.H1("ICSRA Interactive Dashboard"),

        # cost target slider
        html.Div([
            html.Label("Cost Target"),
            dcc.Slider(
                id='cost-slider',
                min=min_cost,
                max=max_cost,
                step=(max_cost-min_cost)/100,
                value=default_cost,
                marks=cost_marks,
                tooltip={'always_visible': False}
            ),
            html.Div(id='cost-out')
        ], style={'padding':'20px'}),

        # duration target slider
        html.Div([
            html.Label("Time Target"),
            dcc.Slider(
                id='time-slider',
                min=min_dur,
                max=max_dur,
                step=(max_dur-min_dur)/100,
                value=default_time,
                marks=time_marks,
                tooltip={'always_visible': False}
            ),
            html.Div(id='time-out')
        ], style={'padding':'20px'}),

        # univariate plots, histograms and CDF plots
        html.Div([
            html.Div(dcc.Graph(id='duration-hist'), style={'width':'48%','display':'inline-block'}),
            html.Div(dcc.Graph(id='duration-cdf'),  style={'width':'48%','display':'inline-block'})
        ]),
        html.Div([
            html.Div(dcc.Graph(id='cost-hist'), style={'width':'48%','display':'inline-block'}),
            html.Div(dcc.Graph(id='cost-cdf'),  style={'width':'48%','display':'inline-block'})
        ]),

        # joint plots, satter and heatmap
        html.Div([
            html.Div(dcc.Graph(id='joint-scatter'), style={'width':'48%','display':'inline-block'}),
            html.Div(dcc.Graph(id='joint-heatmap'), style={'width':'48%','display':'inline-block'})
        ]),

        # tornado plots of duration and cost
        html.Div(dcc.Graph(id='tornado-duration')),
        html.Div(dcc.Graph(id='tornado-cost')),

        # deciles table
        html.H2("Decile Percentiles"),
        dcc.Graph(
            id='pct-table',
            figure={
                'data': [go.Table(
                    header={'values': list(df_pct.columns)},
                    cells={'values': [df_pct[col] for col in df_pct.columns]}
                )],
                'layout': {'height':300}
            }
        )
    ])

    @app.callback(
        # figures for all graphs
        Output('duration-hist', 'figure'),
        Output('duration-cdf',  'figure'),
        Output('cost-hist',     'figure'),
        Output('cost-cdf',      'figure'),
        Output('joint-scatter', 'figure'),
        Output('joint-heatmap', 'figure'),
        Output('tornado-duration','figure'),
        Output('tornado-cost',    'figure'),

        # slider values
        Input('cost-slider','value'),
        Input('time-slider','value')
    )


    def update_figs(cost_t, time_t):
        """
        Callback to update all figures when sliders change.

        cost_t: selected cost target
        time_t: selected time target
        """

        # extract percentiles
        dur_p50, dur_p90 = summary['P50 Duration'], summary['P90 Duration']
        cost_p50, cost_p90 = summary['P50 Cost'], summary['P90 Cost']

        # --- duration histogram ---
        dur_hist = go.Figure()
        dur_hist.add_trace(go.Histogram(
            x=durations,
            nbinsx=50,
            name='Simulations',
            marker_color='lightgray',
            opacity=0.6,
            showlegend=True
        ))
        # add P50/P90 as line traces for legend
        dur_hist.add_trace(go.Scatter(x=[dur_p50, dur_p50], y=[0, max(np.histogram(durations, bins=50)[0])],mode='lines', line=dict(color='blue', dash='dash'), name='P50'))
        dur_hist.add_trace(go.Scatter(x=[dur_p90, dur_p90], y=[0, max(np.histogram(durations, bins=50)[0])],mode='lines', line=dict(color='green', dash='dot'), name='P90'))
        dur_hist.update_layout(title='Duration Histogram', xaxis_title='Duration', yaxis_title='Count',legend=dict(orientation='h', y=1.1))


        # --- duration CDF ---
        dur_cdf = go.Figure()
        x_dur = np.sort(durations)
        y_dur = np.arange(1, len(x_dur)+1)/len(x_dur)
        dur_cdf.add_trace(go.Scatter(x=x_dur, y=y_dur, mode='lines', line=dict(color='black'), name='CDF'))
        # p50 and 90 lines
        dur_cdf.add_trace(go.Scatter(x=[dur_p50, dur_p50], y=[0,1], mode='lines', line=dict(color='blue', dash='dash'), name='P50'))
        dur_cdf.add_trace(go.Scatter(x=[dur_p90, dur_p90], y=[0,1], mode='lines', line=dict(color='green', dash='dot'), name='P90'))
        dur_cdf.update_layout(title='Duration CDF', xaxis_title='Duration', yaxis_title='CDF',legend=dict(orientation='h', y=1.1))



        # --- cost histogram ---
        cost_hist = go.Figure()
        cost_hist.add_trace(go.Histogram(
            x=costs,
            nbinsx=50,
            name='Simulations',
            marker_color='lightgray',
            opacity=0.6,
            showlegend=True
        ))
        cost_hist.add_trace(go.Scatter(x=[cost_p50, cost_p50], y=[0, max(np.histogram(costs, bins=50)[0])], mode='lines', line=dict(color='blue', dash='dash'), name='P50'))
        cost_hist.add_trace(go.Scatter(x=[cost_p90, cost_p90], y=[0, max(np.histogram(costs, bins=50)[0])],mode='lines', line=dict(color='green', dash='dot'), name='P90'))
        cost_hist.update_layout(title='Cost Histogram', xaxis_title='Cost', yaxis_title='Count', legend=dict(orientation='h', y=1.1))



        # --- cost CDF ---
        cost_cdf = go.Figure()
        x_cost = np.sort(costs)
        y_cost = np.arange(1, len(x_cost)+1)/len(x_cost)
        cost_cdf.add_trace(go.Scatter(x=x_cost, y=y_cost, mode='lines', line=dict(color='black'), name='CDF'))
        # p50 and 90 lines
        cost_cdf.add_trace(go.Scatter(x=[cost_p50, cost_p50], y=[0,1], mode='lines', line=dict(color='blue', dash='dash'), name='P50'))
        cost_cdf.add_trace(go.Scatter(x=[cost_p90, cost_p90], y=[0,1], mode='lines', line=dict(color='green', dash='dot'), name='P90'))
        cost_cdf.update_layout(title='Cost CDF', xaxis_title='Cost', yaxis_title='CDF',legend=dict(orientation='h', y=1.1))




        # --- joint scatter plot duration versus cost ---
        sc = go.Figure()
        sc.add_trace(go.Scatter(x=durations, y=costs, mode='markers', marker=dict(size=4, opacity=0.3), name='Simulations'))
        # p50 and p90 for both cost and duration
        sc.add_trace(go.Scatter(x=[dur_p50, dur_p50], y=[min_cost, max_cost], mode='lines', line=dict(color='blue', dash='dash'), name='P50 Duration'))
        sc.add_trace(go.Scatter(x=[dur_p90, dur_p90], y=[min_cost, max_cost], mode='lines', line=dict(color='green', dash='dot'), name='P90 Duration'))
        sc.add_trace(go.Scatter(x=[min_dur, max_dur], y=[cost_p50, cost_p50], mode='lines', line=dict(color='blue', dash='dash'), name='P50 Cost'))
        sc.add_trace(go.Scatter(x=[min_dur, max_dur], y=[cost_p90, cost_p90], mode='lines', line=dict(color='green', dash='dot'), name='P90 Cost'))
        # target lines in red
        sc.add_trace(go.Scatter(x=[time_t, time_t], y=[min_cost, max_cost], mode='lines', line=dict(color='red', dash='solid'), name='Time Target'))
        sc.add_trace(go.Scatter(x=[min_dur, max_dur], y=[cost_t, cost_t], mode='lines', line=dict(color='red', dash='solid'), name='Cost Target'))
        sc.update_layout(title='Joint Scatter', xaxis_title='Duration', yaxis_title='Cost',legend=dict(orientation='h', y=1.1))

        # --- joint heatmap of density ---
        hm = go.Figure(go.Histogram2d(x=durations, y=costs, nbinsx=50, nbinsy=50, colorscale='Blues', name='Density'))
        hm.update_layout(title='Joint Heatmap', xaxis_title='Duration', yaxis_title='Cost')

        # --- tornado plots fo sensitivity ---
        #TODO i think these should be the other way up because you would be most interested in the most sensitive I think [::-1] might work to just reverse the order
        td_fig = go.Figure(go.Bar(x=list(td.values()), y=list(td.keys()), orientation='h', name='Duration Sensitivity'))
        td_fig.update_layout(title='Tornado: Duration Sensitivity (top 10)', xaxis_title='Correlation')
        tc_fig = go.Figure(go.Bar(x=list(tc.values()), y=list(tc.keys()), orientation='h', name='Cost Sensitivity'))
        tc_fig.update_layout(title='Tornado: Cost Sensitivity (top 10)', xaxis_title='Correlation')


        # return all updated figure objects
        return dur_hist, dur_cdf, cost_hist, cost_cdf, sc, hm, td_fig, tc_fig

    # run the dash server
    app.run(host=host, port=port)
