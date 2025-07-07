# -*- coding: utf-8 -*-
"""
Created on Mon Jun 30 17:42:18 2025

@author: dherves
"""

import streamlit as st
import geopandas as gpd
import pydeck as pdk
import pandas as pd
from shapely.geometry import mapping
import matplotlib.pyplot as plt
#import contextily as ctx


from mis_funciones import carga_datos
from mis_funciones import geometria_to_pydeck
from mis_funciones import mapa_pydeck
from mis_funciones import cambiar_crs
from mis_funciones import read_gdf_capa
from mis_funciones import interseccion_capas




st.title("Consulta Zona Protegida -> Masa de agua")
st.markdown("Consulta Zona Protegida -> Masa de agua")
st.sidebar.header("Consulta Zona Protegida -> Masa de agua")
#listamos todas las capas que tiene el gdb 

lista_de_capas=list(gpd.list_layers(st.session_state.rutaGDB)["name"])

#st.write(lista_de_capas)

# Filtrar las zonas protegidas que empiecen por 'NE' (nivel europeo)
zonasNE = [c for c in lista_de_capas if c.startswith("NE")]
zonasNI = [c for c in lista_de_capas if c.startswith("NI")]
zonasPH = [c for c in lista_de_capas if c.startswith("PH")]

zonas_protegidas = zonasNE + zonasNI + zonasPH #+ zonasAUX
#quitamos capas de zonas protegidas sin el campo EUZPROTCOD
zonas_protegidas.remove("NE_ZonaCaptacionZonaSensible")
zonas_protegidas.remove("NE_ZonasSensible")
zonas_protegidas.remove("NI_ReservaMarinaInt")


# Filtrar las zonas  'MasasAuga'
#masas_agua = [c for c in lista_de_capas if c.startswith("MasasAgua")]
masas_agua = ["MasasAguaLagos","MasasAguaPuertos","CuencasTotales","MasasAguaTransicion","MasasAguaCosteras"]


#cargamos la primera capa masas de agua
gdf_masas=read_gdf_capa(st.session_state.rutaGDB,masas_agua[0]) #el primer elemento de la lista es el 0, el segundo el 1, etc

#cargamos todas las capas de masas de agua
for masa in masas_agua[1:]: #empieza en 1 (se salta el primer elemento)
    gdfnew = read_gdf_capa(st.session_state.rutaGDB,masa)
    gdf_masas = pd.concat([gdf_masas,gdfnew],ignore_index=True,join="inner",axis=0)

capa = st.selectbox('Selecciona capa de zona protegida', zonas_protegidas )
#cargamos la zona protegida de interés
if capa:
    gdf_zona=read_gdf_capa(st.session_state.rutaGDB,capa)
    EUZPROTCOD=st.selectbox("selecciona código de zona protegida",gdf_zona.EUZPROTCOD.unique())
    if EUZPROTCOD:
        gdf_zona=gdf_zona[gdf_zona.EUZPROTCOD == EUZPROTCOD]
        
        gdf_masas_solapadas=interseccion_capas(gdf_zona, gdf_masas)
        if st.button("Ejecutar Consulta"):
            st.dataframe(gdf_masas_solapadas.drop(columns=["geometry","info"],inplace=False))
        
            polygon_layer_zona = geometria_to_pydeck(gdf_zona,color="red")
            polygon_layer_masa= geometria_to_pydeck(gdf_masas_solapadas,color="blue")
            mapa_pydeck([polygon_layer_masa,polygon_layer_zona])