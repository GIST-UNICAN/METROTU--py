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
from datetime import datetime, date, timedelta
from itertools import chain
import textos_html_informe_semanal
from shutil import copyfile
import locale
import collections
from pdfkit import from_file as create_pdf


locale.setlocale(locale.LC_ALL, '')
lista_archivos = defaultdict(list)
recorridos = ("Barrios_Sardinero", "Sardinero_barrios", "Barrios_Valdecilla",
              "Valdecilla_barrios")
lista_df = dict()
lineas = (8, 9, 13, 14, 17, 20)#(3, 8, 9, 13, 14, 17, 20)

cortes = {17: (8, 14), 8: (8, 14), 9: (8, 14)}#{3: (8, 14, 20), 17: (8, 14), 8: (8, 14), 9: (8, 14)}


cuerpo_informe = ""

actual = datetime.now()
dia_resta = 3
dia_inicio = actual-timedelta(days=(dia_resta+6))
dia_fin = actual-timedelta(days=dia_resta)
dia_excluir = (25,)
un_minuto = timedelta(minutes=1)
dia_primero = int(
    "".join((str(dia_inicio.year), str(dia_inicio.month), str(dia_inicio.day))))
dia_hasta = int(
    "".join((str(dia_fin.year), str(dia_fin.month), str(dia_fin.day))))

dia_control = dia_inicio
un_dia = timedelta(days=1)
lista_dias = []
while dia_control <= dia_fin:
    if dia_control.weekday() < 5 and dia_control.day not in dia_excluir:
        lista_dias.append(dia_control)
    dia_control += un_dia
lista_dias.append(datetime(1990,1,1,0,0,0))

def devuelve_color():
    for color in ("b", "g", "r", "c", "m", "y", "y", "k"):
        yield color


def devuelve_estilo():
    for color in ("--", "-", "-", "-", "-", "-", "-", "-"):
        yield color


def mes_letra(mes):
    return date(1900, mes, 1).strftime('%B')


# se generan unas listas recuperadas de los csv de los informes y se disagrega por dia y linea
for nombre in recorridos:
    nombres_archivos = list()
    for dia in lista_dias:
        dia_desde = int(
                "".join((str(dia.year), str(dia.month), str(dia.day))))
        lista_archivos[nombre].append(
            *glob.glob('.\CSV\{0}-{1}.csv'.format(dia_desde, nombre)))
    lista_df_sentido = list()
    for file in lista_archivos[nombre]:
        df = pd.read_csv(file)
        if '199011' in file:
            df['dia'] = 'teorico'
        else:
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
directorio = 'variacion_semanal_{}_{}'.format(dia_primero, dia_hasta)
if os.path.exists(directorio):
    pass
else:
    os.mkdir(directorio)
copyfile('tabla.css', directorio+'tabla.css')
# se pintan las gráficas y se guardan
for sentido in diccionario_linea_sentido.keys():
    for linea, lista_dataframe in collections.OrderedDict(sorted(diccionario_linea_sentido[sentido].items())).items():
        #        print("SENTIDO: "+sentido+" LINEA: "+str(linea)+" DIAS: "+str(len(lista_dataframe)))
        fig = plt.figure(figsize=(10, 5))
        ax = plt.gca()
        plt.grid(True)
        handles = []
        labels = []
        colores = devuelve_color()
        estilos = devuelve_estilo()
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
                estilo = next(estilos)
                for x, y in zip(x_s, y_s):
                    if str(df_dia["dia"].iloc[0]) != 'teorico':
                        plt.scatter(x, y, color=color)
                    handle, = plt.plot(x, y, color=color, linestyle=estilo)
                handles.append(handle)
                labels.append(str(df_dia["dia"].iloc[0]))
        else:
            pass
            x_s = (df_dia["hora salida"] for df_dia in lista_dataframe)
            y_s = (df_dia["espera minutos"] for df_dia in lista_dataframe)
            dias = (df_dia["dia"] for df_dia in lista_dataframe)
            for x, y, dia in zip(x_s, y_s, dias):
                color = next(colores)
                if dia.tolist()[0] != 'teorico':
                    plt.scatter(x, y, color=color)

                handle, = plt.plot(x, y, color=color, linestyle=next(estilos))
                handles.append(handle)
                labels.append(dia.tolist()[0])

        plt.xlabel('Hora del día')
        plt.ylabel('Minutos de transbordo')
        plt.ylim(0, 20)
        plt.xlim(7, 23.5)
        plt.legend(handles, labels, loc=1, title='Días')
        figura_ruta = sentido+'-'+str(linea)
        plt.savefig(directorio+'\\'+sentido+'-'+str(linea))
        titulo = 'Línea {} sentido {}'.format(str(linea), sentido)
        cuerpo_informe = "".join((cuerpo_informe,
                                  textos_html_informe_semanal.apartado_informe.format(
                                      titulo=titulo,
                                      grafico=figura_ruta)))

# se genera un informe de este tipo
with open(directorio+'\\'+'informe.html', 'w') as file:
    print(textos_html_informe_semanal.plantilla_web_estilos +
          textos_html_informe_semanal.plantilla_web_cuerpo.format(
              dia_inicio=dia_inicio.day,
              dia_fin=dia_fin.day,
              mes_inicio=mes_letra(dia_inicio.month),
              mes_fin=mes_letra(dia_fin.month),
              informe_completo=cuerpo_informe), file=file)
    create_pdf(
        directorio+'\\'+'informe.html',
        directorio+'\\'+'resumen_semanal_{}-{}-{}_al_{}-{}-{}.pdf'.format(dia_inicio.year, dia_inicio.month, dia_inicio.day,
                                                          dia_fin.year, dia_fin.month, dia_fin.day))
