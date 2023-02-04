# %%
import plotly.express as px
import plotly.io as pio
import pandas as pd

data_file = r"https://raw.githubusercontent.com/elizabethts/publish-plotly-website/master/airbnb.csv"


# %%
def clean_data(df):
    
    # replace numbers with strings
    df.neighborhood = df.neighborhood.map({1 : 'Friedrichshain-Kreuzberg', 2 : 'Mitte', 3 : 'Pankow', 4 : 'Neukölln', 5 :'Charlottenburg-Wilm',
                        6 : 'Tempelhof - Schöneberg', 7 : 'Lichtenberg', 8 : 'Treptow - Köpenick', 9 : 'Steglitz - Zehlendorf',
                        10 : 'Reinickendorf', 11 : 'Marzahn - Hellersdorf', 12 : 'Spandau'})

    df.room_type = df.room_type.map({1 : 'Entire home/apt', 2 : 'Private room', 3 : 'Shared room'})

    yes_no_dict = {0: 'No', 1:'Yes'}
    df.wifi = df.wifi.map(yes_no_dict)
    df.washer = df.washer.map(yes_no_dict)
    df.cable_tv = df.cable_tv.map(yes_no_dict)
    df.kitchen = df.kitchen.map(yes_no_dict)
    
    # rename columns
    df.rename(columns={'neighborhood': 'Neighborhood', 'room_type': 'Room Type', 'accommodates': 'Accommodates',
                      'bedrooms': 'Bedrooms', 'number_of_reviews': 'Number of Reviews', 'wifi': 'Wifi', 'cable_tv': 'Cable TV',
                      'washer': 'Washer', 'kitchen': 'Kitchen', 'price': 'Price (US Dollars)'}, inplace=True)
    
    # remove outliers
    df = df[df['Price (US Dollars)']<501]
    
    return df

# %%
df = pd.read_csv(data_file) # path to  csv
df = clean_data(df)
# %%
fig = px.scatter(df, x='Neighborhood', y='Price (US Dollars)'
                 ,size='Accommodates'
                 , hover_data=['Bedrooms', 'Wifi', 'Cable TV', 'Kitchen', 'Washer', 'Number of Reviews']
                 ,color= 'Room Type')
fig.update_layout(template='plotly_white')
fig.update_layout(title='How much should you charge in a Berlin neighborhood?')
fig.show()
# %%
pio.write_html(fig, file="index.html", auto_open=False)
# %%
