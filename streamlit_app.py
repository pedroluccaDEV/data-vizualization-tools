import streamlit as st
import pandas as pd
import os
import plotly.express as px
import plotly.graph_objects as go

# Configuração da página
st.set_page_config(page_title="Spotify Popular Songs Dashboard", layout="wide")

# Função para carregar os dados
@st.cache_data
def load_data():
    file_path = os.path.join(os.path.dirname(__file__), "songs.csv")
    try:
        data = pd.read_csv(file_path, encoding="ISO-8859-1")
        
        # Convertendo a coluna de data para datetime
        data['track_album_release_date'] = pd.to_datetime(data['track_album_release_date'], errors='coerce')
        
        # Corrigindo tipos de dados numéricos
        data['track_popularity'] = data['track_popularity'].astype(float)
        data['danceability'] = data['danceability'].astype(float)
        data['energy'] = data['energy'].astype(float)
        data['loudness'] = data['loudness'].astype(float)
        data['speechiness'] = data['speechiness'].astype(float)
        data['acousticness'] = data['acousticness'].astype(float)
        data['valence'] = data['valence'].astype(float)
        data['tempo'] = data['tempo'].astype(float)
        data['duration_ms'] = data['duration_ms'].astype(int)
        
        return data
    except Exception as e:
        st.error(f"Erro ao carregar o arquivo: {e}")
        return pd.DataFrame()

# Função para criar gráficos de barras horizontais (Top 15 de 2020)
def create_top_15_2020(df, title):
    # Filtrando as 15 músicas mais populares de 2020
    df_2020 = df[df['track_album_release_date'].dt.year == 2020]
    top_15_2020 = df_2020.nlargest(15, 'track_popularity')[['track_name', 'track_popularity']]
    
    # Gráfico de barras horizontais
    fig = px.bar(top_15_2020, 
                 x='track_popularity', 
                 y='track_name', 
                 orientation='h', 
                 title=title, 
                 color='track_popularity',
                 color_continuous_scale="greens")  # Cor verde
    
    fig.update_layout(
        xaxis_title="Popularity", 
        yaxis_title="Track Name",
        bargap=0.1  # Aumentando a largura das barras
    )
    st.plotly_chart(fig, use_container_width=True)

# Função para criar gráfico de barras para o top 1 de cada ano
def create_top_1_each_year(df, title):
    # Selecionando o top 1 de cada ano
    top_1_per_year = df.loc[df.groupby(df['track_album_release_date'].dt.year)['track_popularity'].idxmax()]
    top_1_per_year = top_1_per_year[['track_name', 'track_album_release_date', 'track_popularity']]
    
    # Gráfico de barras verticais
    fig = px.bar(top_1_per_year, 
                 x='track_album_release_date', 
                 y='track_popularity', 
                 title=title, 
                 color='track_popularity',
                 color_continuous_scale="greens",  # Cor verde
                 labels={"track_album_release_date": "Year", "track_popularity": "Popularity"})
    
    fig.update_layout(
        xaxis_title="Year", 
        yaxis_title="Popularity",
        bargap=0.15  # Aumentando a largura das barras
    )
    st.plotly_chart(fig, use_container_width=True)

# Função para filtrar os dados por ano e artista
def filter_data(df, start_year, end_year, artist_filter):
    # Filtrando por ano
    df_filtered = df[(df['track_album_release_date'].dt.year >= start_year) & 
                     (df['track_album_release_date'].dt.year <= end_year)]
    
    # Filtrando por artista
    if artist_filter:
        df_filtered = df_filtered[df_filtered['track_artist'].str.contains(artist_filter, case=False, na=False)]
    
    return df_filtered

# Função para criar Gauge Chart
def create_gauge_chart(value, title):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={'text': title},
        gauge={
            'axis': {'range': [0, 1]},
            'bar': {'color': "#329542"},  # Cor verde
            'steps': [
                {'range': [0, 0.25], 'color': "#D9F7E8"},
                {'range': [0.25, 0.5], 'color': "#A9E8A3"},
                {'range': [0.5, 0.75], 'color': "#74C374"},
                {'range': [0.75, 1], 'color': "#329542"}
            ]
        }
    ))
    fig.update_layout(height=300, width=500)  # Aumentando o tamanho do gráfico
    return fig

# Carregar dados
df = load_data()

# Verificar se os dados foram carregados corretamente
if not df.empty:
    # Filtros do painel lateral
    st.sidebar.title("Filters")
    st.sidebar.header("⚙️ Settings")

    # Filtros de ano
    max_year = df['track_album_release_date'].dt.year.max()
    min_year = df['track_album_release_date'].dt.year.min()
    start_year = st.sidebar.slider("Start Year", min_year, max_year, min_year)
    end_year = st.sidebar.slider("End Year", min_year, max_year, max_year)

    # Filtro de artista
    artist_filter = st.sidebar.text_input("Filter by Artist", "")

    # Aplicando filtros
    filtered_df = filter_data(df, start_year, end_year, artist_filter)
    
    # Sessão 1: Gráficos principais (Top 15 de 2020 e Top 1 por Ano)
    st.markdown(f"# Spotify Popular Songs Dashboard")
    st.markdown(f">**This dataset contains a collection of the most popular songs on Spotify, along with various attributes that can be used for music analysis and recommendation systems. It includes audio features, lyrical details, and general metadata about each track, making it an excellent resource for machine learning, data science, and music analytics projects.**")
    st.markdown(f"*link:* https://www.kaggle.com/datasets/rishabhpancholi1302/spotify-most-popular-songs-dataset")
    st.markdown(f"---")
    
    st.markdown(f"## Geral Data View")
    
    col1, col2 = st.columns(2)

    with col1:
        create_top_15_2020(filtered_df, 'Top 15 Most Popular Tracks of 2020')

    with col2:
        create_top_1_each_year(filtered_df, 'Top 1 Track of Each Year')

    st.markdown(f"---")
    st.markdown(f"## Muisic data View")
    # Seleção de música
    track_selected = st.selectbox("Select a track", filtered_df['track_name'].unique())
    track_data = filtered_df[filtered_df['track_name'] == track_selected]

    if not track_data.empty:
        # Exibindo o cover da música e informações ao lado
        track = track_data.iloc[0]
        
        # Exibindo a imagem do cover e informações ao lado
        col1, col2 = st.columns([1, 2.5])  # Ajustando a proporção das colunas para não invadir o cover

        with col1:
            # Exibindo a imagem do cover
            st.markdown(f"#### Music Cover")
            st.image(track['image_url'], width=300, caption="Track Cover")

        with col2:
           # Exibindo as informações da música (ajustado para a direita)
            st.markdown(f"### Music Info")
            st.markdown(f"#### {track['track_name']}")
            st.markdown(f"**Artist:** {track['track_artist']}")
            st.markdown(f"**Release Date:** {track['track_album_release_date'].strftime('%B %d, %Y')}")
            st.markdown(f"**Popularity (Streams):** {track['track_popularity']:.0f}")

            # Exibindo Acousticness, Danceability e Valence como porcentagens
            acousticness_percent = round(track['acousticness'] * 100, 2)
            danceability_percent = round(track['danceability'] * 100, 2)
            valence_percent = round(track['valence'] * 100, 2)

            st.markdown(f"**Acousticness:** {acousticness_percent}%")
            st.markdown(f"**Danceability:** {danceability_percent}%")
            st.markdown(f"**Valence:** {valence_percent}%")

        # Criando os Gauge Charts (Energy e Danceability) com valores em porcentagem
        col1, col2 = st.columns(2)

        # Energy com porcentagem
        with col1:
            energy_percent = round(track['energy'] * 100, 2)  # Multiplicando por 100 e arredondando
            st.subheader(f"Energy of {track['track_name']} ({energy_percent}%)")  # Exibindo como porcentagem
            fig_energy = create_gauge_chart(track['energy'], "Energy")
            st.plotly_chart(fig_energy, use_container_width=True)

        # Danceability com porcentagem
        with col2:
            danceability_percent = round(track['danceability'] * 100, 2)  # Multiplicando por 100 e arredondando
            st.subheader(f"Danceability of {track['track_name']} ({danceability_percent}%)")  # Exibindo como porcentagem
            fig_danceability = create_gauge_chart(track['danceability'], "Danceability")
            st.plotly_chart(fig_danceability, use_container_width=True)

    
else:
    st.error("Nenhum dado foi carregado. Verifique se o arquivo CSV está no local correto.")
