# -*- coding: utf-8 -*-
"""
Created on Mon Apr 23 10:32:08 2018

@author: Andres
"""

import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict

lista_archivos=defaultdict(list)
recorridos=("Barrios_Sardinero","Barrios_Valdecilla","Sardinero_barrios","Valdecilla_barrios")
lista_df=dict()
lineas=(3,8,9,13,14,17,20)
dia_desde=2018416
dia_hasta=2018420
dias=list(range(dia_desde,dia_hasta+1,1))
dias=list(map(str,dias))


for nombre in recorridos:
    nombres_archivos=list()
    for dia in dias:
        lista_archivos[nombre].append(*glob.glob('.\CSV\{0}-{1}.csv'.format(dia,nombre)))
    lista_df_sentido=list()
    for file in lista_archivos[nombre]:
        df=pd.read_csv(file)
        df['dia']=pd.DatetimeIndex(df['salida']).day
        lista_df_sentido.append(df)
    lista_df[nombre]=pd.concat(lista_df_sentido)
grupo_clave=None
diccionario_linea_sentido=defaultdict(lambda: defaultdict(list))   
for sentido,dataframe in lista_df.items():
    grupo_linea=dataframe.sort_values( by=['salida']).groupby(['linea_real','dia'])
    for key in grupo_linea.groups.keys():
        diccionario_linea_sentido[sentido][key[0]].append(grupo_linea.get_group(key))
        
for k in diccionario_linea_sentido.keys():
    for linea, lista_dataframe in diccionario_linea_sentido[k]:
        if 
        
    
###        fig, axes = plt.subplots(nrows=nrows, ncols=ncols)
#fig = plt.figure(figsize=(10, 5))
#ax = plt.gca()
###        legend = ax.get_legend()
#plt.grid(True)
#handles = []
#labels = []
#
#grupo = df_interc_barrios.sort_values( by=['salida']).groupby('linea_real')
#for key in grupo.groups.keys():
#    if key in cortes:
#        horas_corte = chain(cortes[key], (24,))
#        grupos = list()
#        hora_0 = 0
#        for hora_1 in horas_corte:
#            franja = (hora_0 < grupo.get_group(key)["hora salida"]) & (
#                grupo.get_group(key)["hora salida"] < hora_1)
#            grupos.append(grupo.get_group(key)[franja])
#            hora_0 = hora_1
#
#        x_s = (g["hora salida"] for g in grupos)
#        y_s = (g["espera minutos"] for g in grupos)
#        for x, y in zip(x_s, y_s):
#            plt.scatter(x, y, color=colores[key])
#            handle, = plt.plot(x, y, color=colores[key])
#
#    else:
#        x = grupo.get_group(key)['hora salida']
#        y = grupo.get_group(key)['espera minutos']
#        plt.scatter(x, y, color=colores[key])
#        handle, = plt.plot(x, y, color=colores[key])
#    handles.append(handle)
#    labels.append(key)
## print(type(ultimo_plot))
###            artistas[str(key)] = ultimo_plot
## ultimo_plot.set_label=str(key)
#    plt.ylim(0, 20)
#    plt.xlim(7, 23.5)
## print(ax.get_legend_handles_labels())
#plt.xlabel('Hora del día')
#plt.ylabel('Minutos de transbordo')
#plt.legend(handles, labels,
#           loc=1,
#           title='Líneas')
#        



