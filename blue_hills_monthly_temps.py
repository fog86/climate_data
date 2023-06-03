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

def format_title(title, subtitle=None, subtitle_font_size=12):
    title = f'{title}'
    if not subtitle:
        return title
    subtitle = f'<span style="font-size: {subtitle_font_size}px;">{subtitle}</span>'
    return f'{title}<br>{subtitle}'


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

    today = date.today()
    title = "Blue Hill Observatory: " + titles[metric]
    subtitle = f'''Data Source: https://www.rcc-acis.org/, Contact: fog86@yahoo.com, Updated: {today}'''

    fig.update_layout(
        title=format_title(title, subtitle, 10),
        xaxis_tickangle=270,
        xaxis_nticks=36,
        xaxis_title="Year",
        yaxis_title="Month"
        )

    return fig


# %%
metric = 'mly_mean_avgt_n'
fig = plot_metric(metric)
fig.show()
# %%
pio.write_html(fig, file="index.html", auto_open=False)
