#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
import random
import os
import base64
import calendar
import datetime

import plotly.express as px
import plotly.graph_objects as gp 

import dash
from dash import Dash, dcc, html, Input, Output, State
from jupyter_dash import JupyterDash
import dash_bootstrap_components as dbc


# In[2]:


image_filename =  'star.jpg'
encoded_image = base64.b64encode(open(image_filename, 'rb').read())
month_years = ["Feb2021-Current","Feb-2021", "Mar-2021", "Apr-2021", "May-2021", "Jun-2021", 
          "Jul-2021", "Aug-2021", "Sep-2021", "Oct-2021", "Nov-2021", "Dec-2021", "Jan-2022", "Feb-2022", "Mar-2022"]
regions = ['Myanmar','Ayeyarwady','Bago','Magway', 'Mandalay', 'Sagaing', 'Taninthayi', 'Yangon', 
           'Kachin', 'Kayah', 'Kayin', 'Chin','Mon', 'Rakhine', 'Shan']
coldict = dict({'M':'blue', 'F':'red', 'NAN': 'green', 'LGBT': 'yellow'})

df = pd.read_csv('Project1.csv', index_col = 0)
tot_death = '{:,d}'.format(df.shape[0])
last_date = datetime.datetime.strptime(df.iloc[-1,0], '%Y-%m-%d').strftime('%d-%b-%Y')
topdate = df.describe().loc['top','Deceased_date']
topdate = datetime.datetime.strptime(topdate, '%Y-%m-%d').strftime('%d-%b-%Y')
g_ratio = df['Sex'].value_counts().to_frame()


col1 = ["Total Male", "Total Female", "Undefined", "Total LGBT"]
col2 = list(g_ratio['Sex'])
col3 = ["Youngest Age", "Oldest Age", "Red Region", "Green Region"]
col4 = ["1 year and 6 months", 90, " ", " "]

colName = ["Total Loss", tot_death, "Highest Loss on", topdate]
dfsummary = pd.DataFrame({colName[0]: col1, colName[1]:col2, colName[2]:col3, colName[3]:col4})


# In[3]:


def timedata_extraction(period):  
    
    df['Year'] = pd. DatetimeIndex(df['Deceased_date']).year
    df['Month'] = pd. DatetimeIndex(df['Deceased_date']).month
    df['Day'] = pd. DatetimeIndex(df['Deceased_date']).day
    df['Month_N'] = df['Month'].apply(lambda x: calendar.month_abbr[x])
    df['Month-Year']= df['Month_N'].astype(str) + '-'+ df['Year'].astype(str)
   
    
    if (period == "Feb2021-Current"):
    
        dtoll = df.groupby(['Month-Year', 'Sex']).count()[['Deceased_date']]
        dtoll.rename(columns={'Deceased_date': 'Number'},inplace = True)
        dtoll.reset_index(inplace = True)

        dtoll['Month-Year'] = pd.Categorical(dtoll['Month-Year'], categories=month_years[1:])
        dtoll.sort_values(["Month-Year", 'Sex'], inplace = True)

        dt = dtoll.groupby('Month-Year').sum()
        dt.reset_index(inplace = True)
    else:
        
        df1 = df[df['Month-Year']==period].copy()

        dtoll = df1.groupby(['Deceased_date', 'Sex']).count()[['Year']]
        dtoll.rename(columns = {'Year': 'Number'}, inplace = True)
        dtoll.reset_index(inplace = True)
        dtoll.sort_values(['Deceased_date', 'Sex'], ascending = (True, True), inplace = True)
        
        dt = dtoll.groupby('Deceased_date').sum()
        dt.reset_index(inplace = True)

    return [dtoll, dt] 


# In[4]:


def bytime_graph(period):
    
    [dtoll, dt] = timedata_extraction(period)
    colseq = [coldict[key] for key in list(dtoll['Sex'].unique())]
    if (period == "Feb2021-Current"):  
        xvalue = 'Month-Year'
        periodstr = '2021 Feb and 2022 March'        
       
    else:
        xvalue = 'Deceased_date'
        periodstr = period        
        
    
    fig = px.bar(dtoll, x = xvalue, y = 'Number', color = 'Sex',  hover_data = ['Number'],
                color_discrete_sequence= colseq, 
                title="Death Tolls due to Military Coup during " + periodstr)
    
    fig.update_layout(yaxis_title = 'Number of Deaths', 
                      xaxis = dict(tickvals = dtoll[xvalue],ticktext = dtoll[xvalue],title = ''))

    fig.update_layout(
        annotations=[
            {"x": x, "y": total*1.05, "text": f"{total}", "showarrow": False}
            for x, total in dt.values
        ]
    )
           
    return fig


# In[5]:


app = JupyterDash(external_stylesheets=[dbc.themes.JOURNAL, dbc.icons.FONT_AWESOME])

app.title = "Tribute to STARs"
server = app.server


# In[6]:


badge = dbc.Button(
    [
        "Notifications",
        dbc.Badge(
            "99+",
            color="danger",
            pill=True,
            text_color="white",
            className="position-absolute top-0 start-100 translate-middle",
        ),
    ],
    color="primary",
    className="position-relative",
)


# In[7]:


app.layout = dbc.Container(
    [
    html.Div([
        html.Img(src='data:image/jpg;base64,{}'.format(encoded_image.decode()),
                height=200),
        html.Div([
            dbc.Button(tot_death, color="danger", size = 'lg'),
            dbc.Button("were killed between", color="dark", size = 'lg'),
            dbc.Button("01-Feb-2021 and " + last_date, color="dark", size = 'lg'),
        ],className="d-grid gap-2"),
   
              
    ], style = {'display': 'flex'}),
    html.Br(),
    html.Br(),
    html.Hr(),     
    html.Div([
            dbc.Button("Data Source", color = "info", id="source",className="mb-3", n_clicks=0, size = 'lg'),
            dbc.Button("Summary", color = "primary", id="stat",className="mb-3", n_clicks=0, size = 'lg'),        
            dbc.Button("By Age Group", color = "secondary", id="age",className="mb-3", n_clicks=0, size = 'lg'),
        
            dbc.Button("By Time", color = "warning", id="time",className="mb-3", n_clicks=0, size = 'lg'),        
            dbc.Button("By Region", color = "danger", id="region",className="mb-3", n_clicks=0, size = 'lg'),
            dbc.Button("By Organization", color = "secondary", id="org",className="mb-3", n_clicks=0, size = 'lg'),
            ],className="d-grid gap-3 d-md-flex justify-content-md-left", style = {'display': 'flex'}), 
        
    dbc.Row([
        dbc.Col(
            dbc.Collapse(
                dbc.Card(dbc.CardBody(dbc.CardLink("Data is downloaded from AAPP", 
                      href="https://aappb.org"))
                    ), style={'height':'50px','width': '450px'}, id="dsourcelink", is_open=False),
        ),   
        dbc.Col(
            dbc.Collapse(dcc.Dropdown(
                id = 'time_id', options=[{'label':state,'value':state} for state in month_years],            
                value='Feb2021-Current', 
                style={'border': '#00ff8b','color': '#5e34eb','borderStyle':'dashed','height':'50px','width': '350px'} ), 
                         id="dd-time", is_open=False),
        ), 
        dbc.Col(
            dbc.Collapse(dcc.Dropdown(
                id = 'region_id', options=[{'label':state,'value':state} for state in regions],            
                value='Myanmar', style={'border': '#ff0000','color': '#5e34eb','borderStyle':'dashed','height':'50px','width': '350px'} ),
                         id="dd-region", is_open=False),
        ), 
        ],className="mt-3",),  

        html.Br(),
        dbc.Collapse(dbc.Table.from_dataframe(dfsummary, striped=True, bordered=True, color = "primary", hover=True), 
                     id="summary-tb",is_open=False),   
        
        dbc.Collapse(dcc.Graph(id='plot1'), id = "graph-id", is_open=False),
    # output graph
    

    ]
)


# In[8]:


@app.callback(
    Output("dsourcelink", "is_open"),
    [Input("source", "n_clicks")],
    [State("dsourcelink", "is_open")],
)

def toggle_collapse(source, is_open):
    if source:
        return not is_open
    return is_open


# In[9]:


@app.callback(
    Output("summary-tb", "is_open"),
    [Input("stat", "n_clicks")],
    [State("summary-tb", "is_open")],
)

def toggle_collapse(stat, is_open):
    if stat:
        return not is_open
    return is_open


# In[10]:


@app.callback(
    Output("dd-time", "is_open"),
    [Input("time", "n_clicks")],
    [State("dd-time", "is_open")],
)

def toggle_collapse(time, is_open):
    if time:
        return not is_open
    return is_open


# In[11]:


@app.callback(
    Output("graph-id", "is_open"),
    [Input("time", "n_clicks")],
    [State("graph-id", "is_open")],
)

def toggle_collapse(time, is_open):
    if time:
        return not is_open
    return is_open


# In[12]:


@app.callback(
    Output("dd-region", "is_open"),
    [Input("region", "n_clicks")],
    [State("dd-region", "is_open")],
)

def toggle_collapse(region, is_open):
    if region:
        return not is_open
    return is_open


# In[13]:


@app.callback(
    Output("plot1", "figure"),
    [Input("time_id", "value")],
)

def draw_figure(b):
    if b is None:
        fig = bytime_graph('Feb2021-Current')
    else:
        fig = bytime_graph(b)
    return fig


# In[14]:


if __name__ == '__main__':
    port = 5000 + random.randint(0, 999)    
    url = "http://127.0.0.1:{0}".format(port)    
    app.run_server(use_reloader=False, debug=True, port=port)


# In[ ]:




