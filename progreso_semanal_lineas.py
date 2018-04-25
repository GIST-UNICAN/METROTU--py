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
import os
from datetime import datetime
from itertools import chain

lista_archivos = defaultdict(list)
recorridos = ("Barrios_Sardinero", "Barrios_Valdecilla",
              "Sardinero_barrios", "Valdecilla_barrios")
lista_df = dict()
lineas = (3, 8, 9, 13, 14, 17, 20)
dia_desde = 2018416
dia_hasta = 2018420
dias = list(range(dia_desde, dia_hasta+1, 1))
dias = list(map(str, dias))
cortes = {3: (8, 14, 20), 17: (8, 14), 8: (8, 14), 9: (8, 14)}


def devuelve_color():
    for color in ("b", "g", "r", "c", "g", "m", "y", "k"):
        yield color


for nombre in recorridos:
    nombres_archivos = list()
    for dia in dias:
        lista_archivos[nombre].append(
            *glob.glob('.\CSV\{0}-{1}.csv'.format(dia, nombre)))
    lista_df_sentido = list()
    for file in lista_archivos[nombre]:
        df = pd.read_csv(file)
        df['dia'] = pd.DatetimeIndex(df['salida']).day
        lista_df_sentido.append(df)
    lista_df[nombre] = pd.concat(lista_df_sentido)
diccionario_linea_sentido = defaultdict(lambda: defaultdict(list))
for sentido, dataframe in lista_df.items():
    grupo_linea = dataframe.sort_values(
        by=['salida']).groupby(['linea_real', 'dia'])
    for key in grupo_linea.groups.keys():
        diccionario_linea_sentido[sentido][key[0]].append(
            grupo_linea.get_group(key))
directorio = 'variacion_semanal_{}_{}'.format(dia_desde, dia_hasta)
if os.path.exists(directorio):
    pass
else:
    os.mkdir(directorio)
for sentido in diccionario_linea_sentido.keys():
    for linea, lista_dataframe in diccionario_linea_sentido[sentido].items():
        print("SENTIDO: "+sentido+" LINEA: "+str(linea)+" DIAS: "+str(len(lista_dataframe)))
        fig = plt.figure(figsize=(10, 5))
        ax = plt.gca()
        plt.grid(True)
        handles = []
        labels = []
        colores = devuelve_color()
        colores2 = devuelve_color()
        if linea in cortes:
            print("SENTIDO: "+sentido+" LINEA: "+str(linea)+" esta en cortes: ")
            horas_corte = chain(cortes[linea], (24,)) 
            for df_dia in lista_dataframe:
                grupos = list()
                hora_0 = 0
                horas_corte = chain(cortes[linea], (24,)) 
                for hora_1 in horas_corte:
                    franja = (hora_0 < df_dia["hora salida"]) & (
                        df_dia["hora salida"] < hora_1)
                    grupos.append(df_dia[franja])
                    hora_0 = hora_1
                print("SENTIDO: "+sentido+" LINEA: "+str(linea)+" grupos: "+str(list(horas_corte)))
                x_s = (g["hora salida"] for g in grupos)
                y_s = (g["espera minutos"] for g in grupos)
                #dias = (g["dia"] for g in grupos)
                color=next(colores)
                color2=next(colores2)
                for x, y  in zip(x_s, y_s):
                    plt.scatter(x, y, color=color)
                    handle, = plt.plot(x, y, color=color2)
                handles.append(handle)
                labels.append(str(df_dia["dia"].iloc[0]))
        else:
            pass
            x_s = (df_dia["hora salida"] for df_dia in lista_dataframe)
            y_s = (df_dia["espera minutos"] for df_dia in lista_dataframe)
            dias = (df_dia["dia"] for df_dia in lista_dataframe)           
            for x, y, dia in zip(x_s, y_s, dias):
                plt.scatter(x, y, color=next(colores))
                handle, = plt.plot(x, y, color=next(colores2))
                handles.append(handle)
                labels.append(dia.tolist()[0])

        plt.xlabel('Hora del día')
        plt.ylabel('Minutos de transbordo')
        plt.ylim(0, 20)
        plt.xlim(7, 23.5)
        plt.legend(handles, labels, loc=1, title='Días')
        plt.savefig(directorio+'\\'+sentido+str(linea))
