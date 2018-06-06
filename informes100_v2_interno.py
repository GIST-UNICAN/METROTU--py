# -*- coding: utf-8 -*-
"""
Created on Thu Apr 26 10:09:27 2018

@author: Andres
"""
from logging import basicConfig, DEBUG
basicConfig(level=DEBUG)

import MySQLdb
from datetime import datetime, timedelta, date
import os

from collections import namedtuple, defaultdict, OrderedDict
from itertools import starmap, groupby, chain, repeat
import pandas as pd
import numpy as np
from functools import reduce
import textos_html_informe_100
import matplotlib
# matplotlib.use('Agg')
#import matplotlib.pyplot as plt
from shutil import copyfile
from pdfkit import from_file as create_pdf
import contextlib
from copy import deepcopy
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from bisect import bisect
import operator
from tools.text_and_output import pretty_debug
from tools.general import exhaust_map
from shutil import copyfile
import locale
from pdfkit import from_file as create_pdf


# necesitamos traer de la db los datos de la linea 100
locale.setlocale(locale.LC_ALL, '')
cuerpo_informe = ""
actual = datetime.now()
dia_resta = 1
dia_inicio = actual - timedelta(days=(dia_resta + 6))
dia_fin = actual - timedelta(days=dia_resta)
un_minuto = timedelta(minutes=1)

tamaño_correcto_tupla_valde_sardi = 9
tamaño_correcto_tupla_sardi_valde = 8

dia_control = dia_inicio
un_dia = timedelta(days=1)
lista_dias = []
dias_excluir = (100,)
while dia_control <= dia_fin:
    if dia_control.weekday() < 5 and dia_control.day not in dias_excluir:
        lista_dias.append(dia_control.day)
    dia_control += un_dia

print(lista_dias)

querie = ("set @fecha_ini='{0}-{1}-{2} 00:00:00'".format(
    dia_inicio.year,
    dia_inicio.month,
    dia_inicio.day),
    "set @fecha_fin='{0}-{1}-{2} 23:59:59'".format(
    dia_fin.year,
    dia_fin.month,
    dia_fin.day),
    """SELECT ppa.viaje, ppa.coche, ppa.instante, pti.HoraTeorica, pti.Nodo, TIMESTAMPDIFF(second,ppa.instante,pti.HoraTeorica) as diferencia from pasos_teoricos_intercambiadores  pti
inner join (Select * from pasos_parada_ajustada where linea=100 and parada in (516,512) and Instante between @fecha_ini and @fecha_fin) ppa
on ppa.Parada=pti.Nodo and ppa.coche=pti.Coche and ppa.viaje=pti.viaje  and year(ppa.instante)=year(pti.Horateorica) and month(ppa.instante)=month(pti.Horateorica) and day(ppa.instante)=day(pti.Horateorica)
where HoraTeorica between @fecha_ini and @fecha_fin
order by pti.Nodo,pti.HoraTeorica asc""")


directorio = "informe_lcentral_medias_llegadas_de_{}{}{}_a_{}{}{}\\".format(dia_inicio.year,
                                                                            dia_inicio.month,
                                                                            dia_inicio.day,
                                                                            dia_fin.year,
                                                                            dia_fin.month,
                                                                            dia_fin.day)
archivo = "{}{}{}".format(actual.year,
                          actual.month,
                          actual.day - dia_resta)

colores = ("b",
           "g",
           "r",
           "c",
           "g",
           "m",
           "y",
           "k")

intervalos_horarios = (0, 6, 12, 18, 24)

def normaliza_fecha(fecha):
    return datetime(2000, 1, 1, fecha.hour, fecha.minute, fecha.second)


def devuelve_intervalo(datetime, intervalos_horarios=intervalos_horarios):
    return bisect(intervalos_horarios, datetime.hour)


def mes_letra(mes):
    return date(1900, mes, 1).strftime('%B')


Columnas = namedtuple("Columnas",
                      ("viaje",
                       "coche",
                       "real",
                       "teorica",
                       "nodo",
                       "diferencia"))
columnas = ("viaje",
            "coche",
            "real",
            "teorica",
            "nodo",
            "diferencia")
cols = Columnas(*range(6))


viajes_ordenado = defaultdict(lambda: defaultdict(
    lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(list)))))


if os.path.exists(directorio):
    pass
else:
    os.mkdir(directorio)
copyfile('tabla.css', directorio + 'tabla.css')

with contextlib.closing(MySQLdb.connect(user='root',
                                        password='madremia902',
                                        host='193.144.208.142',
                                        port=3306,
                                        database='autobuses'
                                        )) as conexion:
    with contextlib.closing(conexion.cursor()) as cursor:
        exhaust_map(cursor.execute, querie)
        datos_row = tuple(cursor)

#generamos el diccionario con los viajes y el desvio segun la hora
diccionario_dia_viajes = defaultdict(lambda: defaultdict(lambda: defaultdict(pd.DataFrame)))
for dia_intercambiador, rows in groupby(
        datos_row, lambda fila: (fila[cols.real].day, fila[cols.nodo])):
    for fila in rows:
        if dia_intercambiador[0] in lista_dias:
            df = pd.DataFrame([list(fila),],columns=columnas)
            #normalizamos la hora teorica para el pintado
            df['hora_normalizada']=df['teorica'].apply(normaliza_fecha)
            df['diferencia']=df['diferencia']/60
            #se añade al dataframe o se genera un dataframe nuevo para cada intervalo horario
            if diccionario_dia_viajes[dia_intercambiador[1]
                ][devuelve_intervalo(fila[cols.teorica])][dia_intercambiador[0]].shape[0]==0:
                diccionario_dia_viajes[dia_intercambiador[1]
                ][devuelve_intervalo(fila[cols.teorica])][dia_intercambiador[0]]=df
            else:
                df1=diccionario_dia_viajes[dia_intercambiador[1]
                ][devuelve_intervalo(fila[cols.teorica])][dia_intercambiador[0]]
                df2=df1.append(df)
                diccionario_dia_viajes[dia_intercambiador[1]
                ][devuelve_intervalo(fila[cols.teorica])][dia_intercambiador[0]]=df2
                

#generado un diccionario con el desvio de cada servicio vamos a proceder a pintarlo
        

# si la parada es alguna de las de las cabeceras vamos a usar la consulta
# de la otra db
# for coche_viaje, rows in groupby(datos_row, lambda fila: (fila[cols.coche],
#                                                          fila[cols.viaje])):
#    Sentido = namedtuple(
#        "Sentido", ("Valdecilla_Sardinero", 'Sardinero_Valdecilla'))
#    sentido = Sentido(*range(2))
#    sentido_viaje = ''
#    for fila in rows:
#        if fila[cols.instante].day in dias_excluir:
#            continue
#        if fila[cols.parada] == paradas.Valdecilla:
#            viajes_ordenado[coche_viaje[0]]['Valdecilla_Sardinero'][devuelve_intervalo(fila[cols.instante])][fila[cols.instante].day][coche_viaje[1]
#                                                                                                                                      ].append(normaliza_fecha(fila[cols.instante]))
#            sentido_viaje = sentido.Valdecilla_Sardinero
#        elif fila[cols.parada] == paradas.Int_Sardinero_1:
#            viajes_ordenado[coche_viaje[0]]['Sardinero_Valdecilla'][devuelve_intervalo(fila[cols.instante])][fila[cols.instante].day][coche_viaje[1]
#                                                                                                                                      ].append(normaliza_fecha(fila[cols.instante]))
#            sentido_viaje = sentido.Sardinero_Valdecilla
#        elif fila[cols.parada] in paradas_a_sardinero:
#            viajes_ordenado[coche_viaje[0]]['Valdecilla_Sardinero'][devuelve_intervalo(fila[cols.instante])][fila[cols.instante].day][coche_viaje[1]
#                                                                                                                                      ].append(normaliza_fecha(fila[cols.instante]))
#        elif fila[cols.parada] in paradas_a_valdecilla:
#            viajes_ordenado[coche_viaje[0]]['Sardinero_Valdecilla'][devuelve_intervalo(fila[cols.instante])][fila[cols.instante].day][coche_viaje[1]
#                                                                                                                                      ].append(normaliza_fecha(fila[cols.instante]))
# filtro para borrar los malos
#
#viajes_ordenado_filtrado = deepcopy(viajes_ordenado)
#
# for key, d1 in viajes_ordenado.items():
#    for sentido, d2 in d1.items():
#        for grupo_hora, d3 in d2.items():
#            for dia, d4 in d3.items():
#                for viaje, lista in d4.items():
#                    if sentido == 'Valdecilla_Sardinero':
#                        if filtro_valdecilla_sardinero(lista):
#                            del viajes_ordenado_filtrado[key][sentido][grupo_hora][dia][viaje]
#                    elif sentido == 'Sardinero_Valdecilla':
#                        if filtro_sardinero_valdecilla(lista):
#                            del viajes_ordenado_filtrado[key][sentido][grupo_hora][dia][viaje]
#
#
# montamos otro diccionario mas cocreto con los distintos df a pintar
# for coche, valores in viajes_ordenado_filtrado.items():
#    if coche != 1:
#        pass
#    for sentido, valores2 in valores.items():
#        if sentido == 'Valdecilla_Sardinero':
#            continue
#        #        inicia_plot = True
#        sentido_opuesto = 'Sardinero_Valdecilla' if sentido == 'Valdecilla_Sardinero' else 'Valdecilla_Sardinero'
#        tamaño = tamaño_correcto_tupla_valde_sardi if sentido == 'Valdecilla_Sardinero' else tamaño_correcto_tupla_sardi_valde
#        tamaño_opuesto = tamaño_correcto_tupla_sardi_valde if sentido == 'Valdecilla_Sardinero' else tamaño_correcto_tupla_valde_sardi
#        nombres = paradas_a_sardinero_nombres if sentido == 'Valdecilla_Sardinero' else paradas_a_valdecilla_nombres
#        nombres_opuesto = paradas_a_valdecilla_nombres if sentido == 'Valdecilla_Sardinero' else paradas_a_sardinero_nombres
#        distancias = distancia_valdecilla_sardinero if sentido == 'Valdecilla_Sardinero' else distancia_sardinero_valdecilla
#        distancias_opuesto = distancia_sardinero_valdecilla if sentido == 'Valdecilla_Sardinero' else distancia_valdecilla_sardinero
#        # hay que dividir los viajes si son muchos para que se pinten en grupos
#        # más pequeños y se vea mejor
#        num_grafica = 0
#        for grupo_hora, valores3 in sorted(
#                valores2.items(), key=operator.itemgetter(0)):
#            inicia_plot = True
#            num_grafica += 1
#            for dia, valores4 in valores3.items():
#
#                df = pd.DataFrame.from_dict(
#                    viajes_ordenado_filtrado[coche][sentido][grupo_hora][dia], orient='columns', dtype=None)
#                df2 = pd.DataFrame.from_dict(
#                    viajes_ordenado_filtrado[coche][sentido_opuesto][grupo_hora][dia], orient='columns', dtype=None)
#                if df.empty or df2.empty:
#                    continue
#                else:
#
#                    color = colores[lista_dias.index(dia)]
#    #                handles.append(str(dia))
#                    df['paradas'] = distancias
#                    df2['paradas'] = list(5000 - x for x in distancias_opuesto)
#                    #df['pasos_parada']=df.apply(tuple, axis=1)
#                    columnas = list(df.columns.values)
#                    columnas_opuesto = list(df2.columns.values)
#        #            ax = df.plot(x=columnas[0], y='paradas',
#        # label='Viaje {}'.format(str(columnas[0])), figsize=(20, 10))
#                    if inicia_plot:
#                        texto_label = f"Dia {dia} viaje {columnas[0]}"
#                        ax = df.plot(x=columnas[0], y='paradas',
#                                     color=color, label=texto_label, figsize=(15, 10))
#                        ax2 = ax.twinx()
#                        texto_label = f"Dia {dia} viaje {columnas_opuesto[0]}"
#                        df2.plot(x=columnas_opuesto[0], y='paradas', ax=ax2,
#                                 color=color, label=texto_label)
#                        inicia_plot = False
#                    else:
#                        texto_label = f"Dia {dia} viaje {columnas[0]}"
#                        df.plot(x=columnas[0], y='paradas',
#                                ax=ax, color=color, label=texto_label)
#                        texto_label = f"Dia {dia} viaje {columnas_opuesto[0]}"
#                        df2.plot(x=columnas_opuesto[0], y='paradas', ax=ax2,
#                                 color=color, label=texto_label)
#                    for viaje in columnas[1:-1]:
#                        texto_label = f"Dia {dia} viaje {viaje}"
#                        df.plot(x=viaje, y='paradas', ax=ax,
#                                color=color, label=texto_label)
#                    for viaje in columnas_opuesto[1:-1]:
#                        texto_label = f"Dia {dia} viaje {viaje}"
#                        df2.plot(x=viaje, y='paradas', ax=ax2,
#                                 color=color, label=texto_label)
# se crea el dibujo para la vuelta en el otro eje
#
#                    ax.set_yticks(distancias)
#                    ax.set_yticklabels(nombres)
#                    ax2.set_yticks(list(5000 - x for x in distancias_opuesto))
#                    ax2.set_yticklabels(nombres_opuesto)
#
#                    titulo = 'Coche {} grafica {}'.format(
#                        str(coche),
#                        str(num_grafica))
#                    ax.set_title(titulo, color='black')
#                    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
#                    ax.set_ylim([0, 5000])
#                    ax2.set_ylim([0, 5000])
#                    ax.legend(loc='center left', bbox_to_anchor=(1.15, 0.5))
#                    lgd = ax2.legend(loc='center left',
#                                     bbox_to_anchor=(1.3, 0.5))
#                    ax.grid()
#                    ax2.grid()
#                    fig = ax.get_figure()
#                    figura_ruta_relativa = 'coche_{}_grafica_{}.png'.format(
#                        str(coche),
#                        str(num_grafica))
#                    figura_ruta = directorio + figura_ruta_relativa
#            fig.savefig(
#                figura_ruta,
#                bbox_extra_artists=(lgd,), bbox_inches='tight')
#
#            cuerpo_informe = "".join((cuerpo_informe,
#                                      textos_html_informe_100.apartado_informe.format(
#                                          titulo=titulo,
#                                          grafico=figura_ruta_relativa)))
#
# una vez obtenidas las gráficas habría que sacar unas tablas de
# desviación media
#columnas = ['sentido', 'coche', 'dia', 'viaje', 'tv', 'v_comercial']
# columnas_mostrar_final = ['coche', 'sentido', 'viaje', 'media tiempo viaje (minutos)',
#                          'media velocidad comercial (km/h)', 'desviación tiempo viaje',
#                          'desviación velocidad comercial']
#df_mean = pd.DataFrame(columns=columnas)
# for coche, valores in viajes_ordenado_filtrado.items():
#    for sentido, valores2 in valores.items():
#        for grupo_hora, valores3 in sorted(
#                valores2.items(), key=operator.itemgetter(0)):
#            for dia, valores4 in valores3.items():
#                for viaje, valores5 in valores4.items():
#                    tv = sorted(valores5)[-1] - sorted(valores5)[0]
#                    v = 3.6 * 4900 / tv.seconds
#                    df_mean.loc[len(df_mean)] = [
#                        sentido, coche, dia, viaje, tv, v]
# creado el df hay que hacer una pivot table para agregar los datos
#
#df_mean['tv_minutes'] = df_mean['tv'].apply(lambda x: x.seconds / 60)
#
# pivot_table = pd.pivot_table(df_mean, values=['v_comercial', 'tv_minutes'],
#                             index=['coche', 'sentido', 'viaje'],
#                             aggfunc=[np.mean, np.std])
# pivot_table.reset_index(inplace=True)
#pivot_table.columns = columnas_mostrar_final
#pivot_table.sort_values(['coche', 'viaje'], inplace=True)
#cwd = os.getcwd()
# pivot_table.to_csv(
#    path_or_buf=cwd + R"\CENTRAL-CSV\{}{}{}_a_{}{}{}.csv".format(dia_inicio.year,
#                                                                 dia_inicio.month,
#                                                                 dia_inicio.day,
#                                                                 dia_fin.year,
#                                                                 dia_fin.month,
#                                                                 dia_fin.day))
# tabla_html = pivot_table.to_html(classes='paleBlueRows',
#                                 columns=columnas_mostrar_final, index=False,
#                                 justify='center')
# se añade al cuerpo del informe
# cuerpo_informe = "".join((cuerpo_informe,
#                          textos_html_informe_100.apartado_informe_tabla.format(
#                              tabla=tabla_html)))
#
# se genera un informe de este tipo
# with open(directorio + 'informe.html', 'w') as file:
#    print(textos_html_informe_100.plantilla_web_estilos +
#          textos_html_informe_100.plantilla_web_cuerpo.format(
#              dia_inicio=dia_inicio.day,
#              dia_fin=dia_fin.day,
#              mes_inicio=mes_letra(dia_inicio.month),
#              mes_fin=mes_letra(dia_fin.month),
#              informe_completo=cuerpo_informe), file=file)
#    create_pdf(
#        directorio + 'informe.html',
#        directorio + 'linea_central_del_{}-{}-{}_al_{}-{}-{}.pdf'.format(dia_inicio.year,
#                                                                         dia_inicio.month,
#                                                                         dia_inicio.day,
#                                                                         dia_fin.year,
#                                                                         dia_fin.month,
# dia_fin.day))
