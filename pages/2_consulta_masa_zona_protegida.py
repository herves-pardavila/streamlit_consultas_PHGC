# -*- coding: utf-8 -*-
"""
Created on Tue Jul  1 11:29:19 2025

@author: dherves
"""


import streamlit as st
import geopandas as gpd
import pydeck as pdk
import pandas as pd
from shapely.geometry import mapping
import matplotlib.pyplot as plt
#import contextily as ctx

from mis_funciones import geometria_to_pydeck
from mis_funciones import mapa_pydeck
from mis_funciones import cambiar_crs
from mis_funciones import read_gdf_capa
from mis_funciones import interseccion_capas

st.title("Consulta Masa de agua -> Zona Protegida")
st.markdown("Consulta Masa de agua -> Zona Protegida")
st.sidebar.header("Consulta Masa de agua -> Zona Protegida")


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
masas_agua = [c for c in lista_de_capas if c.startswith("MasasAgua")]
masas_agua = masas_agua + ["RedHidrograficaBasica","Cuencas","CuencasTotales"]


#cargamos la primera capa de zonas protegidas
gdf_zonas=read_gdf_capa(st.session_state.rutaGDB,zonas_protegidas[0]) #el primer elemento de la lista es el 0, el segundo el 1, etc

#cargamos todas las capas de zonas protegidas
for zona in zonas_protegidas[1:]: #empieza en 1 (se salta el primer elemento)
    gdfnew = read_gdf_capa(st.session_state.rutaGDB,zona)
    gdf_zonas = pd.concat([gdf_zonas,gdfnew],ignore_index=True,join="inner",axis=0)

capa = st.selectbox('Selecciona capa de masa de agua', masas_agua )
#cargamos la zona protegida de interés
if capa:
    gdf_masa=read_gdf_capa(st.session_state.rutaGDB,capa)
    codigo_masa=st.selectbox("selecciona código de masa de agua",gdf_masa.COD_MASA.unique())
    if codigo_masa:
        gdf_masa=gdf_masa[gdf_masa.COD_MASA == codigo_masa]
        
        gdf_zonas_solapadas = interseccion_capas(gdf_masa,gdf_zonas)
        
        if st.button("Ejecutar Consulta"):
            st.dataframe(gdf_zonas_solapadas.drop(columns=["geometry","info"],inplace=False))
        
            #gdf_masa=cambiar_crs(gdf_masa)
            #gdf_zonas_solapadas=cambiar_crs(gdf_zonas_solapadas)
            polygon_layer_masa = geometria_to_pydeck(gdf_masa,color="blue")
            polygon_layer_zona= geometria_to_pydeck(gdf_zonas_solapadas,color="red")
            mapa_pydeck([polygon_layer_masa,polygon_layer_zona])
            

            