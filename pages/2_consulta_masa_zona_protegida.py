# -*- coding: utf-8 -*-
"""
Created on Tue Jul  1 11:29:19 2025

@author: dherves
"""

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


#st.set_page_config(page_title="Consulta Masa de agua -> Zona Protegida")
st.markdown("Consulta Masa de agua -> Zona Protegida")
st.sidebar.header("Consulta Masa de agua -> Zona Protegida")


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


#cargamos la primera capa de zonas protegidas
gdf_zonas=gpd.read_file(st.session_state.rutaGDB,layer=zonas_protegidas[0]) #el primer elemento de la lista es el 0, el segundo el 1, etc

#cargamos todas las capas de zonas protegidas
for zona in zonas_protegidas[1:]: #empieza en 1 (se salta el primer elemento)
    gdfnew = gpd.read_file(st.session_state.rutaGDB,layer=zona)
    gdf_zonas = pd.concat([gdf_zonas,gdfnew],ignore_index=True,join="inner",axis=0)

capa = st.selectbox('Selecciona capa de masa de agua', masas_agua )
#cargamos la zona protegida de interés
if capa:
    gdf_masa=gpd.read_file(st.session_state.rutaGDB,layer=capa)
    codigo_masa=st.selectbox("selecciona código de masa de agua",gdf_masa.COD_MASA.unique())
    if codigo_masa:
        gdf_masa=gdf_masa[gdf_masa.COD_MASA == codigo_masa]
        
        #filtro las zonas protegidas que intersecan a mi masa de agua
        gdf_zonas_solapadas = gdf_zonas[gdf_zonas.geometry.apply(lambda x: x.intersects(gdf_masa.geometry.iloc[0]))]
        #calculo el area de las zonas protegidas intersecada con la masa de agua
        gdf_interseccion=gdf_zonas.geometry.apply(lambda x: x.intersection(gdf_masa.geometry.iloc[0]))
        #me quedo, obviamente, con las zonas protegidas con un área de intersección > 0
        areas_interseccion=gdf_interseccion.geometry.area[gdf_interseccion.geometry.area>0]
        #añado a las zonas protegidas solapadas una nueva columna con el area intersecada
        gdf_zonas_solapadas.loc[areas_interseccion.index,"Area_interseccion_m2"]=areas_interseccion
        #añado nueva columna con el area total
        gdf_zonas_solapadas["Area_total_m2"]=gdf_zonas_solapadas.geometry.area
        #añado porcentaje
        gdf_zonas_solapadas["Porcentaje_area_(%)"]=(gdf_zonas_solapadas.Area_interseccion_m2/gdf_zonas_solapadas.Area_total_m2)*100
        
        if st.button("Ejecutar Consulta"):
            st.dataframe(gdf_zonas_solapadas.drop(columns=["geometry"],inplace=False))
        
        if st.button("Ver en mapa"):
            fig=plt.figure()
            ax=fig.add_subplot(111)
            gdf_zonas_solapadas.plot(column="EUZPROTCOD",ax=ax,cmap="Blues",label="Zonas protegidas",legend=True)
            leg1=ax.get_legend()
            gdf_masa.plot(column="COD_MASA",ax=ax,cmap="autumn",label="Masa de agua "+str(capa)+" "+codigo_masa,legend=True,  legend_kwds={'loc': 'upper left'})
            #ax.legend(loc="upper center")
            #ctx.add_basemap(ax=ax, crs=gdf_zona.crs, source= ctx.providers.OpenStreetMap.DE.url)
            ax.add_artist(leg1)
            st.pyplot(fig,clear_figure=False)
            