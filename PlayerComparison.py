import numpy as np
import pandas as pd
import streamlit as st #type: ignore
import plotly.express as px #type: ignore
import plotly.graph_objects as go


url = "https://raw.githubusercontent.com/griffisben/Wyscout_Prospect_Research/refs/heads/main/Main%20App/BRI%20Liga%201%2024-25.csv"
df = pd.read_csv(url)
df['player_name'] = df['Full name'].apply(lambda x: x.split()[0][0] + ". " + x.split()[-1])
def pos(series):
  if series.find("GK") != -1:
    return "GK"
  elif series.find("B") != -1:
    return "DF"
  elif series.find("M") != -1:
    return "MF"
  elif series.find("F") != -1:
    return "FW"
  else:
    return "FW"

df['pos'] = df['Primary position'].apply(pos)

float_cols = df.select_dtypes(include=['float64']).columns

for col in float_cols:
    df[col] = round(df[col],2)


params_p90 = [x for x in df.columns if "per 90" in x]
params_df = ['Duels per 90', 'Successful defensive actions per 90', 'Aerial duels per 90', 'Sliding tackles per 90', 'Shots blocked per 90', 'Interceptions per 90', 'Fouls per 90', 'Progressive passes per 90']
params_att = ['Successful attacking actions per 90', 'Goals per 90', 'Non-penalty goals per 90', 'xG per 90', 'Shots per 90', 'Assists per 90', 'Crosses per 90','Dribbles per 90', 'Touches in box per 90']
params_mf = [ 'xA per 90',  'Assists per 90', 'Key passes per 90', 'Passes to final third per 90', 'Passes to penalty area per 90', 'Through passes per 90', 'Progressive passes per 90',]
params_gk = [ 'Conceded goals per 90', 'Shots against per 90', 'xG against per 90', 'Prevented goals per 90', 'Back passes received as GK per 90', 'Exits per 90',]

params_dict = {"GK":params_gk,"DF":params_df,"MF":params_mf,"FW":params_att}


st.title("BRI LIGA 1 - Player Comparison")
col1, col2 = st.columns(2)
with col1:
    teams1 = df['Team within selected timeframe'].unique()
    team1 = st.selectbox("Select Team 1",teams1)
    position1 = st.selectbox("Select Position 1",["GK","DF","MF","FW"])
    player_1 = df[(df['Team'] == team1) & (df['pos'] == position1)]

    selected_player_1 = st.selectbox("Select Player 1",player_1['player_name'])

with col2:
    teams2 = df['Team within selected timeframe'].unique()
    team2 = st.selectbox("Select Team 2",teams2)
    position2 = st.selectbox("Select Position 2",["GK","DF","MF","FW"])
    player_2 = df[(df['Team'] == team2) & (df['pos'] == position2)]

    selected_player_2 = st.selectbox("Select Player 2",player_2['player_name'])

def show_plot():
    if position1 == position2:
        selected_params = params_dict[position1]
    else:
        raise ValueError("Positions must be the same")
    
    comparison1 = df[df['player_name'] == selected_player_1]
    comparison2 = df[df['player_name'] == selected_player_2]

    player_1_values = player_1[player_1['player_name'] == selected_player_1][selected_params].values[0]
    player_2_values = player_2[player_2['player_name'] == selected_player_2][selected_params].values[0]

    player_1_values = [100*round(len(df[df[x]<y])/len(df),2) for y,x in zip(player_1_values,selected_params)]
    player_2_values = [100*round(len(df[df[x]<y])/len(df),2) for y,x in zip(player_2_values,selected_params)]



    N = len(selected_params)

    comparison = pd.DataFrame()
    comparison['player'] = [selected_player_1]*N + [selected_player_2]*N
    comparison['stats'] = selected_params*2
    comparison['percentile'] = np.concatenate([player_1_values,player_2_values])
    fig = px.line_polar(comparison, r='percentile',
                    theta='stats',
                    color='player',
                    line_close=True,
                    color_discrete_sequence=["#00eb93", "#4ed2ff"],
                    width=800,height=650,title=f"<b><span style='color:#00eb93'>{selected_player_1}</span></b> vs <b><span style='color:#4ed2ff'>{selected_player_2}</span></b> by Percentile")

    fig.update_traces(mode="markers+lines",fill='toself')
    fig.update_polars(angularaxis_showgrid=False,
                    radialaxis_gridwidth=0,
                    gridshape='linear',
                    bgcolor="#ffffff",
                    radialaxis_showticklabels=False
                    )

    fig.update_layout(paper_bgcolor="#ffffff",\
                      legend=dict(yanchor="bottom",y=-.2,xanchor="center",x=0.5),\
                      title=dict(x=0.5,xanchor='center',font=dict(family="Roboto",size=30))
                    )
    st.plotly_chart(fig,use_container_width=True)
    
    outfield = ['Team within selected timeframe','Age','Matches played','Minutes played','Goals','Non-penalty goals','xG','Assists','xA','Duels won, %','Shots','Accurate crosses, %','Successful dribbles, %','Accurate passes, %','Accurate through passes, %','Accurate progressive passes, %']
    goalie = ['Team within selected timeframe','Conceded goals','Shots against','Clean sheets','Save rate, %','xG against','Prevented goals']

    parameters = outfield if position1 != "GK" else goalie
    
    column1, column2,column3 = st.columns(3)

    with column1:
        st.markdown(f"<p style='font-size: large; text-align: center; color: black; font-weight: bold;'>{comparison1['Full name'].values[0]}</p>",unsafe_allow_html=True)
        st.markdown(f"<img src='{comparison1['Team logo'].values[0]}' style='display: block; margin: 0 auto;'>" , unsafe_allow_html=True)
    
    with column2:
        st.subheader("")

    with column3:
        st.markdown(f"<p style='font-size: large; text-align: center; color: black; font-weight: bold;'>{comparison2['Full name'].values[0]}</p>",unsafe_allow_html=True)
        st.markdown(f"<img src='{comparison2['Team logo'].values[0]}' style='display: block; margin: 0 auto;'>" , unsafe_allow_html=True)

    data = pd.DataFrame()
    data[selected_player_1] = df[df["player_name"] == selected_player_1][parameters[1:]].values[0]
    data['Statistic'] = parameters[1:]
    data[selected_player_2] = df[df["player_name"] == selected_player_2][parameters[1:]].values[0]

    first = ["#00eb93" if x>y else "#ffffff" for x,y in zip(data[selected_player_1],data[selected_player_2])]
    stats_color = ['#ffffff']*len(first)
    second = ["#4ed2ff" if y>x else "#ffffff" for x,y in zip(data[selected_player_1],data[selected_player_2])]

    fig1 = go.Figure(layout=dict(height=550),data=[go.Table(columnwidth = [40,120,40],
    header=dict(values=[f"<b>{x}</b>" for x in data.columns],
                fill_color='black',
                font=dict(color='white', size=12),
                align=['left','center','right'],
                font_size=15),
    cells=dict(values=[data[x] for x in data.columns],
               fill_color=[first,stats_color, second],
               align=['left','center','right'],
               line_color=[first,stats_color, second],
               font_size=12))
    ])

    st.plotly_chart(fig1)

st.button("Compare",key="compare",on_click=show_plot)
