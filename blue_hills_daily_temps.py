# %%
import urllib3
import json
import pandas as pd
import plotly.graph_objects as go
# import plotly.io as pio

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
    "elems": [{"name": "mint", "interval": "dly", "duration": 1, "reduce": "min"},
              {"name": "mint", "interval": "dly", "duration": 1, "reduce": "mean"},
              {"name": "maxt", "interval": "dly", "duration": 1, "reduce": "max"},
              {"name": "maxt", "interval": "dly", "duration": 1, "reduce": "mean"},
              {"name": "avgt", "interval": "dly", "duration": 1, "reduce": "mean"}
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
df["DOY"] = df.DATE.dt.day_of_year

for col in data_columns:
    # convert data columns from strings to numbers and missing 'M' values to Nan
    df[col] = pd.to_numeric(df[col], errors='coerce')
    # add normalized metric
    df[col + '_n'] = df[col].groupby(df["MONTH"]
                                     ).transform(lambda x: (x - x.mean()))

titles = {
    'dly_min_mint': 'Daily Low Temperature',
    'dly_mean_mint': 'Daily Low Temperature',
    'dly_max_maxt': 'Daily High Temperature',
    'dly_mean_maxt': 'Daily High Temperature',
    'dly_mean_avgt': 'Daily Mean Temperature',
    'dly_min_mint_n': 'Normalized Daily Low Temperature',
    'dly_mean_mint_n': 'Normalized Daily Low Temperature',
    'dly_max_maxt_n': 'Normalized Daily High Temperature',
    'dly_mean_maxt_n': 'Normalized Daily High Temperature',
    'dly_mean_avgt_n': 'Normalized Daily Mean Temperature'
}
# %%
# Plot data


def plot_metric(metric):

    fig = go.Figure(go.Heatmap(
        z=df[metric],
        x=df.YEAR,
        y=df.DOY,
        text=df.YEARMONTH,
        colorscale='balance',
        colorbar={"ticksuffix": "°F",
                  "showticksuffix": "last",
                  "nticks": 10}
    ))

    fig.update_layout(
        title="Blue Hill Observatory: " + titles[metric],
        xaxis_tickangle=270,
        xaxis_nticks=36,
        xaxis_title="Year",
        yaxis_title="Day of Year",
    )
    return fig


# %%
metric = 'dly_mean_avgt'
fig = plot_metric(metric)
fig.show()
# %%
