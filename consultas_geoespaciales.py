# -*- coding: utf-8 -*-
"""
Created on Mon Jun 30 16:19:23 2025

@author: dherves
"""

import streamlit as st
import geopandas as gpd
import pydeck as pdk
import pandas as pd
from shapely.geometry import mapping
import base64



# -------- FUNCIÓN PARA LISTAR CAPAS EN UNA GDB --------


# -------- FUNCIÓN PARA CONVERTIR GEOMETRÍA A pydeck --------
def geometria_to_pydeck(gdf):
    data = []
    for _, row in gdf.iterrows():
        geom = row.geometry
        if geom is None:
            continue
        if geom.geom_type == "Polygon":
            coords = list(mapping(geom)["coordinates"])
            data.append({"coordinates": coords[0]})  # solo anillo exterior
        elif geom.geom_type == "MultiPolygon":
            for part in geom.geoms:
                coords = list(mapping(part)["coordinates"])
                data.append({"coordinates": coords[0]})  # solo anillo exterior
    return pd.DataFrame(data)

st.set_page_config(page_title="Consultas geoespacialessss")
left_column, right_column=st.columns(2)
left_column.image("logo_AQ.png")
right_column.image("logo-augas-de-galicia.png")

# -------- CONFIGURACIÓN DE LA PÁGINA --------


st.title("Consultas Geoespaciales")
st.sidebar.success("Seleciona tipo de consulta.")

# -------- ENTRADA: RUTA A LA GDB --------

#ruta_gdb = st.text_input("Introduce la ruta local a la carpeta .gdb")
#st.session_state.rutaGDB=ruta_gdb
ruta_gdb="./data/PHGC28_33_GDB_Ed00.gdb"
#@st.cache_data
def carga_datos(ruta):
   
    capas = list(gpd.list_layers(ruta)["name"])

    if capas:
        capa_sel = st.selectbox("Selecciona una capa", capas)
        try:
            gdf = gpd.read_file(ruta_gdb, layer=capa_sel)
        except Exception as e:
            st.error(f"Error al cargar la capa: {e}")
        else:
            if gdf.empty:
                st.warning("La capa está vacía.")
            else:
                st.success(f"{len(gdf)} elementos cargados")

                # Asegurarse de que está en WGS84
                if gdf.crs and gdf.crs.to_epsg() != 4326:
                    gdf = gdf.to_crs(epsg=4326)

                gdf = gdf[gdf.geometry.notnull()]
                df_coords = geometria_to_pydeck(gdf)

                # Crear capa pydeck
                polygon_layer = pdk.Layer(
                    "PolygonLayer",
                    data=df_coords,
                    get_polygon="coordinates",
                    get_fill_color=[0, 100, 255, 100],
                    get_line_color=[0, 0, 0],
                    line_width_min_pixels=1,
                    pickable=True,
                )

                # Vista inicial centrada en los datos
                view_state = pdk.ViewState(
                    latitude=gdf.geometry.centroid.y.mean(),
                    longitude=gdf.geometry.centroid.x.mean(),
                    zoom=8
                )

                # Crear y mostrar el mapa
                deck = pdk.Deck(
                    layers=[polygon_layer],
                    initial_view_state=view_state,
                    map_style="mapbox://styles/mapbox/light-v9"
                )

                st.pydeck_chart(deck)
    else:
        st.error("No se encontraron capas en la GDB.")





carga_datos(ruta_gdb)

















