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
import matplotlib.pyplot as plt
from shutil import copyfile
from pdfkit import from_file as create_pdf
import contextlib
from copy import deepcopy
import matplotlib.pyplot as plt

# necesitamos traer de la db los datos de la linea 100
actual = datetime.now()
dia_resta = 3
un_minuto = timedelta(minutes=1)

tamaño_correcto_tupla_valde_sardi = 9
tamaño_correcto_tupla_sardi_valde = 8

querie = ("SELECT pp.Coche, pp.Viaje, pp.Parada, COALESCE(ppa.Instante, "
          "pp.Instante) as Instante FROM autobuses.pasos_parada pp  left join "
          "autobuses.pasos_parada_ajustada ppa on pp.Coche=ppa.Coche and "
          "ppa.Viaje=pp.Viaje and ppa.Linea=pp.Linea and ppa.Fecha=pp.fecha "
          "and pp.Parada=ppa.Parada where pp.linea=100 and pp.fecha='{}-{}-{}' "
          "order by pp.coche, pp.viaje, pp.Instante").format(actual.year,
                                                             actual.month,
                                                             actual.day-dia_resta)
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


def filtro_valdecilla_sardinero(clave_lista,
                                tamaño_correcto_tupla_valde_sardi=tamaño_correcto_tupla_valde_sardi):
    return tamaño_correcto_tupla_valde_sardi != len(clave_lista[1])


def filtro_sardinero_valdecilla(clave_lista,
                                tamaño_correcto_tupla_sardi_valde=tamaño_correcto_tupla_sardi_valde):
    return tamaño_correcto_tupla_sardi_valde != len(clave_lista[1])


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
        cursor.execute(querie)
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
paradas_a_valdecilla_nombres = ("","Int_Sardinero_1",
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

viajes_ordenado = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

# si la parada es alguna de las de las cabeceras vamos a usar la consulta de la otra db
for coche_viaje, rows in groupby(datos_row, lambda fila: (fila[cols.coche],
                                                          fila[cols.viaje])):
    Sentido = namedtuple(
        "Sentido", ("Valdecilla_Sardinero", 'Sardinero_Valdecilla'))
    sentido = Sentido(*range(2))
    sentido_viaje = ''
    for fila in rows:
        if fila[cols.parada] == paradas.Valdecilla:
            viajes_ordenado[coche_viaje[0]]['Valdecilla_Sardinero'][coche_viaje[1]
                                                                    ].append(fila[cols.instante])
            sentido_viaje = sentido.Valdecilla_Sardinero
        elif fila[cols.parada] == paradas.Int_Sardinero_1:
            viajes_ordenado[coche_viaje[0]]['Sardinero_Valdecilla'][coche_viaje[1]
                                                                    ].append(fila[cols.instante])
            sentido_viaje = sentido.Sardinero_Valdecilla
        elif fila[cols.parada] in paradas_a_sardinero:
            viajes_ordenado[coche_viaje[0]]['Valdecilla_Sardinero'][coche_viaje[1]
                                                                    ].append(fila[cols.instante])
        elif fila[cols.parada] in paradas_a_valdecilla:
            viajes_ordenado[coche_viaje[0]]['Sardinero_Valdecilla'][coche_viaje[1]
                                                                    ].append(fila[cols.instante])
# filtro para borrar los malos

viajes_ordenado_filtrado = deepcopy(viajes_ordenado)
for key, d1 in viajes_ordenado.items():
    for d2 in filter(filtro_valdecilla_sardinero, d1['Valdecilla_Sardinero'].items()):
        del viajes_ordenado_filtrado[key]['Valdecilla_Sardinero'][d2[0]]

    for d2 in filter(filtro_sardinero_valdecilla, d1['Sardinero_Valdecilla'].items()):
        del viajes_ordenado_filtrado[key]['Sardinero_Valdecilla'][d2[0]]

# montamos otro diccionario mas cocreto con los distintos df a pintar
for coche, valores in viajes_ordenado_filtrado.items():
    for sentido, valores2 in valores.items():
        tamaño = tamaño_correcto_tupla_valde_sardi if sentido == 'Valdecilla_Sardinero' else tamaño_correcto_tupla_sardi_valde
        nombres = paradas_a_sardinero_nombres if sentido == 'Valdecilla_Sardinero' else paradas_a_valdecilla_nombres
        df = pd.DataFrame.from_dict(
            viajes_ordenado_filtrado[coche][sentido], orient='columns', dtype=None)
        df['paradas'] = list(range(tamaño))
        #df['pasos_parada']=df.apply(tuple, axis=1)
        columnas = list(df.columns.values)
        ax = df.plot(x=columnas[0], y='paradas',
                     label='Viaje {}'.format(str(columnas[0])), figsize=(20,10))
        for viaje in columnas[1:-1]:
            df.plot(x=viaje, y='paradas', ax=ax,
                    label='Viaje {}'.format(str(viaje)))
        ax.set_yticklabels(nombres)
        ax.legend(loc='center left', bbox_to_anchor=(1.0, 0.5))
        titulo='Coche {} sentido {}'.format(str(coche), sentido)
        ax.set_title(titulo, color='black')
        fig = ax.get_figure()
        fig.savefig(directorio+'coche_{}_sentido_{}.png'.format(str(coche),sentido))
