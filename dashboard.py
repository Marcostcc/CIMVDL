import streamlit as st
import pandas as pd
import duckdb as duck
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from matplotlib.patheffects import withStroke
#import altair as alt
#import geopandas as gpd

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
st.title('Total de estadias (em pessoa-dias) em' + ' ' + select1)

# A1. Query para obter os dados INTERNACIONAIS
with duck.connect('CIM_VDL.duckdb') as cursor:
    quem_dormiu_int_concelho = pd.DataFrame(data=cursor.execute("select * from quem_dormiu_int_concelho").fetchall(), columns=["pais_origem", "geo_area_nome","dormidas_totais"])

# A1. rename 'Guadeloupe and Martinique and French Guiana' in pais_origem to 'France'
quem_dormiu_int_concelho['pais_origem'] = quem_dormiu_int_concelho['pais_origem'].replace('Guadeloupe and Martinique and French Guiana', 'France')

# A1. open geojson file
world = read_gpkg('C:/Users/marco/Documents/MEGA/CIMVDL/CIM-VDL/geopackages/mundo_simples.gpkg', 'mundo_simples')

# A1. merge dos dados com o geodataframe
world_gdf = world.merge(quem_dormiu_int_concelho, left_on='NAME_PT', right_on='pais_origem', how='left')
#-----------------------------------------------------------------------------#

# A2. Query para obter os dados NACIONAIS
with duck.connect('CIM_VDL.duckdb') as cursor:
    quem_dormiu_nac_concelho = pd.DataFrame(data=cursor.execute("select * from quem_dormiu_nac_concelho").fetchall(), columns=["pais_origem", "geo_area_nome", "concelho_residencia","dormidas_totais"])

# A2. geodataframe de PORTUGAL
portugal_con = read_gpkg('C:/Users/marco/Documents/MEGA/CIMVDL/CIM-VDL/geopackages/simplified_portugal.gpkg', 'simplified')

# A2. merge dos dados com o geodataframe
portugal_gdf = portugal_con.merge(quem_dormiu_nac_concelho, left_on='Concelho', right_on='concelho_residencia', how='left')

#-----------------------------------------------------------------------------#

# A3. Query para obter os dados VISEU DÃO LAFÕES
with duck.connect('CIM_VDL.duckdb') as cursor:
    quem_dormiu_reg_concelho = pd.DataFrame(data=cursor.execute("select * from quem_dormiu_reg_concelho").fetchall(), columns=["pais_origem", "geo_area_nome", "concelho_residencia","dormidas_totais"])

# A3. geodataframe de VDL
vdl_con = read_gpkg('C:/Users/marco/Documents/MEGA/CIMVDL/CIM-VDL/geopackages/vdl_con.gpkg', 'vdl_con')

# A3. merge dos dados com o geodataframe
vdl_gdf = vdl_con.merge(quem_dormiu_reg_concelho, left_on='Concelho', right_on='concelho_residencia', how='left')


# criar cloropleth map com os dados
a1, a2, a3 = st.columns((4,3,3))

# with a1 plot the map for the world with the selected concelho
with a1:
    # add discriptive
    #st.write('Residentes Internacionais')
    # Plot the geometry of the world with gray color
    fig, ax = plt.subplots(figsize=(10, 6))
    world_gdf.plot(ax=ax, color='lightgray')

    # Plot the geometry of the world with LogNorm color scale
    world_gdf[world_gdf['geo_area_nome'] == select1].plot(column='dormidas_totais', cmap='viridis', legend=True, ax=ax, norm=LogNorm(vmin=1, vmax=20000))
    #Add the names of distritos to portugal
    # for distrito in world_gdf['Distrito'].unique():
    #     x = world_gdf[world_gdf['Distrito'] == distrito].unary_union.centroid.x
    #     y = world_gdf[world_gdf['Distrito'] == distrito].unary_union.centroid.y
    #     ax.annotate(distrito, xy=(x, y), xytext=(3, 3), textcoords='offset points', fontsize=8, color='black', zorder=3, path_effects=[withStroke(linewidth=4, foreground='w')])

    # Set title and remove axis labels
    plt.title('Visitantes Residentes Internacionais')
    plt.gca().patch.set_alpha(0)
    plt.axis('off')
    st.pyplot(fig)

# with a2 plot the map for portugal with the selected concelho
with a2:
    # add discriptive
    #st.write('Residentes em Portugal')
    # Plot the geometry of Portugal with gray color
    fig, ax = plt.subplots(figsize=(10, 6))
    portugal_gdf.plot(ax=ax, color='lightgray')

    # Plot the geometry of Viseu with LogNorm color scale
    portugal_gdf[portugal_gdf['geo_area_nome'] == select1].plot(column='dormidas_totais', cmap='viridis', legend=True, ax=ax, norm=LogNorm(vmin=1, vmax=20000))
    #Add the names of distritos to portugal
    # for distrito in portugal_gdf['Distrito'].unique():
    #     x = portugal_gdf[portugal_gdf['Distrito'] == distrito].unary_union.centroid.x
    #     y = portugal_gdf[portugal_gdf['Distrito'] == distrito].unary_union.centroid.y
    #     ax.annotate(distrito, xy=(x, y), xytext=(3, 3), textcoords='offset points', fontsize=8, color='black', zorder=3, path_effects=[withStroke(linewidth=4, foreground='w')])

    # Set title and remove axis labels
    plt.title('Visitantes Residentes em Portugal')
    plt.gca().patch.set_alpha(0)
    plt.axis('off')
    st.pyplot(fig)

with a3:
    # add discriptive
    #st.write('Residentes em Viseu Dão Lafões')
    # Plot the geometry of Viseu with LogNorm color scale
    fig, ax = plt.subplots(figsize=(10, 6))
    vdl_gdf.plot(ax=ax, color='lightgray')
    vdl_gdf[vdl_gdf['geo_area_nome'] == select1].plot(column='dormidas_totais', cmap='viridis', legend=True, ax=ax, norm=LogNorm(vmin=1, vmax=20000))
    #Add the names of distritos to portugal
    # for distrito in vdl_gdf['Distrito'].unique():
    #     x = vdl_gdf[vdl_gdf['Distrito'] == distrito].unary_union.centroid.x
    #     y = vdl_gdf[vdl_gdf['Distrito'] == distrito].unary_union.centroid.y
    #     ax.annotate(distrito, xy=(x, y), xytext=(3, 3), textcoords='offset points', fontsize=8, color='black', zorder=3, path_effects=[withStroke(linewidth=4, foreground='w')])

    # Set title and remove axis labels
    plt.title('Visitantes Residentes em Viseu Dão Lafões')
    plt.gca().patch.set_alpha(0)
    plt.axis('off')
    st.pyplot(fig)