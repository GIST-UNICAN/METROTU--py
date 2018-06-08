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
# import matplotlib.pyplot as plt
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

locale.setlocale(locale.LC_ALL, '')

# VARIABLES
espiras_dir_valdecilla = (2036, 2028, 2046, 2013, 1035)
espiras_dir_sardinero = (2035, 2043, 2019, 2075, 1034)
espira_cajo = (2002,)
limite_descarga = (40000, 40000, 8000) #(7500,7500,1500)
nombres=('Sardinero - Valdecilla', 'Valdecilla - Sardinero', 'Cajo')
cuerpo_informe = ''

actual = datetime.now()
dia_resta = 1
dia_inicio = actual - timedelta(days=(dia_resta + 6))
dia_fin = actual - timedelta(days=dia_resta)
un_minuto = timedelta(minutes=1)
dia_control = dia_inicio
un_dia = timedelta(days=1)
# esto seria recomendable cambiarlo cuando hay bisisestos
un_año = timedelta(days=366)
lista_dias = []
dias_excluir = (100,)
dia_inicio_anterior = dia_inicio - un_año
dia_fin_anterior = dia_fin - un_año
while dia_control <= dia_fin:
    # SE EXCLUYEN LOS FINES DE SEMANA
    if dia_control.weekday() < 5 and dia_control.day not in dias_excluir:
        lista_dias.append(dia_control.day)
    dia_control += un_dia

columnas=['n_datos_usados','intensidad', 'ocupacion', 'dia','hora']

# FUNCIONES


# DESCARGA DATOS
descargas_a_realizar = {(dia_inicio, dia_fin): tuple(zip((espiras_dir_valdecilla, espiras_dir_sardinero, espira_cajo), limite_descarga, nombres)),
                        (dia_inicio_anterior, dia_fin_anterior): tuple(zip((espiras_dir_valdecilla, espiras_dir_sardinero, espira_cajo), limite_descarga, nombres))}
datos_row=defaultdict(lambda: defaultdict(pd.DataFrame))
for dias, valores in descargas_a_realizar.items():
    dia_inicio = dias[0]
    dia_fin = dias[1]
    for espiras, limite, nombre in valores:
        espiras= espiras if len(espiras)>1 else f'({espiras[0]})'
        querie = ("set @fecha_ini='{}-{}-{} 00:00:00'".format(dia_inicio.year,
                                                              dia_inicio.month,
                                                              dia_inicio.day),
                  "set @fecha_fin = '{}-{}-{} 23:59:59'".format(dia_fin.year,
                                                                dia_fin.month,
                                                                dia_fin.day),
                  """SELECT
                            
                        	count(intensidad) as datos_usados,
                            AVG(intensidad) AS intensidad_media,
                            AVG(ocupacion) AS ocupacion_media,
                            weekday(fecha) as dia,
                            HOUR(fecha) AS hora
                        FROM
                                        (SELECT
                                       intensidad,
                                       ocupacion,
                                       fecha,
                                       espira
                             FROM
                                (SELECT
                                    intensidad,
                                    ocupacion,
                                    fecha,
                                       espira
                                FROM
                                    lecturas_espiras
                                    FORCE INDEX (fecha, espira)
                                WHERE
                                    fecha > @fecha_ini
                                    and
                                    weekday(fecha) not  in (6,5)
                                    and
                                    espira in  {}
                                ORDER BY
                                    fecha
                                ASC
                                LIMIT
                                    {}
                                )
                            corte_inferior
                                        WHERE
                                       fecha < @fecha_fin)
                                        corte_temporal_completo
                        WHERE
                                        1=1
                        GROUP BY
                                        dia,Hora""".format(espiras, limite))
        
        with contextlib.closing(MySQLdb.connect(user='root',
                                                password='madremia902',
                                                host='193.144.208.142',
                                                port=3306,
                                                database='Trafico_Santander'
                                                )) as conexion:
            with contextlib.closing(conexion.cursor()) as cursor:
                exhaust_map(cursor.execute, querie)
                datos_row[nombre][dia_inicio.year] = pd.DataFrame(list(cursor), columns=columnas)
                print('datos descargados')
                
# PROCESO DE DATOS

# CONSTRUCCIÓN DEL INFORME

# SALVADO DEL INFORME
