# -*- coding: utf-8 -*-
"""
Created on Thu Apr 26 10:09:27 2018

@author: Andres
"""
import MySQLdb
from datetime import datetime, timedelta
import os
from tools import exhaust_map
from collections import namedtuple, defaultdict, OrderedDict
from itertools import starmap, groupby, chain, repeat
import pandas as pd
import numpy as np
from functools import reduce
import textos_html_informe
import matplotlib
matplotlib.use('Agg')
#import matplotlib.pyplot as plt
from shutil import copyfile
from pdfkit import from_file as create_pdf
import contextlib
from copy import deepcopy
import matplotlib.pyplot as plt
from bisect import bisect

# necesitamos traer de la db los datos de la linea 100
actual = datetime.now()
dia_resta = 3
dia_inicio = actual-timedelta(days=(dia_resta+5))
dia_fin = actual-timedelta(days=dia_resta)
un_minuto = timedelta(minutes=1)

tamaño_correcto_tupla_valde_sardi = 9
tamaño_correcto_tupla_sardi_valde = 8

lista_dias = (23, 24, 25, 26, 27)

intervalos_horarios=(0,6,9,12,15,18,21,24)

querie = ("create temporary table t1 as (select * from pasos_parada where "
          " fecha between '{0}-{1}-{2}' and '{3}-{4}-{5}' and linea=100) ".format(
              dia_inicio.year,
              dia_inicio.month,
              dia_inicio.day,
              dia_fin.year,
              dia_fin.month,
              dia_fin.day),
          "create temporary table t2 as (select * from pasos_parada_ajustada "
          "where fecha between '{0}-{1}-{2}' and '{3}-{4}-{5}' and linea=100)".format(
              dia_inicio.year,
              dia_inicio.month,
              dia_inicio.day,
              dia_fin.year,
              dia_fin.month,
              dia_fin.day),
          "SELECT pp.Coche, pp.Viaje, pp.Parada, COALESCE(ppa.Instante, "
          "pp.Instante) as Instante FROM t1 pp  left join "
          "t2 ppa on pp.Coche=ppa.Coche and "
          "ppa.Viaje=pp.Viaje and ppa.Linea=pp.Linea and ppa.Fecha=pp.fecha "
          "and pp.Parada=ppa.Parada where pp.linea=100 and pp.fecha between "
          "'{0}-{1}-{2}' and '{3}-{4}-{5}' and DAYOFWEEK(pp.fecha) not in (1,7) "
          "order by pp.coche, pp.viaje, pp.Instante".format(dia_inicio.year,
                                                            dia_inicio.month,
                                                            dia_inicio.day,
                                                            dia_fin.year,
                                                            dia_fin.month,
                                                            dia_fin.day))
querie_cabeceras = ("SELECT coche, viaje, Parada, Instante from "
                    "autobuses.pasos_parada_ajustada where linea=100 "
                    "and parada in (512,509,511,516) and fecha='{}-{}-{}' "
                    "order by coche, viaje ").format(actual.year,
                                                     actual.month,
                                                     actual.day-dia_resta)
directorio = "informe_lcentral_{}{}{}/".format(actual.year,
                                               actual.month,
                                               actual.day-dia_resta)
archivo = "{}{}{}".format(actual.year,
                          actual.month,
                          actual.day-dia_resta)

colores=("b",
                                                       "g",
                                                       "r",
                                                       "c",
                                                       "g",
                                                       "m",
                                                       "y",
                                                       "k")

def filtro_valdecilla_sardinero(clave_lista,
                                tamaño_correcto_tupla_valde_sardi=tamaño_correcto_tupla_valde_sardi):
    return tamaño_correcto_tupla_valde_sardi != len(clave_lista[1])


def filtro_sardinero_valdecilla(clave_lista,
                                tamaño_correcto_tupla_sardi_valde=tamaño_correcto_tupla_sardi_valde):
    return tamaño_correcto_tupla_sardi_valde != len(clave_lista[1])

def normaliza_fecha(fecha):
    return datetime(2000,1,1,fecha.hour,fecha.minute,fecha.second)

def devuelve_intervalo(datetime, intervalos_horarios=intervalos_horarios):
    return bisect(intervalos_horarios,datetime.hour)


if os.path.exists(directorio):
    pass
else:
    os.mkdir(directorio)
copyfile('tabla.css', directorio+'tabla.css')

with contextlib.closing(MySQLdb.connect(user='root',
                                        password='madremia902',
                                        host='193.144.208.142',
                                        port=3306,
                                        database='autobuses'
                                        )) as conexion:
    with contextlib.closing(conexion.cursor()) as cursor:
        exhaust_map(cursor.execute, querie)
        datos_row = tuple(cursor)


Paradas = namedtuple("Paradas", ("Avenida_Valdecilla", "Valdecilla",
                                 "San_Fernando", "Jesus_Monasterio_7",
                                 "Correos_plaza", "Jardines_Pereda",
                                 "Puerto_Chico", "Casimiro_Sainz_6", "Ies_Llamas",
                                 "Int_Sardinero", "Int_Sardinero_1",
                                 "Vega_Lamera", "Casimiro_Sainz_15",
                                 "Paseo_Pereda", "Correos", "Pza_Ayto",
                                 "San_Fernando_22"))

paradas = Paradas(Avenida_Valdecilla=512, Valdecilla=509,
                  San_Fernando=11, Jesus_Monasterio_7=510,
                  Correos_plaza=14, Jardines_Pereda=15,
                  Puerto_Chico=16, Casimiro_Sainz_6=261, Ies_Llamas=194,
                  Int_Sardinero=516, Int_Sardinero_1=511,
                  Vega_Lamera=171, Casimiro_Sainz_15=76,
                  Paseo_Pereda=39, Correos=40, Pza_Ayto=41,
                  San_Fernando_22=43)

paradas_a_sardinero = (paradas.Valdecilla, paradas.San_Fernando,
                       paradas.Jesus_Monasterio_7, paradas.Correos_plaza,
                       paradas.Jardines_Pereda, paradas.Puerto_Chico,
                       paradas.Casimiro_Sainz_6,
                       paradas.Ies_Llamas, paradas.Int_Sardinero)

paradas_a_sardinero_nombres = ("", "Valdecilla",
                               "San_Fernando", "Jesus_Monasterio_7",
                               "Correos_plaza", "Jardines_Pereda",
                               "Puerto_Chico", "Casimiro_Sainz_6", "Ies_Llamas",
                               "Int_Sardinero")
paradas_a_valdecilla_nombres = ("", "Int_Sardinero_1",
                                "Vega_Lamera", "Casimiro_Sainz_15",
                                "Paseo_Pereda", "Correos", "Pza_Ayto",
                                "San_Fernando_22", "Avenida_Valdecilla")

paradas_a_valdecilla = (paradas.Int_Sardinero_1, paradas.Vega_Lamera,
                        paradas.Casimiro_Sainz_15, paradas.Paseo_Pereda,
                        paradas.Correos, paradas.Pza_Ayto,
                        paradas.San_Fernando_22, paradas.Avenida_Valdecilla)

Columnas = namedtuple("Columnas",
                      ("coche",
                       "viaje",
                       "parada",
                       "instante"))
cols = Columnas(*range(4))

viajes_ordenado = defaultdict(lambda: defaultdict(
    lambda:  defaultdict(lambda: defaultdict (lambda: defaultdict(list)))))

# si la parada es alguna de las de las cabeceras vamos a usar la consulta de la otra db
for coche_viaje, rows in groupby(datos_row, lambda fila: (fila[cols.coche],
                                                          fila[cols.viaje])):
    Sentido = namedtuple(
        "Sentido", ("Valdecilla_Sardinero", 'Sardinero_Valdecilla'))
    sentido = Sentido(*range(2))
    sentido_viaje = ''
    for fila in rows:
        if fila[cols.parada] == paradas.Valdecilla:
            viajes_ordenado[coche_viaje[0]]['Valdecilla_Sardinero'][fila[cols.instante].day][devuelve_intervalo(fila[cols.instante])][coche_viaje[1]
                                                                                             ].append(normaliza_fecha(fila[cols.instante]))
            sentido_viaje = sentido.Valdecilla_Sardinero
        elif fila[cols.parada] == paradas.Int_Sardinero_1:
            viajes_ordenado[coche_viaje[0]]['Sardinero_Valdecilla'][fila[cols.instante].day][devuelve_intervalo(fila[cols.instante])][coche_viaje[1]
                                                                                             ].append(normaliza_fecha(fila[cols.instante]))
            sentido_viaje = sentido.Sardinero_Valdecilla
        elif fila[cols.parada] in paradas_a_sardinero:
            viajes_ordenado[coche_viaje[0]]['Valdecilla_Sardinero'][fila[cols.instante].day][devuelve_intervalo(fila[cols.instante])][coche_viaje[1]
                                                                                             ].append(normaliza_fecha(fila[cols.instante]))
        elif fila[cols.parada] in paradas_a_valdecilla:
            viajes_ordenado[coche_viaje[0]]['Sardinero_Valdecilla'][fila[cols.instante].day][devuelve_intervalo(fila[cols.instante])][coche_viaje[1]
                                                                                             ].append(normaliza_fecha(fila[cols.instante]))
# filtro para borrar los malos

viajes_ordenado_filtrado = deepcopy(viajes_ordenado)

for key, d1 in viajes_ordenado.items():
    for dia in lista_dias:
        
        for d2 in filter(filtro_valdecilla_sardinero, d1['Valdecilla_Sardinero'][dia].items()):
            del viajes_ordenado_filtrado[key]['Valdecilla_Sardinero'][dia][d2[0]]
        for d2 in filter(filtro_sardinero_valdecilla, d1['Sardinero_Valdecilla'][dia].items()):
            del viajes_ordenado_filtrado[key]['Sardinero_Valdecilla'][dia][d2[0]]
        if len(d1['Sardinero_Valdecilla'][dia].items()) == 0:
            del viajes_ordenado_filtrado[key]['Sardinero_Valdecilla'][dia]
        if len(d1['Valdecilla_Sardinero'][dia].items()) == 0:
            del viajes_ordenado_filtrado[key]['Valdecilla_Sardinero'][dia]


# montamos otro diccionario mas cocreto con los distintos df a pintar
for coche, valores in viajes_ordenado_filtrado.items():
    if coche != 1:
        continue
    for sentido, valores2 in valores.items():

        tamaño = tamaño_correcto_tupla_valde_sardi if sentido == 'Valdecilla_Sardinero' else tamaño_correcto_tupla_sardi_valde
        nombres = paradas_a_sardinero_nombres if sentido == 'Valdecilla_Sardinero' else paradas_a_valdecilla_nombres
        inicia_plot=True
        #hay que dividir los viajes si son muchos para que se pinten en grupos más pequeños y se vea mejor
        for dia in lista_dias:
            
            df = pd.DataFrame.from_dict(
                viajes_ordenado_filtrado[coche][sentido][dia], orient='columns', dtype=None)
            if df.empty:
                continue
            else:
                color=colores[lista_dias.index(dia)]
#                handles.append(str(dia))
                df['paradas'] = list(range(tamaño))
                df2 = df
                #df['pasos_parada']=df.apply(tuple, axis=1)
                columnas = list(df.columns.values)
    #            ax = df.plot(x=columnas[0], y='paradas',
    #                         label='Viaje {}'.format(str(columnas[0])), figsize=(20, 10))
                if inicia_plot:
                    ax = df.plot(x=columnas[0], y='paradas', color=color, legend=False)
                    inicia_plot=False
                else:
                    handles.append(df.plot(x=columnas[0], y='paradas', ax=ax, color=color,  legend=False))
                for viaje in columnas[1:-1]:
                    df.plot(x=viaje, y='paradas', ax=ax, color=color, legend=False)
                ax.set_yticklabels(nombres)
                ax.legend(loc='center left', bbox_to_anchor=(1.0, 0.5))
                titulo = 'Coche {} sentido {}'.format(str(coche), sentido)
                ax.set_title(titulo, color='black')
                fig = ax.get_figure()
                fig.savefig(
                    directorio+'coche_{}_sentido_{}.png'.format(str(coche), sentido))
