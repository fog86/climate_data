# %%
import urllib3
import json
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
from datetime import date

"""
Queries historical temperature data from ACIS API for Blue Hill
Observatory outputs visualization

ACIS documentation: http://www.rcc-acis.org/docs_webservices.html
ACIS query builder:  https://builder.rcc-acis.org/
"""

base_url = "http://data.rcc-acis.org/StnData"

http = urllib3.PoolManager()

# site id 190736 is Blue Hills
params = {
    "sid": "190736",
    "sdate": "por",
    "edate": "por",
    "output": "json",
    "elems": [{"name": "mint", "interval": "mly", "duration": 1, "reduce": "min"},
              {"name": "mint", "interval": "mly", "duration": 1, "reduce": "mean"},
              {"name": "maxt", "interval": "mly", "duration": 1, "reduce": "max"},
              {"name": "maxt", "interval": "mly", "duration": 1, "reduce": "mean"},
              {"name": "avgt", "interval": "mly", "duration": 1, "reduce": "mean"}
              ]
}


# %%
url = base_url + "?params=" + json.dumps(params)
req = http.request('GET', url)
result = json.loads(req.data.decode('utf-8'))

# %%
columns = ['YEARMONTH']
data_columns = ['_'.join([x['interval'], x['reduce'], x['name']])
                for x in params['elems']]
columns.extend(data_columns)
# %%
# in result.data, all values will be strings and missing will be 'M'
df = pd.DataFrame(result["data"], columns=columns)

# %%
df["DATE"] = pd.to_datetime(df.YEARMONTH)
df["YEAR"] = df.DATE.dt.year
df["MONTH"] = df.DATE.dt.month

for col in data_columns:
    # convert data columns from strings to numbers and missing 'M' values to Nan
    df[col] = pd.to_numeric(df[col], errors='coerce')
    # add normalized metric
    df[col + '_n'] = df[col].groupby(df["MONTH"]
                                     ).transform(lambda x: (x - x.mean()))

titles = {
    'mly_min_mint': 'Minimum Daily Low Temperature',
    'mly_mean_mint': 'Mean Daily Low Temperature',
    'mly_max_maxt': 'Maximum Daily High Temperature',
    'mly_mean_maxt': 'Mean Daily High Temperature',
    'mly_mean_avgt': 'Mean Daily Mean Temperature',
    'mly_min_mint_n': 'Normalized Minimum Daily Low Temperature',
    'mly_mean_mint_n': 'Normalized Mean Daily Low Temperature',
    'mly_max_maxt_n': 'Normalized Maximum Daily High Temperature',
    'mly_mean_maxt_n': 'Normalized Mean Daily High Temperature',
    'mly_mean_avgt_n': 'Normalized Mean Daily Mean Temperature'
}
# %%
# Plot data


def plot_metric(metric):

    fig = go.Figure(go.Histogram2d(
        z=df[metric],
        x=df.YEAR,
        y=df.MONTH,
        histfunc="avg",
        colorscale='balance',
        xbins_size=10,
        ybins_size=1,
        texttemplate="%{z:.1f}",
        colorbar={"ticksuffix": "°F",
                  "showticksuffix": "last",
                  "nticks": 10}
    ))

    fig.update_layout(
        title="Blue Hill Observatory: " + titles[metric],
        xaxis_tickangle=270,
        xaxis_nticks=36,
        xaxis_title="Year",
        yaxis_title="Month"
    )

    today = date.today()
    note = f'''Data Source: https://www.rcc-acis.org/<br>Aggregated by: Will Gardner, fog86@yahoo.com<br>Updated: {today}'''
    
    fig.add_annotation(
        text=note,
         showarrow=False,
         x=0,
         y=-0.27,
         xref='paper',
         yref='paper' ,
         xanchor='left',
         yanchor='bottom',
         xshift=-1,
         yshift=-5,
         font=dict(size=10, color="grey"),
         align="left"
        )
    
    return fig


# %%
metric = 'mly_mean_avgt_n'
fig = plot_metric(metric)
fig.show()
# %%
pio.write_html(fig, file="index.html", auto_open=False)
