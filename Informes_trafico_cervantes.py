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
import textos_html_informe_cervantes
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
from scipy.interpolate import interp1d

locale.setlocale(locale.LC_ALL, '')

# VARIABLES
borde_html = "border-bottom:solid windowtext 1.5pt;"
espiras_analizar = (2050, 2049, 2001, 2002, 2003, 2021, 2022, 2044, 2042, 2041)
nombres = (
    'Cisneros',
    'Guevara',
    'Jesús de Monasterio _ San Luís',
    'Jesús de Monasterio _ Jesús de Monasterio',
    'Jesús de Monasterio (edificio ONCE)',
    'Rubio',
    'Isabel la Católica',
    'Isabel II esquina Francisco de Quevedo',
    'Rualasal',
    'Lealtad')

limite_descarga = 1500  # (40000, 40000, 8000) #(7500,7500,1500)

# limite_descarga = (400000,400000,80000)#(40000, 40000, 8000)
# #(7500,7500,1500)

cuerpo_informe = ''

un_minuto = timedelta(minutes=1)

un_dia = timedelta(days=1)

dia_analisis = datetime.now() - un_dia

dia_inicio = dia_analisis.replace(hour=0, minute=0, second=0)
dia_fin = dia_analisis.replace(hour=23, minute=59, second=59)
print(dia_inicio)
print(dia_fin)
input('continuar')

dia_control = dia_inicio
# esto seria recomendable cambiarlo cuando hay bisisestos

lista_dias = []
dias_excluir = (100,)


while dia_control <= dia_fin:
    # SE EXCLUYEN LOS FINES DE SEMANA
    if dia_control.weekday() < 5 and dia_control.day not in dias_excluir:
        lista_dias.append(dia_control.day)
    dia_control += un_dia

columnas = ['n_datos_usados', 'intensidad', 'ocupacion', 'dia', 'hora']

# FUNCIONES


def mes_letra(mes):
    return date(1900, mes, 1).strftime('%B')


# DESCARGA DATOS
descargas_a_realizar = {(dia_inicio, dia_fin): tuple(
    zip(espiras_analizar, repeat(limite_descarga), nombres))}
datos_row = defaultdict(lambda: defaultdict(pd.DataFrame))
for dias, valores in descargas_a_realizar.items():
    dia_inicio = dias[0]
    dia_fin = dias[1]
    for espiras, limite, nombre in valores:
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
                                    espira =  {}
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
                try:
                    exhaust_map(cursor.execute, querie)
                    df = pd.DataFrame(list(cursor), columns=columnas)
                    datos_row[nombre][dia_inicio.year] = df
                    print('datos descargados')
                except Exception:
                    print('no se ha podido descargar ')

# CREAMOS EL DIRECTORIO
directorio = "informe_cervantes_de_{}{}{}\\".format(dia_inicio.year,
                                                    dia_inicio.month,
                                                    dia_inicio.day)
print(directorio)
# archivo = "{}{}{}".format(actual.year,
#                          actual.month,
#                          dia_resta)
if os.path.exists(directorio):
    pass
else:
    os.mkdir(directorio)
copyfile('tabla.css', directorio + 'tabla.css')
# PROCESO DE DATOS
# aqui vamos a crear para cada uno de los dos sentidos dos gráficos, uno
# que sea intensidad ocupación y otro agregando los datos de intensidad
for destino, datos in datos_row.items():
    print(destino)
    try:
        fig_int_oc, ax_int_oc = plt.subplots()
        fig_int_hor, ax_int_hor = plt.subplots()
        fig_oc_hor, ax_oc_hor = plt.subplots()
#        ax_int_oc_list = ax_int_oc.ravel()
        n = 0
        for año, dataframe in datos.items():
            # empezamos con intensidad ocupacion
            dataframe['intensidad'] = dataframe['intensidad'].apply(float)
            dataframe['intensidad'] = dataframe['intensidad'] / 60
            dataframe['ocupacion'] = dataframe['ocupacion'].apply(float)
            dataframe.plot.scatter(
                y='intensidad',
                x='ocupacion',
                ax=ax_int_oc)
            ax_int_oc.set_ylim([0, 2500])
            ax_int_oc.set_xlim([0, 100])
            ax_int_oc.grid()
            ax_int_oc.set_xlabel('Ocupación (%)', fontsize=15)
            ax_int_oc.set_ylabel('Intensidad (veh/hora)', fontsize=15)
            ax_int_oc.set_title(str(año), fontsize=20)
            n += 1
            # hacemos lo propio con los de intensidad horaria
            pivot_table = pd.pivot_table(
                dataframe,
                values=['intensidad'],
                index=['hora'],
                aggfunc=[
                    np.mean])
            pivot_table.reset_index(inplace=True)
            pivot_table.columns = ['Hora', 'Intensidad']
            pivot_table_interpolada = pd.DataFrame()
            # interrpolamos para suaviozar las lineas

            horas = tuple(range(0, 24))
            f1 = interp1d(horas, pivot_table['Intensidad'], kind='cubic')
            pivot_table_interpolada['intensidad_itp'] = f1(horas)
            pivot_table_interpolada['Hora'] = horas
            pivot_table_interpolada.index = horas
            pivot_table_interpolada.plot(
                y='intensidad_itp',
                x='Hora',
                ax=ax_int_hor,
                label=str(año))
            ax_int_hor.set_xlabel('Hora del día', fontsize=15)
            ax_int_hor.set_ylabel('Intensidad (veh/hora)', fontsize=15)
            # hacemos lo propio con los de ocupacion
            pivot_table = pd.pivot_table(
                dataframe,
                values=['ocupacion'],
                index=['hora'],
                aggfunc=[
                    np.mean])
            pivot_table.reset_index(inplace=True)
            pivot_table.columns = ['Hora', 'Ocupacion']
            pivot_table_interpolada = pd.DataFrame()
            # interrpolamos para suaviozar las lineas

            horas = tuple(range(0, 24))
            f1 = interp1d(horas, pivot_table['Ocupacion'], kind='cubic')
            pivot_table_interpolada['ocupacion_itp'] = f1(horas)
            pivot_table_interpolada['Hora'] = horas
            pivot_table_interpolada.index = horas
            pivot_table_interpolada.plot(
                y='ocupacion_itp',
                x='Hora',
                ax=ax_oc_hor)
            ax_oc_hor.set_xlabel('Hora del día', fontsize=15)
            ax_oc_hor.set_ylabel('Ocupación (%/hora)', fontsize=15)

        fig_int_oc.set_size_inches((15, 7))
        figura_ruta_relativa = 'int_ocup_destino_{}.png'.format(
            str(destino))
        figura_ruta = directorio + figura_ruta_relativa
        fig_int_oc.savefig(figura_ruta)
        titulo = 'Gráfico Intensidad Ocupación {}'.format(destino)
        cuerpo_informe = "".join((cuerpo_informe,
                                  textos_html_informe_cervantes.apartado_informe.format(
                                      borde="",
                                      titulo=titulo,
                                      grafico=figura_ruta_relativa)))
        # guardamos el otro grafico tambien

        fig_int_hor.set_size_inches((15, 7))
        figura_ruta_relativa = 'int_horaria_destino_{}.png'.format(
            str(destino))
        figura_ruta = directorio + figura_ruta_relativa
        fig_int_hor.savefig(figura_ruta, bbox_inches='tight')
        cuerpo_informe = "".join((cuerpo_informe,
                                  textos_html_informe_cervantes.apartado_informe.format(
                                      borde="",
                                      titulo=titulo,
                                      grafico=figura_ruta_relativa)))
        # guardamos el grafico de ocupacion horaria
        
        fig_oc_hor.set_size_inches((15, 7))
        figura_ruta_relativa = 'oc_horaria_destino_{}.png'.format(
            str(destino))
        figura_ruta = directorio + figura_ruta_relativa
        fig_oc_hor.savefig(figura_ruta, bbox_inches='tight')
        titulo = 'Gráfico Ocupación Horaria {}'.format(destino)
        cuerpo_informe = "".join((cuerpo_informe,
                                  textos_html_informe_cervantes.apartado_informe.format(
                                      borde=borde_html,
                                      titulo=titulo,
                                      grafico=figura_ruta_relativa)))
        print(destino)
    except Exception as e:
        raise
        print('ERROR')


# SALVADO DEL INFORME
# se añade al cuerpo del informe
cuerpo_informe = "".join((cuerpo_informe,
                          textos_html_informe_cervantes.apartado_informe_tabla.format(
                              tabla='')))

# se genera un informe de este tipo
with open(directorio + 'informe.html', 'w') as file:
    print(textos_html_informe_cervantes.plantilla_web_estilos +
          textos_html_informe_cervantes.plantilla_web_cuerpo.format(
              dia_inicio=dia_inicio.day,
              mes_inicio=mes_letra(dia_inicio.month),
              informe_completo=cuerpo_informe), file=file)
create_pdf(
    directorio + 'informe.html',
    directorio + "informe_cervantes_de_{}{}{}.pdf".format(dia_inicio.year,
                                                          dia_inicio.month,
                                                          dia_inicio.day))
