# %%
import pandas as pd
import plotly.express as px
import plotly.io as pio
import numpy as np
import plotly.graph_objects as go

#pio.renderers.default = "browser"

# %%
data_file = "Boston weather data 20230207.csv"
df_raw = pd.read_csv(data_file)
# %%

keep_station = "BLUE HILL COOP, MA US"

df = pd.DataFrame({"DATE": pd.to_datetime(df_raw.DATE),
                  "TMAX": df_raw.TMAX, "TMIN": df_raw.TMIN, "LOC": df_raw.NAME})
# %%
df = df[df["LOC"]==keep_station]
df["DOY"] = df.DATE.dt.day_of_year
df["YEAR"] = df.DATE.dt.year
df["THETA"] = df.DOY * 360 / 365
df["TMAX_ma"] = df.TMAX.rolling(30).mean()
df["TMIN_ma"] = df.TMIN.rolling(30).mean()
df["YEARMONTH"] = df.DATE.dt.strftime('%Y-%m')
df["MONTH"] = df.DATE.dt.month


#del(df_raw)
#df.drop(df.loc[df.TMAX>110].index, inplace=True) #outlier at 130deg
#df.drop(df.loc[df.YEAR==1998].index, inplace=True) #1998 is incomplete
# %%
# Plot temp vs time by location
fig = px.scatter(df, x='DATE', y='TMIN', color='DOY', facet_col='LOC'
                 )
fig.show()
# %%
# plot temp vs day of year, polar plot
fig2 = px.scatter_polar(df, r="TMIN", theta="THETA", color="YEAR",)
fig2.show()

# %%
df["Y"] = df["TMAX_ma"] * np.sin(np.radians(df.THETA))
df["X"] = df["TMAX_ma"] * np.cos(np.radians(df.THETA))

# %%
fig4 = px.scatter(df, x="DOY", y="TMAX_ma", color="YEAR")
fig4.show()
# %%
fig5 = px.scatter_3d(df, x="YEAR", y="DOY", z="TMAX_ma", color="TMAX_ma")
fig5.show()


# %%
# cartesian 3D plot
x, y, z = df.YEAR, df.DOY, df.TMAX_ma
layout = go.Layout(scene=dict(aspectmode="manual",
                   aspectratio=dict(x=3, y=2, z=1)))

fig = go.Figure(
	data=[go.Scatter3d(x=x, y=y, z=z, mode='markers',
                    marker=dict(
                        size=2,
                        color=z,
                        #colorscale ='Viridis',
                        #opacity = 0.8
                    ))],
	layout=layout)

fig.show()
# %%
x2, y2, z2 = df.DATE, df.X, df.Y #df.X, df.Y, df.DATE

layout = go.Layout(scene=dict(aspectmode="manual",
                   aspectratio=dict(x=3, y=1, z=1)))

fig = go.Figure(
	data=[go.Scatter3d(x=x2, y=y2, z=z2, mode='markers',
                    marker=dict(
                        size=2,
                        color=df.TMAX_ma,
                        #colorscale ='Viridis',
                        #opacity = 0.8
                    ))],
	layout=layout)

fig.show()

# %%

df_by_month = df.groupby(["YEARMONTH", "MONTH"])["TMIN"].min().to_frame().reset_index()
# %%

fig = px.line(df_by_month, x='YEARMONTH', y='TMIN', color='MONTH',
    color_discrete_sequence=px.colors.qualitative.Dark24)
fig.show()
# %%
