# -*- coding: utf-8 -*-
"""
Created on Wed Jul  2 12:24:38 2025

@author: dherves
"""

import pandas as pd
from shapely.geometry import mapping
import geopandas as gpd
import streamlit as st
import pydeck as pdk


def cambiar_crs(gdf):
    
    # Asegurarse de que está en WGS84
    if gdf.crs and gdf.crs.to_epsg() != 4326:
        gdf = gdf.to_crs(epsg=4326)
    return gdf
    

def carga_datos(ruta):
   
    capas = list(gpd.list_layers(ruta)["name"])

    if capas:
        capa_sel = st.selectbox("Selecciona una capa", capas)
        try:
            gdf = gpd.read_file(ruta, layer=capa_sel)
        except Exception as e:
            st.error(f"Error al cargar la capa: {e}")
        else:
            if gdf.empty:
                st.warning("La capa está vacía.")
            else:
                st.success(f"{len(gdf)} elementos cargados")

               
                gdf=cambiar_crs(gdf)
                gdf = gdf[gdf.geometry.notnull()]
               
                
               

               
    else:
        st.error("No se encontraron capas en la GDB.")
    return gdf




def geometria_to_pydeck(gdf):
    
    geometry_type=gdf.geometry.geom_type.unique()[0]
    
    data=[]
    
    
    
    if geometry_type == "Polygon":
        #type_of_layer="PolygonLayer"
        
        for _, row in gdf.iterrows():
            geom=row.geometry
            coords=list(mapping(geom)["coordinates"])
            data.append({"coordinates":coords[0]})
        layer=pdk.Layer(
            "PolygonLayer",
            data=pd.DataFrame(data),
            get_polygon="coordinates",
            get_fill_color=[0, 100, 255, 100],
            get_line_color=[0, 0, 0],
            line_width_min_pixels=1,
            pickable=True,)
            
    elif geometry_type == "MultiPolygon":
        #type_of_layer ="PolygonLayer"
        for _,row in gdf.iterrows():
            geom=row.geometry
            for part in geom.geoms:
                coords = list(mapping(part)["coordinates"])
                data.append({"coordinates": coords[0]})  # solo anillo exterior
                
        layer=pdk.Layer(
            "PolygonLayer",
            data=pd.DataFrame(data),
            get_polygon="coordinates",
            get_fill_color=[0, 100, 255, 100],
            get_line_color=[0, 0, 0],
            line_width_min_pixels=1,
            pickable=True,)
    elif geometry_type=="LineString":
        for _,row in gdf.iterrows():
            geom=row.geometry
            coords=list(mapping(geom)["coordinates"])
            data.append({"coordinates":coords})
            
        layer=pdk.Layer(
            "PathLayer",
            data=pd.DataFrame(data),
            get_path="coordinates",
            get_color=[255, 0, 0],
            get_width=50,
            lineWidthUnits="pixels",
            pickable=True,
            autohighlight=True,
            )
        
    elif geometry_type=="MultiLineString":
        for _,row in gdf.iterrows():
            geom=row.geometry
            for part in geom.geoms:
                coords=list(mapping(part)["coordinates"])
                data.append({"coordinates":coords})
            
        layer=pdk.Layer(
            "PathLayer",
            data=pd.DataFrame(data),
            get_path="coordinates",
            get_color=[255, 0, 0],
            get_width=50,
            lineWidthUnits="pixels",
            pickable=True,
            autohighlight=True,
            )
    elif geometry_type == "Point":
        
        for _,row in gdf.iterrows():
            geom=row.geometry
            coords=list(mapping(geom)["coordinates"])
            data.append({"coordinates":coords})
        
        layer = pdk.Layer(
            "ScatterplotLayer",
            data=pd.DataFrame(data),
            get_position="coordinates",
            get_color=[0, 200, 0],
            get_radius=1000,  # Ajusta el radio
            radUnits="pixels",
            pickable=True,
        )                 
    
    return layer    



def mapa_pydeck(list_of_layers):
    
    # Vista inicial centrada en los datos
    view_state = pdk.ViewState(
        latitude=42.7,
        longitude=-8.5,
        zoom=7
    )

    # Crear y mostrar el mapa
    deck = pdk.Deck(
        layers=list_of_layers,
        initial_view_state=view_state,
        #map_style="mapbox://styles/mapbox/light-v9"
    )

    st.pydeck_chart(deck)
    
    return




if __name__ == "__main__":
    
    gdf=carga_datos("./data/PHGC28_33_GDB_Ed00.gdb")
    layer=geometria_to_pydeck(gdf)
    
    