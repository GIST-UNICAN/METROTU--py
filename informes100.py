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

# necesitamos traer de la db los datos de la linea 100
actual = datetime.now()
dia_resta = 2
un_minuto = timedelta(minutes=1)
querie = ("SELECT * FROM autobuses.pasos_parada  where linea=100 "
          "and fecha='{}-{}-{}'order by coche, viaje").format(actual.year,
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
        cursor.execute(querie_cabeceras)
        datos_row_cabeceras = tuple(cursor) 

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
paradas_a_valdecilla = (paradas.Int_Sardinero_1, paradas.Vega_Lamera,
                        paradas.Casimiro_Sainz_15, paradas.Paseo_Pereda,
                        paradas.Correos, paradas.Pza_Ayto,
                        paradas.San_Fernando_22, paradas.Avenida_Valdecilla)

Columnas = namedtuple("Columnas",
                      ("linea",
                       "coche",
                       "viaje",
                       "parada",
                       "instante",
                       "nombre"))
cols = Columnas(*range(6))

viajes_ordenado = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

#si la parada es alguna de las de las cabeceras vamos a usar la consulta de la otra db
for coche_viaje, rows in groupby(datos_row, lambda fila: (fila[cols.coche],
                                                          fila[cols.viaje])):
    Sentido = namedtuple(
        "Sentido", ("Valdecilla_Sardinero", 'Sardinero_Valdecilla'))
    sentido = Sentido(*range(2))
    sentido_viaje = ''
    for fila in rows:
        if fila[cols.parada] == paradas.Valdecilla:
            viajes_ordenado[coche_viaje[0]][coche_viaje[1]
                                            ]['Valdecilla_Sardinero'].append(fila[cols.instante])
            sentido_viaje = sentido.Valdecilla_Sardinero
        elif fila[cols.parada] == paradas.Int_Sardinero:
            viajes_ordenado[coche_viaje[0]][coche_viaje[1]
                                            ]['Sardinero_Valdecilla'].append(fila[cols.instante])
            sentido_viaje = sentido.Sardinero_Valdecilla
        elif fila[cols.parada] in paradas_a_sardinero:
            viajes_ordenado[coche_viaje[0]][coche_viaje[1]
                                            ]['Valdecilla_Sardinero'].append(fila[cols.instante])
        elif fila[cols.parada] in paradas_a_valdecilla:
            viajes_ordenado[coche_viaje[0]][coche_viaje[1]
                                            ]['Sardinero_Valdecilla'].append(fila[cols.instante])

