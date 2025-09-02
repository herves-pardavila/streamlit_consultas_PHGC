# -*- coding: utf-8 -*-
"""
Created on Wed Jul  2 12:24:38 2025

@author: dherves

Funciones que usa nuestra aplicación de streamlit

"""

import pandas as pd
from shapely.geometry import mapping
import geopandas as gpd
import streamlit as st
import pydeck as pdk


def cambiar_crs(gdf):
    """
    La librería que usamos para representar capas GIS en mapas se llam pydeck. Esta 
    librería solo admite capas en el crs 4326

    Parameters
    ----------
    gdf : GeoPandas.GeoDataFrame
        capas gis vectorial leida con geopandas

    Returns
    -------
    gdf : GeoPandas.GeoDataFrame
        capas gis vectorial leida con geopandas y con crs = 4326

    """
    
    # Asegurarse de que está en WGS84
    if gdf.crs and gdf.crs.to_epsg() != 4326:
        gdf = gdf.to_crs(epsg=4326)
    return gdf
    
def read_gdf_capa(ruta,capa):
    """
    Lee una capa de un gdb

    Parameters
    ----------
    ruta : str
        Ruta a una carpeta gdb
    capa : str
        nombre de la capa

    Returns
    -------
    gdf : GeoPandas.GeoDataFrame
        capa gis seleccionada

    """
    
    gdf = gpd.read_file(ruta,layer=capa)
   
    gdf["info"] = gdf.apply(
        lambda row: "\n".join([f"{col}: {row[col]}" for col in gdf.columns if col != gdf.geometry.name]),
        axis=1
    )
    return gdf
    
def carga_datos(ruta):
    """
    Lee una carpeta gdb, lista las capas allí presentas y abre un desplegable en la 
    aplicación de streamlit para que seleciones la capa que quieres cargar

    Parameters
    ----------
    ruta : str
        Ruta al archivo/carpeta gdb

    Returns
    -------
    gdf : GeoPandas.GeoDataFrame
        capa seleccionada en el desplegable de la apliación streamlit

    """
   
    capas = list(gpd.list_layers(ruta)["name"])

    if capas:
        capa_sel = st.selectbox("Selecciona una capa", capas)
        try:
            gdf = read_gdf_capa(ruta, capa_sel)
        except Exception as e:
            st.error(f"Error al cargar la capa: {e}")
        else:
            if gdf.empty:
                st.warning("La capa está vacía.")
            else:
                st.success(f"{len(gdf)} elementos cargados")

               
                gdf = gdf[gdf.geometry.notnull()]
               
                
               

               
    else:
        st.error("No se encontraron capas en la GDB.")
    return gdf




def geometria_to_pydeck(gdf,color=None):
    """
    Transforma la columna geometry de un GeoPandas.GeoDataFrame a un formato
    que pydeck puede representar.

    Parameters
    ----------
    gdf : GeoPandas.GeoDataFrame
        capa gis que queremos representar en un mapa pydeck
    color : st, optional
        color con el queremos representar el gdf. The default is blue.

    Returns
    -------
    layer : pydeck.Layer
        Objeto pydeck que ya le podemos pasar a la función mapa_pydeck para que 
        lo represente

    """
    
    global colors
    colors={"red":[255,0,0,100],"blue":[0,0,255,100],"verde":[0,255,0,100],"amarillo":[255,255,0,100],"purple":[120,0,120,100]}
    
    gdf=cambiar_crs(gdf)
    geometry_type=gdf.geometry.geom_type.unique()[0]
    
    data=[]
    

    if geometry_type == "Polygon":
        #type_of_layer="PolygonLayer"
        
        for _, row in gdf.iterrows():
            geom=row.geometry
            coords=list(mapping(geom)["coordinates"])
            data.append({"coordinates":coords[0], "info":row["info"]})
            
        if color != None:
            fill_color=colors[color]
        else:
            fill_color=[0, 100, 255, 100]
        layer=pdk.Layer(
            "PolygonLayer",
            data=pd.DataFrame(data),
            get_polygon="coordinates",
            get_fill_color=fill_color,
            get_line_color=[0, 0, 0],
            line_width_min_pixels=1,
            pickable=True,)
            
    elif geometry_type == "MultiPolygon":
        #type_of_layer ="PolygonLayer"
        for _,row in gdf.iterrows():
            geom=row.geometry
            for part in geom.geoms:
                coords = list(mapping(part)["coordinates"])
                data.append({"coordinates": coords[0], "info":row["info"]})  # solo anillo exterior
        if color != None:
            fill_color=colors[color]
        else:
            fill_color=[0, 100, 255, 100]
                
        layer=pdk.Layer(
            "PolygonLayer",
            data=pd.DataFrame(data),
            get_polygon="coordinates",
            get_fill_color=fill_color,
            get_line_color=[0, 0, 0],
            line_width_min_pixels=1,
            pickable=True,)
    elif geometry_type=="LineString":
        for _,row in gdf.iterrows():
            geom=row.geometry
            coords=list(mapping(geom)["coordinates"])
            data.append({"coordinates":coords, "info":row["info"]})
        
        if color != None:
            fill_color=colors[color]
        else:
            fill_color=[255, 0, 0]
        
        layer=pdk.Layer(
            "PathLayer",
            data=pd.DataFrame(data),
            get_path="coordinates",
            get_color=fill_color,
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
                data.append({"coordinates":coords,"info":row["info"]})
        
        if color != None:
            fill_color=colors[color]
        else:
            fill_color=[255, 0, 0]    
        
        layer=pdk.Layer(
            "PathLayer",
            data=pd.DataFrame(data),
            get_path="coordinates",
            get_color=fill_color,
            get_width=50,
            lineWidthUnits="pixels",
            pickable=True,
            autohighlight=True,
            )
    elif geometry_type == "Point":
        
        for _,row in gdf.iterrows():
            geom=row.geometry
            coords=list(mapping(geom)["coordinates"])
            data.append({"coordinates":coords,"info":row["info"]})
        
        
        if color != None:
            fill_color=colors[color]
        else:
            fill_color=[0, 200, 0]
        layer = pdk.Layer(
            "ScatterplotLayer",
            data=pd.DataFrame(data),
            get_position="coordinates",
            get_color=fill_color,
            get_radius=1000,  # Ajusta el radio
            radUnits="pixels",
            pickable=True,
        )                 
    
    return layer    

def mapa_pydeck(list_of_layers):
    """
    Genera un mapa en una aplicación de streamlit

    Parameters
    ----------
    list_of_layers : list
        Lista de capas a representar. Cada capa tiene que ser una salida de la
        función geometria_to_pydeck, definida más arriba. La salida de esa función
        tiene un formato que pydeck entiende

    Returns
    -------
    None.

    """
    
    # Vista inicial centrada en las siguientes latitudes y longitudes
    view_state = pdk.ViewState(
        latitude=42.7,
        longitude=-8.5,
        zoom=7
    )

    # Crear y mostrar el mapa
    deck = pdk.Deck(
        layers=list_of_layers,
        initial_view_state=view_state,
        tooltip={"text": "{info}"},
        map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json",
    )

    st.pydeck_chart(deck)
    
    return

def interseccion_capas(capa_central, capa_periferica):
    """
    Obtiene los elementos de una capa periférica que intersecan a una capa central.
    Además, para cada uno de estos elementos, calcula el área de la intersección 
    y el porcentaje que representa esta intersección sobre el área total del 
    elemento de la capa periférica.

    Parameters
    ----------
    capa_central : geopandas.GeoDataFrame
        Capa central
    capa_periferica : geopandas.GeoDataFrame
        Capa periférica

    Returns
    -------
    gdf_perifericas_solapadas : TYPE
        DESCRIPTION.

    """
    
    #filtro los elementos de la capa periferica que intersecan a mi capa central
    gdf_perifericas_solapadas = capa_periferica[capa_periferica.geometry.apply(lambda x: x.intersects(capa_central.geometry.iloc[0]))]
    
    #calculo las areas de la capa periferica que se intersecan con la central
    gdf_interseccion=gdf_perifericas_solapadas.geometry.apply(lambda x: x.intersection(capa_central.geometry.iloc[0]))
    
    #me quedo, obviamente, con las zonas protegidas con un área de intersección > 0
    areas_interseccion=gdf_interseccion.geometry.area[gdf_interseccion.geometry.area>0]
    #areas_interseccion=gdf_interseccion.geometry.area[gdf_interseccion.geometry.area>0]
    
    #añado a la capa periférica, una nueva columna con las áreas de intersección
    gdf_perifericas_solapadas.loc[areas_interseccion.index,"Area_interseccion_m2"]=areas_interseccion
    
    #añado nueva columna con el aire total
    gdf_perifericas_solapadas["Area_total_m2"]=gdf_perifericas_solapadas.geometry.area
    
    #añado porcentaje
    gdf_perifericas_solapadas["Porcentaje_area_(%)"]=(gdf_perifericas_solapadas.Area_interseccion_m2/gdf_perifericas_solapadas.Area_total_m2)*100
    
    return gdf_perifericas_solapadas



if __name__ == "__main__":
    
    gdf=carga_datos("./data/PHGC28_33_GDB_Ed00.gdb")
    layer=geometria_to_pydeck(gdf)
    
    