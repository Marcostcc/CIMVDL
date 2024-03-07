import streamlit as st
import numpy as np
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

# A1. remove row where NAME == Antarctica from world
world = world[world['NAME'] != 'Antarctica']

# A1. merge dos dados com o geodataframe
world_gdf = world.merge(quem_dormiu_int_concelho, left_on='NAME_PT', right_on='pais_origem', how='left')

# A2. Query para obter os dados dos paises que mais visitam
with duck.connect('CIM_VDL.duckdb') as cursor:
    total_dormidas_by_pais = pd.DataFrame(data=cursor.execute("select * from estadias_int_por_pais").fetchall(), columns=["pais_origem", "dormidas_totais"]).sort_values(by='dormidas_totais', ascending=False)

# A2. Query para obter os dados dos paises por concelho
with duck.connect('CIM_VDL.duckdb') as cursor:
    total_dormidas_by_concelho = pd.DataFrame(data=cursor.execute("select * from estadias_int_per_concelho").fetchall(), columns=["pais_origem", "geo_area_nome", "dormidas_totais"]).sort_values(by='dormidas_totais', ascending=False)
#-----------------------------------------------------------------------------#

# B1. Query para obter os dados NACIONAIS
with duck.connect('CIM_VDL.duckdb') as cursor:
    quem_dormiu_nac_concelho = pd.DataFrame(data=cursor.execute("select * from quem_dormiu_nac_concelho").fetchall(), columns=["pais_origem", "geo_area_nome", "concelho_residencia","distrito_residencia","dormidas_totais"])

# B1. geodataframe de PORTUGAL
portugal_con = read_gpkg('C:/Users/marco/Documents/MEGA/CIMVDL/CIM-VDL/geopackages/simplified_portugal.gpkg', 'simplified')

# B1. merge dos dados com o geodataframe
portugal_gdf = portugal_con.merge(quem_dormiu_nac_concelho, left_on='Concelho', right_on='concelho_residencia', how='left')

#-----------------------------------------------------------------------------#

# C1. Query para obter os dados VISEU DÃO LAFÕES
with duck.connect('CIM_VDL.duckdb') as cursor:
    quem_dormiu_reg_concelho = pd.DataFrame(data=cursor.execute("select * from quem_dormiu_reg_concelho").fetchall(), columns=["pais_origem", "geo_area_nome", "concelho_residencia","dormidas_totais"])

# C1. geodataframe de VDL
vdl_con = read_gpkg('C:/Users/marco/Documents/MEGA/CIMVDL/CIM-VDL/geopackages/vdl_con.gpkg', 'vdl_con')

# C1. merge dos dados com o geodataframe
vdl_gdf = vdl_con.merge(quem_dormiu_reg_concelho, left_on='Concelho', right_on='concelho_residencia', how='left')


# criar cloropleth map com os dados
a1, a2 = st.columns((5.5,4.5))

# with a1 plot the map for the world with the selected concelho
with a1:
    # add discriptive
    st.write('Quantidade de dormidas registadas por Turistas Internacionais em' + ' ' + select1)
    # Plot the geometry of the world with gray color
    fig1, ax = plt.subplots(figsize=(10, 6))
    world_gdf.plot(ax=ax, color='lightgray')

    # Plot the geometry of the world with LogNorm color scale
    world_gdf[world_gdf['geo_area_nome'] == select1].plot(column='dormidas_totais', cmap='viridis', legend=True, ax=ax, norm=LogNorm(vmin=1, vmax=20000),legend_kwds={'shrink': 0.3})
    #Add the names of distritos to portugal
    # for distrito in world_gdf['Distrito'].unique():
    #     x = world_gdf[world_gdf['Distrito'] == distrito].unary_union.centroid.x
    #     y = world_gdf[world_gdf['Distrito'] == distrito].unary_union.centroid.y
    #     ax.annotate(distrito, xy=(x, y), xytext=(3, 3), textcoords='offset points', fontsize=8, color='black', zorder=3, path_effects=[withStroke(linewidth=4, foreground='w')])

    # Set title and remove axis labels
    plt.title('Mapa de calor dos Turistas Internacionais')
    ax.patch.set_alpha(0)
    ax.axis('off')
    st.pyplot(fig1)

# with a2 plot the map for portugal with the selected concelho
with a2:
    bar_width = 0.3
    st.write('Turistas Internacionais registados em' + ' ' + select1 + ' ' + 'vs Total em Viseu Dão Lafões')
    # Get the top 10 countries from total_dormidas_by_pais
    top_10_countries = total_dormidas_by_pais.head(10)['pais_origem']

    r1 = np.arange(len(total_dormidas_by_pais.head(10)))

    # Create an array of indices for the bars representing dormidas for Viseu
    r2 = [x + bar_width for x in r1]

    # Filter total_dormidas_by_concelho for the specific concelho Viseu and top 10 countries
    filtered_dormidas_concelho = total_dormidas_by_concelho[(total_dormidas_by_concelho['geo_area_nome'] == select1) & (total_dormidas_by_concelho['pais_origem'].isin(top_10_countries))]

    # Create figure and axis objects
    figA2, ax = plt.subplots(figsize=(10, 6))

    # Plot the bars
    bars1 = ax.bar(r1, total_dormidas_by_pais.dormidas_totais.head(10), color='skyblue', width=bar_width, edgecolor='grey', label='Total de Estadias em VDL')
    bars2 = ax.bar(r2, filtered_dormidas_concelho['dormidas_totais'], color='lightgreen', width=bar_width, edgecolor='grey', label='Estadias em' + ' ' + select1)

    # Add labels, title, and legend
    ax.set_xlabel('País de Origem', fontweight='bold')
    ax.set_ylabel('Quantidade de Estadias', fontweight='bold')
    ax.set_title('Comparação de Estadias em Viseu Dão Lafões e em'  + ' ' + select1, fontweight='bold')
    ax.set_xticks([r + bar_width/2 for r in range(len(total_dormidas_by_pais.pais_origem.head(10)))])
    ax.set_xticklabels(total_dormidas_by_pais.pais_origem.head(10))
    ax.legend()

    # Add value labels on top of the bars
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.annotate('{}'.format(height),
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom')

    # Show plot
    # Remove the border color of the figure
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
    st.pyplot(figA2)

b1, b2 = st.columns((5.5,4.5))

with b1:
    # add discriptive
    st.write('Quantidade de dormidas registadas por Turistas Nacionais em' + ' ' + select1)
    # Plot the geometry of Portugal with gray color
    fig2, ax = plt.subplots(figsize=(10, 6))
    portugal_gdf.plot(ax=ax, color='lightgray')

    # Plot the geometry of Viseu with LogNorm color scale
    portugal_gdf[portugal_gdf['geo_area_nome'] == select1].plot(column='dormidas_totais', cmap='viridis', legend=True, ax=ax, norm=LogNorm(vmin=1, vmax=20000),legend_kwds={'shrink': 0.3})
    #Add the names of distritos to portugal
    # for distrito in portugal_gdf['Distrito'].unique():
    #     x = portugal_gdf[portugal_gdf['Distrito'] == distrito].unary_union.centroid.x
    #     y = portugal_gdf[portugal_gdf['Distrito'] == distrito].unary_union.centroid.y
    #     ax.annotate(distrito, xy=(x, y), xytext=(3, 3), textcoords='offset points', fontsize=8, color='black', zorder=3, path_effects=[withStroke(linewidth=4, foreground='w')])

    # Set title and remove axis labels
    plt.title('Mapa de calor dos Turistas Nacionais')
    ax.patch.set_alpha(0)
    ax.axis('off')
    st.pyplot(fig2)

c1, c2 = st.columns((5.5,4.5))

with c1:
    # add discriptive
    st.write('Quantidade de dormidas registadas por Turistas de Viseu Dão Lafões em' + ' ' + select1)
    # Plot the geometry of Viseu with LogNorm color scale
    fig3, ax = plt.subplots(figsize=(10, 6))
    vdl_gdf.plot(ax=ax, color='lightgray')
    vdl_gdf[vdl_gdf['geo_area_nome'] == select1].plot(column='dormidas_totais', cmap='viridis', legend=True, ax=ax, norm=LogNorm(vmin=1, vmax=20000),legend_kwds={'shrink': 0.3})
    #Add the names of distritos to portugal
    # for distrito in vdl_gdf['Distrito'].unique():
    #     x = vdl_gdf[vdl_gdf['Distrito'] == distrito].unary_union.centroid.x
    #     y = vdl_gdf[vdl_gdf['Distrito'] == distrito].unary_union.centroid.y
    #     ax.annotate(distrito, xy=(x, y), xytext=(3, 3), textcoords='offset points', fontsize=8, color='black', zorder=3, path_effects=[withStroke(linewidth=4, foreground='w')])

    # Set title and remove axis labels
    plt.title('Mapa de calor dos Turistas de Viseu Dão Lafões')
    ax.patch.set_alpha(0)
    ax.axis('off')
    st.pyplot(fig3)