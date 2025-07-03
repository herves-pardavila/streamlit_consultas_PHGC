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

from mis_funciones import carga_datos
from mis_funciones import geometria_to_pydeck
from mis_funciones import mapa_pydeck

# -------- FUNCIÓN PARA LISTAR CAPAS EN UNA GDB --------


# -------- FUNCIÓN PARA CONVERTIR GEOMETRÍA A pydeck --------


st.set_page_config(page_title="Consultas geoespacialessss")
left_column, right_column=st.columns(2)
left_column.image("logo_AQ.png")
right_column.image("logo-augas-de-galicia.png")

# -------- CONFIGURACIÓN DE LA PÁGINA --------


st.title("Consultas Geoespaciales")
st.sidebar.success("Seleciona tipo de consulta.")

# -------- ENTRADA: RUTA A LA GDB --------

#ruta_gdb = st.text_input("Introduce la ruta local a la carpeta .gdb")
ruta_gdb="./data/PHGC28_33_GDB_Ed00.gdb"

st.session_state.rutaGDB=ruta_gdb
#@st.cache_data



gdf=carga_datos(st.session_state.rutaGDB)
polygon_layer = geometria_to_pydeck(gdf)
mapa_pydeck([polygon_layer])
















