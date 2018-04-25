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
from datetime import datetime, date
from itertools import chain
import textos_html_informe_semanal
from shutil import copyfile
import locale
from pdfkit import from_file as create_pdf


locale.setlocale(locale.LC_ALL, '')
lista_archivos = defaultdict(list)
recorridos = ("Barrios_Sardinero", "Sardinero_barrios","Barrios_Valdecilla",
               "Valdecilla_barrios")
lista_df = dict()
lineas = (3, 8, 9, 13, 14, 17, 20)
año_desde = 2018
año_hasta = 2018
mes_desde = 4
mes_hasta = 4
dia_inicio = 16
dia_fin = 20
dia_desde = int("".join((str(año_desde), str(mes_desde), str(dia_inicio))))
dia_hasta = int("".join((str(año_hasta), str(mes_hasta), str(dia_fin))))
dias = list(range(dia_desde, dia_hasta+1, 1))
dias = list(map(str, dias))
cortes = {3: (8, 14, 20), 17: (8, 14), 8: (8, 14), 9: (8, 14)}
cuerpo_informe = ""


def devuelve_color():
    for color in ("b", "g", "r", "c", "g", "m", "y", "k"):
        yield color


def mes_letra(mes):
    return date(1900, mes, 1).strftime('%B')


# se generan unas listas recuperadas de los csv de los informes y se disagrega por dia y linea
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

# se genera el directorio donde van los archivos
directorio = 'variacion_semanal_{}_{}'.format(dia_desde, dia_hasta)
if os.path.exists(directorio):
    pass
else:
    os.mkdir(directorio)
copyfile('tabla.css', directorio+'tabla.css')
# se pintan las gráficas y se guardan
for sentido in diccionario_linea_sentido.keys():
    for linea, lista_dataframe in diccionario_linea_sentido[sentido].items():
        #        print("SENTIDO: "+sentido+" LINEA: "+str(linea)+" DIAS: "+str(len(lista_dataframe)))
        fig = plt.figure(figsize=(10, 5))
        ax = plt.gca()
        plt.grid(True)
        handles = []
        labels = []
        colores = devuelve_color()
        colores2 = devuelve_color()
        if linea in cortes:
            #            print("SENTIDO: "+sentido+" LINEA: "+str(linea)+" esta en cortes: ")
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
#                print("SENTIDO: "+sentido+" LINEA: "+str(linea)+" grupos: "+str(list(horas_corte)))
                x_s = (g["hora salida"] for g in grupos)
                y_s = (g["espera minutos"] for g in grupos)
                #dias = (g["dia"] for g in grupos)
                color = next(colores)
                color2 = next(colores2)
                for x, y in zip(x_s, y_s):
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
        figura_ruta = sentido+'-'+str(linea)
        plt.savefig(directorio+'\\'+sentido+'-'+str(linea))
        titulo='Línea {} sentido {}'.format(str(linea),sentido)
        cuerpo_informe = "".join((cuerpo_informe,
                                  textos_html_informe_semanal.apartado_informe.format(
                                      titulo=titulo,
                                      grafico=figura_ruta)))

# se genera un informe de este tipo
with open(directorio+'\\'+'informe.html', 'w') as file:
    print(textos_html_informe_semanal.plantilla_web_estilos +
          textos_html_informe_semanal.plantilla_web_cuerpo.format(
              dia_inicio=dia_inicio,
              dia_fin=dia_fin,
              mes_inicio=mes_letra(mes_desde),
              mes_fin=mes_letra(mes_hasta),
              informe_completo=cuerpo_informe), file=file)
    create_pdf(
        directorio+'\\'+'informe.html',
        directorio+'\\'+'{}-{}-{}_al_{}-{}-{}.pdf'.format(año_desde, mes_desde, dia_inicio,
                                                     año_hasta, mes_hasta, dia_fin))
