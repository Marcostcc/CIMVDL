import streamlit as st
import pandas as pd
import duckdb as duck
import altair as alt
import geopandas as gpd

# Connect to the database
with duck.connect('CIM_VDL.duckdb') as cursor:
    cursor.execute(open('views.sql').read())


#######################################################################  LISTAS/ DICTS  ########################################################################################

# Criar lista com os concelhos
concelhos = ['Aguiar da Beira', 'Carregal do Sal', 'Castro Daire', 'Mangualde',
       'Nelas', 'Oliveira de Frades', 'Penalva do Castelo',
       'Santa Comba Dão', 'São Pedro do Sul', 'Sátão', 'Tondela',
       'Vila Nova de Paiva', 'Viseu', 'Vouzela']

#################################################################  HEADER STUFF  ###############################################################################################

# Deixa o dash expandir até a largura da pagina
st.set_page_config(layout='wide', initial_sidebar_state='expanded')

# Importando o style.css 
with open('C:/Users/marco/Documents/MEGA/TESE/Streamlit/style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Criar o header no sidebar, o `´ no version 2 highlites o texto
st.sidebar.header('SMART CIM `Dashboard`')

# cria o select box no sidebar para filtrar 
st.sidebar.subheader('Dormidas em Viseu Dão Lafões')
select1 = st.sidebar.selectbox('Escolha o Concelho', concelhos) 

#######################################################################  FUNÇÕES  ###########################################################################################

# Função para ler um geopackage e retornar um geodataframe
def read_gpkg(gpkg_path, layer_name):
    return gpd.read_file(gpkg_path, layer=layer_name, driver='GPKG')


#######################################################################  QUEM DORMIU  #########################################################################################

# Titulo da pagina
st.title('Quem Dormiu em' + ' ' + select1)

# Query para obter os dados
with duck.connect('CIM_VDL.duckdb') as cursor:
    dfq = pd.DataFrame(data=cursor.execute("select * from quem_dormiu_nac_concelho").fetchall(), columns=["pais_origem", "geo_area_nome", "concelho_residencia","dormidas_totais"])

gdf = read_gpkg('C:/Users/marco/Documents/MEGA/CIMVDL/CIM-VDL/geopackages/portugal_con.gpkg', 'portugal_con')

#merge dos dados com o geodataframe
gdf = gdf.merge(dfq, left_on='Concelho', right_on='concelho_residencia', how='left')
gdf = gdf.to_crs(epsg=4326)

# criar cloropleth map com os dados
a1, a2, a3 = st.columns((4,3,3))

with a1:
    st.write('Visitantes Internacionais')
    chart = alt.Chart(gdf[gdf.geo_area_nome == select1]).mark_geoshape().encode(
        color='dormidas_totais:Q'
    ).properties(
        width=400,
        height=400
    )
    st.altair_chart(chart)
