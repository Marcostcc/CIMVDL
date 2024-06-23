import streamlit as st
import numpy as np
import pandas as pd
import duckdb as duck
import geopandas as gpd
import plotly.express as px
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from matplotlib.patheffects import withStroke
import altair as alt
#import altair as alt
#import geopandas as gpd

# Deixa o dash expandir até a largura da pagina
st.set_page_config(layout='wide', initial_sidebar_state='expanded')

alt.themes.enable("dark")

# Connect to the database
with duck.connect('CIM_VDL.duckdb') as cursor:
    cursor.execute(open('views.sql').read())

####################################################################### CSS STYLE  ###########################################################################################

# CSS styling
st.markdown("""
<style>

[data-testid="block-container"] {
    padding-left: 2rem;
    padding-right: 2rem;
    padding-top: 1rem;
    padding-bottom: 0rem;
    margin-bottom: -7rem;
}

[data-testid="stVerticalBlock"] {
    padding-left: 0rem;
    padding-right: 0rem;
}

[data-testid="stMetric"] {
    background-color: #393939;
    text-align: center;
    padding: 15px 0;
}

[data-testid="stMetricLabel"] {
  display: flex;
  justify-content: center;
  align-items: center;
}

[data-testid="stMetricDeltaIcon-Up"] {
    position: relative;
    left: 38%;
    -webkit-transform: translateX(-50%);
    -ms-transform: translateX(-50%);
    transform: translateX(-50%);
}

[data-testid="stMetricDeltaIcon-Down"] {
    position: relative;
    left: 38%;
    -webkit-transform: translateX(-50%);
    -ms-transform: translateX(-50%);
    transform: translateX(-50%);
}

</style>
""", unsafe_allow_html=True)


#######################################################################  LISTAS/ DICTS  ########################################################################################

# Criar lista com os concelhos
concelhos = ['Viseu Dão Lafões','Aguiar da Beira', 'Carregal do Sal', 'Castro Daire', 'Mangualde',
       'Nelas', 'Oliveira de Frades', 'Penalva do Castelo',
       'Santa Comba Dão', 'São Pedro do Sul', 'Sátão', 'Tondela',
       'Vila Nova de Paiva', 'Viseu', 'Vouzela']

meses = ['Jan-Dez','Janeiro','Fevereiro','Março','Abril','Maio','Junho','Julho','Agosto','Setembro','Outubro','Novembro','Dezembro']

anos = ['2022 e 2023','2022','2023']

pages = ['Pagina Principal','Painel de Estadias', 'Painel de tempo de permanencia', 'Painel de Deslocamento', 'Comparador de Concelhos', 'Personas']

#################################################################  HEADER STUFF  ###############################################################################################


# Importando o style.css 
with open('C:/Users/marco/Documents/MEGA/TESE/Streamlit/style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Criar o header no sidebar, o `´ no version 2 highlites o texto
st.sidebar.header('SMART CIM `Dashboard`')

# cria o select box no sidebar para filtrar 
st.sidebar.subheader('Turistas de Viseu Dão Lafões')

select_page = st.sidebar.selectbox('Escolha o Painel de Análise', pages)

select_ano = st.sidebar.selectbox('Escolha o Ano a analisar', anos) 

select_mes = st.sidebar.selectbox('Escolha o mês a analisar', meses) 

select1 = st.sidebar.selectbox('Escolha o Local a analisar', concelhos)


#######################################################################  FUNÇÕES  ########################################################################################

# Função para ler um geopackage e retornar um geodataframe
def read_gpkg(gpkg_path, layer_name):
    return gpd.read_file(gpkg_path, layer=layer_name, driver='GPKG')


def make_heatmap(input_df, input_y, input_x, input_color, input_color_theme):
    heatmap = alt.Chart(input_df).mark_rect().encode(
            y=alt.Y(f'{input_y}:O', axis=alt.Axis(title="Year", titleFontSize=18, titlePadding=15, titleFontWeight=900, labelAngle=0)),
            x=alt.X(f'{input_x}:O', axis=alt.Axis(title="", titleFontSize=18, titlePadding=15, titleFontWeight=900)),
            color=alt.Color(f'max({input_color}):Q',
                            legend=None,
                            scale=alt.Scale(scheme=input_color_theme)),
            stroke=alt.value('black'),
            strokeWidth=alt.value(0.25),
        ).properties(width=900
        ).configure_axis(
        labelFontSize=12,
        titleFontSize=12
        ) 
    # height=300
    return heatmap

def make_choropleth(input_df, concelho, input_column, input_id):
    choropleth = px.choropleth(input_df, locations=input_id,
                            color_continuous_scale="Viridis",
                            color = input_column,
                            labels={'pais_origem':'Origem', 'total_individuos':'Nº de Turistas'},
                            )
    choropleth.update_layout(
        template='plotly_dark',
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        margin=dict(l=0, r=0, t=0, b=0),
        height=350
    )
    return choropleth

def make_donut(input_response, input_text, input_color):
    chart_color = ['#29b5e8', '#155F7A']
    if input_response == 0:
        # If input_response is 0%, create a DataFrame with one row containing the 0% value
        source = pd.DataFrame({
            "Topic": ['', input_text],
            "% value": [100, 0]
        })
    else:
        # Otherwise, create a DataFrame with the input response and its complement
        source = pd.DataFrame({
            "Topic": ['', input_text],
            "% value": [100-input_response, input_response]
        })

    source_bg = pd.DataFrame({
        "Topic": ['', input_text],
        "% value": [100, 0]
    })
    
    plot = alt.Chart(source).mark_arc(innerRadius=40, outerRadius=65, cornerRadius=20).encode(
        theta="% value",
        color=alt.Color("Topic:N",
                        scale=alt.Scale(
                            domain=[input_text, ''],
                            range=chart_color),
                        legend=None),
    ).properties(width=169, height=169)  # Increase width and height by 30%
    
    text = plot.mark_text(align='center', color="#29b5e8", font="Lato", fontSize=32, fontWeight=700, fontStyle="italic").encode(text=alt.value(f'{input_response} %'))
    plot_bg = alt.Chart(source_bg).mark_arc(innerRadius=40, outerRadius=65, cornerRadius=20).encode(
        theta="% value",
        color= alt.Color("Topic:N",
                        scale=alt.Scale(
                            domain=[input_text, ''],
                            range=chart_color),  # 31333F
                        legend=None),
    ).properties(width=169, height=169)  # Increase width and height by 30%
    return plot_bg + plot + text


def calculate_international_ratio(nacional_df , internacional_df, input_month):
    ratio = int((perm_inter.total_individuos.sum() / perm_nac.total_individuos.sum()) * 100)
    return ratio

# create a function to calculate the most visited country using most_visited_country = perm_inter[perm_inter['tipologia'] == "Turista"].groupby('pais_origem').agg({'total_individuos': 'sum'}).sort_values(by='total_individuos', ascending=False).head(1)
def most_visited_country(df, input_month):
    most_visited_country = df[df['tipologia'] == "Turista"].groupby('pais_origem').agg({'total_individuos': 'sum'}).sort_values(by='total_individuos', ascending=False).head(1)
    return most_visited_country

def most_visited_district(df, input_month):
    most_visited_district = df[df['tipologia'] == "Turista"].groupby('distrito_residencia').agg({'total_individuos': 'sum'}).sort_values(by='total_individuos', ascending=False).head(1)
    return most_visited_district

#######################################################################  PAINEL PRINCIPAL  ########################################################################################

if select_page == 'Pagina Principal':
    col = st.columns((1.5, 4.5, 2), gap='medium')

    with duck.connect('CIM_VDL.duckdb') as cursor:
        perm_inter = pd.DataFrame(data=cursor.execute("select * from permanencia_internacional_concelho").fetchall(), columns = ['datekey', 'pais_origem', 'distrito_residencia', 'concelho_residencia_codigo' ,'concelho_residencia', 'geo_area_codigo', 'geo_area_nome','tipologia','individuos','val_0_1_h','val_1_2_h','val_2_4_h','val_4_8_h','val_8_mais_h', 'residente_VDL', 'total_individuos','media_horas','dia_semana','feriado'])

    with duck.connect('CIM_VDL.duckdb') as cursor:
            perm_nac = pd.DataFrame(data=cursor.execute("select * from permanencia_nacional_concelho").fetchall(), columns = ['datekey','pais_origem', 'distrito_residencia', 'concelho_residencia_codigo' ,'concelho_residencia', 'geo_area_codigo', 'geo_area_nome','tipologia','individuos','val_0_1_h','val_1_2_h','val_2_4_h','val_4_8_h','val_8_mais_h', 'residente_VDL', 'total_individuos','media_horas','dia_semana','feriado'])


    with col[0]:
        st.markdown('### Métricas Gerais')
        #col1 Query para obter o pais que mais visita
        with duck.connect('CIM_VDL.duckdb') as cursor:
            permanencia_int_por_concelho = pd.DataFrame(data=cursor.execute("select * from pais_mais_visitou").fetchall(), columns=["pais_origem", "total_individuos"]).sort_values(by='total_individuos', ascending=False)
        
        # col1anwser the sum of the pais_origem.unique()
        col1_answer = permanencia_int_por_concelho['pais_origem'].nunique()
        # col1_compare the sum of the "dormidas_totais" column from the same month last year
        col1_compare = col1_answer - 42
        st.metric("Turistas" + " de ",
                    str(col1_answer) + ' Países')
        
        # use most_visited_country function and make a metric
        #st.markdown('##### País mais visitou')
        most_visited = most_visited_country(perm_inter, select_mes)
        st.metric(label='Turistas de', value=most_visited.index[0], delta=int(most_visited.total_individuos[0]))

        st.markdown('##### Racio de Internacionais')

        inter_nac_ratio = calculate_international_ratio(perm_nac, perm_inter, select_mes)
        # select_mes = "Dezembro" or "Jan-Dez"
        if select_mes == "Dezembro" or select_mes == "Jan-Dez":
            inter_nac_ratio = calculate_international_ratio(perm_nac, perm_inter, select_mes)
            # Display the donut chart
            donut_chart = make_donut(inter_nac_ratio, " ", inter_nac_ratio)
            st.altair_chart(donut_chart)
        else:
            st.metric(label=" ", value="0%", delta="")
        
    with col[1]:
        vdl_con = read_gpkg('C:/Users/marco/Documents/MEGA/CIMVDL/CIM-VDL/geopackages/vdl_con.gpkg', 'vdl_con')
        # groupby "Concelho", "geometry" and sum "total_individuos" for perm_inter_gdf
        perm_inter_grouped = perm_inter.groupby(['geo_area_nome']).agg({'total_individuos': 'sum'}).reset_index()

        #groupby "Concelho", "geometry" and sum "total_individuos" for perm_nac_gdf
        perm_nac_grouped = perm_nac.groupby(['geo_area_nome']).agg({'total_individuos': 'sum'}).reset_index()
        # merge vdl_con with perm_inter
        perm_inter_gdf = vdl_con.merge(perm_inter_grouped, left_on='Concelho', right_on='geo_area_nome', how='left')
        # merge vdl_con with perm_nac
        perm_nac_gdf = vdl_con.merge(perm_nac_grouped, left_on='Concelho', right_on='geo_area_nome', how='left')

        # create a choropleth for perm_inter_gdf
        fig3, ax = plt.subplots()

        # Set the background color to black
        fig3.patch.set_facecolor('#0E1117')
        vmin = perm_inter_gdf['total_individuos'].min()
        vmax = perm_inter_gdf['total_individuos'].max()

        # Plot the geometry of Viseu with a LogNorm color scale
        perm_inter_gdf.plot(column='total_individuos', cmap='viridis', legend=True, ax=ax, legend_kwds={'shrink': 0.3}, norm=LogNorm(vmin=vmin, vmax=vmax))

        # Add the names of distritos to portugal
        for distrito in perm_inter_gdf['Concelho'].unique():
            x = perm_inter_gdf[perm_inter_gdf['Concelho'] == distrito].unary_union.centroid.x
            y = perm_inter_gdf[perm_inter_gdf['Concelho'] == distrito].unary_union.centroid.y
            ax.annotate(distrito, xy=(x, y), xytext=(3, 3), textcoords='offset points', fontsize=8, color='black', zorder=3, path_effects=[withStroke(linewidth=4, foreground='w')])

        # Set title and remove axis labels
        plt.title('Mapa de calor dos Turistas Internaciais', color='white')
        ax.patch.set_alpha(0)
        ax.axis('off')

        # Show the plot
        st.pyplot(fig3)


    with col[2]:
        st.markdown('#### Turistas Internacionais')
        # order the perm_inter_grouped by "total_individuos"
        st.dataframe(perm_inter_grouped.sort_values(by='total_individuos', ascending=False),
                    column_order=("geo_area_nome", "total_individuos"),
                    hide_index=True,
                    width=None,
                    column_config={
                        "geo_area_nome": st.column_config.TextColumn(
                            "Concelhos",
                        ),
                        "total_individuos": st.column_config.ProgressColumn(
                            "Turistas",
                            format="%f",
                            min_value=0,
                            max_value=max(perm_inter_grouped.total_individuos),
                        )}
                    )

#-------------------------------- Second row --------------------------------#
        
    col = st.columns((1.5, 4.5, 2), gap='medium')

    with col[0]:
        with duck.connect('CIM_VDL.duckdb') as cursor:
            distrito_mais_visitado = pd.DataFrame(data=cursor.execute("select * from distrito_mais_visitou").fetchall(), columns=["distrito_residencia", "total_individuos"]).sort_values(by='total_individuos', ascending=False)

        # col1anwser the sum of the pais_origem.unique()
        col1_answer = distrito_mais_visitado['distrito_residencia'].nunique()
        # col1_compare the sum of the "dormidas_totais" column from the same month last year
        col1_compare = col1_answer - 42
        st.metric("Turistas" + " de ",
                    str(col1_answer) + ' Distritos')
        
        # use most_visited_country function and make a metric
        #st.markdown('##### País mais visitou')
        most_visited = most_visited_district(perm_nac, select_mes)
        st.metric(label='Turistas de', value=most_visited.index[0], delta=int(most_visited.total_individuos[0]))

    with col[1]:
        # create a choropleth for perm_inter_gdf
        fig1, ax1 = plt.subplots()

        # Set the background color to black
        fig1.patch.set_facecolor('#0E1117')
        vmin = perm_nac_gdf['total_individuos'].min()
        vmax = perm_nac_gdf['total_individuos'].max()

        # Plot the geometry of Viseu with a LogNorm color scale
        perm_nac_gdf.plot(column='total_individuos', cmap='viridis', legend=True, ax=ax1, legend_kwds={'shrink': 0.3}, norm=LogNorm(vmin=vmin, vmax=vmax))

        # Add the names of distritos to portugal
        for distrito in perm_nac_gdf['Concelho'].unique():
            x = perm_nac_gdf[perm_nac_gdf['Concelho'] == distrito].unary_union.centroid.x
            y = perm_nac_gdf[perm_nac_gdf['Concelho'] == distrito].unary_union.centroid.y
            ax1.annotate(distrito, xy=(x, y), xytext=(3, 3), textcoords='offset points', fontsize=8, color='white', zorder=3, path_effects=[withStroke(linewidth=4, foreground='black')])

        # Set title and remove axis labels
        plt.title('Mapa de calor dos Turistas Nacionais', color='white')
        ax1.patch.set_alpha(0)
        ax1.axis('off')

        # Show the plot
        st.pyplot(fig1)

    with col[2]:
        st.markdown('#### Turistas Nacionais')
        # order the perm_inter_grouped by "total_individuos"
        st.dataframe(perm_nac_grouped.sort_values(by='total_individuos', ascending=False),
                    column_order=("geo_area_nome", "total_individuos"),
                    hide_index=True,
                    width=None,
                    column_config={
                        "geo_area_nome": st.column_config.TextColumn(
                            "Concelhos",
                        ),
                        "total_individuos": st.column_config.ProgressColumn(
                            "Turistas",
                            format="%f",
                            min_value=0,
                            max_value=max(perm_nac_grouped.total_individuos),
                        )}
                    )







#######################################################################  PAINEL DE ESTADIAS  ########################################################################################

if select_page == 'Painel de Estadias':
    st.title(select_page)
    st.write( '### ' + select1 + ' | ' + select_mes + ',  ' + select_ano)

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
        total_dormidas_int_pais = pd.DataFrame(data=cursor.execute("select * from estadias_int_por_pais").fetchall(), columns=["pais_origem", "dormidas_totais"]).sort_values(by='dormidas_totais', ascending=False)

    # A2. Query para obter os dados dos paises por concelho
    with duck.connect('CIM_VDL.duckdb') as cursor:
        total_dormidas_int_concelho = pd.DataFrame(data=cursor.execute("select * from estadias_int_per_concelho").fetchall(), columns=["pais_origem", "geo_area_nome", "dormidas_totais"]).sort_values(by='dormidas_totais', ascending=False)
    #-----------------------------------------------------------------------------#

    # B1. Query para obter os dados NACIONAIS
    with duck.connect('CIM_VDL.duckdb') as cursor:
        quem_dormiu_nac_concelho = pd.DataFrame(data=cursor.execute("select * from quem_dormiu_nac_concelho").fetchall(), columns=["pais_origem", "geo_area_nome", "concelho_residencia","distrito_residencia","dormidas_totais"])

    # B1. geodataframe de PORTUGAL
    portugal_con = read_gpkg('C:/Users/marco/Documents/MEGA/CIMVDL/CIM-VDL/geopackages/simplified_portugal.gpkg', 'simplified')

    # B1. merge dos dados com o geodataframe
    portugal_gdf = portugal_con.merge(quem_dormiu_nac_concelho, left_on='Concelho', right_on='concelho_residencia', how='left')

    # B2. Query para obter os dados dos distritos que mais visitam
    with duck.connect('CIM_VDL.duckdb') as cursor:
        total_dormidas_nac_distrito = pd.DataFrame(data=cursor.execute("select * from estadias_nac_por_distrito").fetchall(), columns=["distrito_residencia", "dormidas_totais"]).sort_values(by='dormidas_totais', ascending=False)

    # B2. Query para obter os dados dos distritos por concelho
    with duck.connect('CIM_VDL.duckdb') as cursor:
        total_dormidas_nac_concelho = pd.DataFrame(data=cursor.execute("select * from estadias_nac_per_concelho").fetchall(), columns=["geo_area_nome", "distrito_residencia", "dormidas_totais"]).sort_values(by='dormidas_totais', ascending=False)

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
        st.write('Mapa de calor das Origens dos Turistas ' + 'em ' + select1)
        fig1, ax1 = plt.subplots(figsize=(10, 6))
        fig1.patch.set_facecolor('#0E1117')

        # Plot the geometry of the world with gray color
        world_gdf.plot(ax=ax1, color='lightgray')

        # Plot the geometry of the world with LogNorm color scale
        world_gdf[world_gdf['geo_area_nome'] == select1].plot(column='dormidas_totais', cmap='viridis', legend=True, ax=ax1, norm=LogNorm(vmin=1, vmax=20000),legend_kwds={'shrink': 0.3})

        # Set title and remove axis labels
        #plt.title('Mapa de calor dos Turistas Internacionais')
        ax1.patch.set_alpha(0)
        ax1.axis('off')

        # Change the color of tick labels to white
        ax1.tick_params(axis='both', colors='white')

        st.pyplot(fig1)

        # Create a DataFrame with all countries and set the color to gray initially
        # world_gdf['color'] = 'gray'

        # # Update the color for countries that visited "Sátão"
        # world_gdf.loc[world_gdf[world_gdf['geo_area_nome'] == select1].index, 'color'] = world_gdf[world_gdf['geo_area_nome'] == select1]['dormidas_totais']

        # # Plot the choropleth map
        # fig = px.choropleth(world_gdf, geojson=world_gdf.geometry, locations=world_gdf.index, 
        #                     color="color",
        #                     color_continuous_scale='Viridis',
        #                     hover_data=["NAME_PT"])

        # fig.update_geos(fitbounds="locations", visible=False)

        # fig.show()

    # with a2 plot the map for portugal with the selected concelho
    with a2:
        bar_width = 0.3
        st.write('Comparação de Estadias em Viseu Dão Lafões e em' + ' ' + select1) 
        # Get the top 10 countries from total_dormidas_int_pais
        top_10_countries = total_dormidas_int_pais.head(10)['pais_origem']

        r1 = np.arange(len(total_dormidas_int_pais.head(10)))

        # Create an array of indices for the bars representing dormidas for Viseu
        r2 = [x + bar_width for x in r1]

        # Filter total_dormidas_int_concelho for the specific concelho Viseu and top 10 countries
        filtered_dormidas_concelho = total_dormidas_int_concelho[(total_dormidas_int_concelho['geo_area_nome'] == select1) & (total_dormidas_int_concelho['pais_origem'].isin(top_10_countries))]

        # Create figure and axis objects
        figA2, ax = plt.subplots(figsize=(10, 6))
        #figA2.patch.set_facecolor('#0E1117')

        # Plot the bars
        bars1 = ax.bar(r1, total_dormidas_int_pais.dormidas_totais.head(10), color='skyblue', width=bar_width, edgecolor='grey', label='Total de Estadias em VDL')
        bars2 = ax.bar(r2, filtered_dormidas_concelho['dormidas_totais'], color='lightgreen', width=bar_width, edgecolor='grey', label='Estadias em' + ' ' + select1)

        # Add labels, title, and legend
        ax.set_xlabel('País de Origem', fontweight='bold')
        ax.set_ylabel('Quantidade de Estadias', fontweight='bold')
        ax.set_title('Comparação de Estadias em Viseu Dão Lafões e em'  + ' ' + select1, fontweight='bold')
        ax.set_xticks([r + bar_width/2 for r in range(len(total_dormidas_int_pais.pais_origem.head(10)))])
        ax.set_xticklabels(total_dormidas_int_pais.pais_origem.head(10))
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
        #st.write('Quantidade de dormidas registadas por Turistas Nacionais em' + ' ' + select1)
        # Plot the geometry of Portugal with gray color
        fig2, ax = plt.subplots(figsize=(10, 6))
        fig2.patch.set_facecolor('#0E1117')
        #fig2.patch.set_facecolor('#0E1117')
        portugal_gdf.plot(ax=ax, color='lightgray')

        # Plot the geometry of Viseu with LogNorm color scale
        portugal_gdf[portugal_gdf['geo_area_nome'] == select1].plot(column='dormidas_totais', cmap='viridis', legend=True, ax=ax, norm=LogNorm(vmin=1, vmax=20000),legend_kwds={'shrink': 0.3})
        #Add the names of distritos to portugal
        # for distrito in portugal_gdf['Distrito'].unique():
        #     x = portugal_gdf[portugal_gdf['Distrito'] == distrito].unary_union.centroid.x
        #     y = portugal_gdf[portugal_gdf['Distrito'] == distrito].unary_union.centroid.y
        #     ax.annotate(distrito, xy=(x, y), xytext=(3, 3), textcoords='offset points', fontsize=8, color='black', zorder=3, path_effects=[withStroke(linewidth=4, foreground='w')])

        # Set title and remove axis labels
        #plt.title('Mapa de calor dos Turistas Nacionais')
        ax.patch.set_alpha(0)
        ax.axis('off')
        st.pyplot(fig2)

    with b2:
        #st.write('Turistas Nacionais registados em' + ' ' + select1 + ' ' + 'vs Total em Viseu Dão Lafões')
        bar_height = 0.3

        # Get the top 10 districts from total_dormidas_nac_distrito
        top_10_distritos = total_dormidas_nac_distrito.head(14)['distrito_residencia']

        r1 = np.arange(len(total_dormidas_nac_distrito.head(14)))

        # Create an array of indices for the bars representing dormidas for Viseu
        r2 = [y + bar_height for y in r1]

        # Filter total_dormidas_int_concelho for the specific concelho Viseu and top 10 districts
        filtered_dormidas_concelho = total_dormidas_nac_concelho[(total_dormidas_nac_concelho['geo_area_nome'] == select1) & (total_dormidas_nac_concelho['distrito_residencia'].isin(top_10_distritos))]

        # Create figure and axis objects
        figB2, ax = plt.subplots(figsize=(10, 15))
        # figB2.patch.set_facecolor('#0E1117')

        # Plot the bars horizontally
        bars1 = ax.barh(r1, total_dormidas_nac_distrito.dormidas_totais.head(14), color='skyblue', height=bar_height, edgecolor='grey', label='Total de Estadias em VDL')
        bars2 = ax.barh(r2, filtered_dormidas_concelho['dormidas_totais'], color='lightgreen', height=bar_height, edgecolor='grey', label='Estadias em' + ' ' + select1)

        # Add labels, title, and legend
        ax.set_ylabel('País de Origem', fontweight='bold')
        ax.set_xlabel('Quantidade de Estadias', fontweight='bold')
        ax.set_title('Comparação de Estadias totais de Viseu Dão Lafões com apenas'  + ' ' + select1, fontweight='bold')
        ax.set_yticks([r + bar_height/2 for r in range(len(total_dormidas_nac_distrito.distrito_residencia.head(14)))])
        ax.set_yticklabels(total_dormidas_nac_distrito.distrito_residencia.head(14))
        ax.legend()

        # Add value labels on the right side of the bars
        for bars in [bars1, bars2]:
            for bar in bars:
                width = bar.get_width()
                ax.annotate('{}'.format(width),
                            xy=(width, bar.get_y() + bar.get_height() / 2),
                            xytext=(3, 0),  # 3 points horizontal offset
                            textcoords="offset points",
                            ha='left', va='center')


        # Show plot
        # Remove the border color of the figure
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
        st.pyplot(figB2)

    c1, c2 = st.columns((5.5,4.5))

    with c1:
        # add discriptive
        #st.write('Quantidade de dormidas registadas por Turistas de Viseu Dão Lafões em' + ' ' + select1)
        # Plot the geometry of Viseu with LogNorm color scale
        fig3, ax = plt.subplots(figsize=(10, 6))
        fig3.patch.set_facecolor('#0E1117')
        #fig3.patch.set_facecolor('#0E1117')
        vdl_gdf.plot(ax=ax, color='lightgray')
        vdl_gdf[vdl_gdf['geo_area_nome'] == select1].plot(column='dormidas_totais', cmap='viridis', legend=True, ax=ax, norm=LogNorm(vmin=1, vmax=20000),legend_kwds={'shrink': 0.3})
        #Add the names of distritos to portugal
        # for distrito in vdl_gdf['Distrito'].unique():
        #     x = vdl_gdf[vdl_gdf['Distrito'] == distrito].unary_union.centroid.x
        #     y = vdl_gdf[vdl_gdf['Distrito'] == distrito].unary_union.centroid.y
        #     ax.annotate(distrito, xy=(x, y), xytext=(3, 3), textcoords='offset points', fontsize=8, color='black', zorder=3, path_effects=[withStroke(linewidth=4, foreground='w')])

        # Set title and remove axis labels
        #plt.title('Mapa de calor dos Turistas de Viseu Dão Lafões')
        ax.patch.set_alpha(0)
        ax.axis('off')
        st.pyplot(fig3)
