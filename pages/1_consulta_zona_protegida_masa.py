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
from osgeo import ogr
import matplotlib.pyplot as plt
#import contextily as ctx

def listar_capas(gdb_path):
    # Abrimos la GDB
    ds = ogr.Open(gdb_path)
    if not ds:
        print(f"No se pudo abrir la geodatabase: {gdb_path}")
        return

    
    lista_capas = []
    for i in range(ds.GetLayerCount()):
        layer = ds.GetLayerByIndex(i)
        layer_name = layer.GetName()  # Devuelve la ruta tipo "Grupo/Capa"
        geom_type = ogr.GeometryTypeToName(layer.GetGeomType())
        #print(f"- {layer_name} ({geom_type})")
        lista_capas.append(layer_name)

    return lista_capas


st.set_page_config(page_title="Consulta Zona Protegida -> Masa de agua")
st.markdown("Consulta Zona Protegida -> Masa de agua")
st.sidebar.header("Consulta Zona Protegida -> Masa de agua")
#listamos todas las capas que tiene el gdb 
lista_de_capas=listar_capas(st.session_state.rutaGDB)
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


#cargamos la primera capa masas de agua
gdf_masas=gpd.read_file(st.session_state.rutaGDB,layer=masas_agua[0]) #el primer elemento de la lista es el 0, el segundo el 1, etc

#cargamos todas las capas de zonas protegidas
for masa in masas_agua[1:]: #empieza en 1 (se salta el primer elemento)
    gdfnew = gpd.read_file(st.session_state.rutaGDB,layer=masa)
    gdf_masas = pd.concat([gdf_masas,gdfnew],ignore_index=True,join="inner",axis=0)

capa = st.selectbox('Selecciona capa de zona protegida', zonas_protegidas )
#cargamos la zona protegida de interés
if capa:
    gdf_zona=gpd.read_file(st.session_state.rutaGDB,layer=capa)
    EUZPROTCOD=st.selectbox("selecciona código de zona protegida",gdf_zona.EUZPROTCOD.unique())
    if EUZPROTCOD:
        gdf_zona=gdf_zona[gdf_zona.EUZPROTCOD == EUZPROTCOD]
        
        #filtro las masas de agua que intersecan a mi zona protegida
        gdf_masas_solapadas = gdf_masas[gdf_masas.geometry.apply(lambda x: x.intersects(gdf_zona.geometry.iloc[0]))]
        #calculo el area de las masas intersecada con la zona protegida
        gdf_interseccion=gdf_masas.geometry.apply(lambda x: x.intersection(gdf_zona.geometry.iloc[0]))
        #me quedo, obviamente, con las zonas protegidas con un área de intersección > 0
        areas_interseccion=gdf_interseccion.geometry.area[gdf_interseccion.geometry.area>0]
        #añado a las masas solapadas una nueva columna con el area intersecada
        gdf_masas_solapadas.loc[areas_interseccion.index,"Area_interseccion_m2"]=areas_interseccion
        #añado nueva columna con el aire total
        gdf_masas_solapadas["Area_total_m2"]=gdf_masas_solapadas.geometry.area
        #añado porcentaje
        gdf_masas_solapadas["Porcentaje_area_(%)"]=(gdf_masas_solapadas.Area_interseccion_m2/gdf_masas_solapadas.Area_total_m2)*100
        
        if st.button("Ejecutar Consulta"):
            st.dataframe(gdf_masas_solapadas.drop(columns=["geometry"],inplace=False))
        
        if st.button("Ver en mapa"):
            fig=plt.figure()
            ax=fig.add_subplot(111)
            gdf_masas_solapadas.plot(column="COD_MASA",ax=ax,cmap="Blues",label="Masas de agua",legend=True)
            leg1=ax.get_legend()
            gdf_zona.plot(column="EUZPROTCOD",ax=ax,cmap="autumn",label="Zona protegida "+str(capa)+" "+EUZPROTCOD,legend=True,  legend_kwds={'loc': 'upper left'})
            #ax.legend(loc="upper center")
            #ctx.add_basemap(ax=ax, crs=gdf_zona.crs, source= ctx.providers.OpenStreetMap.DE.url)
            ax.add_artist(leg1)
            st.pyplot(fig,clear_figure=False)
            