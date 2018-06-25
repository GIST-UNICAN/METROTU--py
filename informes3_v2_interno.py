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
limites_outlayers = (-10, 10)



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
    """SELECT ppa.viaje, ppa.coche, ppa.instante, pti.HoraTeorica, pti.Nodo, TIMESTAMPDIFF(second,pti.HoraTeorica,ppa.instante) as diferencia from pasos_teoricos_intercambiadores  pti
inner join (Select * from pasos_parada_ajustada where linea=3 and parada =509 and Instante between @fecha_ini and @fecha_fin) ppa
on ppa.Parada=pti.Nodo and ppa.coche=pti.Coche and ppa.viaje=pti.viaje  and year(ppa.instante)=year(pti.Horateorica) and month(ppa.instante)=month(pti.Horateorica) and day(ppa.instante)=day(pti.Horateorica)
where HoraTeorica between @fecha_ini and @fecha_fin
order by pti.Nodo,pti.HoraTeorica asc""")


directorio = "informe_l3_medias_llegadas_de_{}{}{}_a_{}{}{}\\".format(dia_inicio.year,
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
           "m",
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


def formatea_fecha(pandas_datetime):
    dt = pandas_datetime.to_pydatetime()
    return datetime.strftime(dt, '%H:%M:%S')


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

# generamos el diccionario con los viajes y el desvio segun la hora
diccionario_dia_viajes = defaultdict(
    lambda: defaultdict(
        lambda: defaultdict(
            pd.DataFrame)))
for dia_intercambiador, rows in groupby(
        datos_row, lambda fila: (fila[cols.real].day, fila[cols.nodo])):
    for fila in rows:
        if dia_intercambiador[0] in lista_dias:
            df = pd.DataFrame([list(fila), ], columns=columnas)
            # normalizamos la hora teorica para el pintado
            df['hora_normalizada'] = df['teorica'].apply(normaliza_fecha)
            df['diferencia'] = df['diferencia'] / 60
            # se añade al dataframe o se genera un dataframe nuevo para cada
            # intervalo horario
            if diccionario_dia_viajes[dia_intercambiador[1]
                                      ][devuelve_intervalo(fila[cols.teorica])][dia_intercambiador[0]].shape[0] == 0:
                diccionario_dia_viajes[dia_intercambiador[1]
                                       ][devuelve_intervalo(fila[cols.teorica])][dia_intercambiador[0]] = df
            else:
                df1 = diccionario_dia_viajes[dia_intercambiador[1]
                                             ][devuelve_intervalo(fila[cols.teorica])][dia_intercambiador[0]]
                df2 = df1.append(df)
                diccionario_dia_viajes[dia_intercambiador[1]
                                       ][devuelve_intervalo(fila[cols.teorica])][dia_intercambiador[0]] = df2


# generado un diccionario con el desvio de cada servicio vamos a proceder
# a pintarlo
for cabecera, elementos in diccionario_dia_viajes.items():
    cabecera_nombre = 'Sardinero' if cabecera == 516 else 'Valdecilla'
    for grupo_horario, elementos1 in elementos.items():
        fig, ax = plt.subplots()

        for dia, elementos2 in elementos1.items():
            df3 = elementos2
            # se quitan los datos anomalos
            df3 = df3[(df3.diferencia >= limites_outlayers[0]) &
                      (df3.diferencia <= limites_outlayers[1])]
            hora = df3['hora_normalizada'].tolist()
            hora1 = [x.to_pydatetime() for x in hora]
            values = df3['diferencia'].tolist()
            color = colores[lista_dias.index(dia)]
            ax.plot_date(hora1, values,
                         label='Día {}'.format(str(dia)), color=color)
            ax.plot(hora1, values, color=color)
            ax.set_ylim([-10, 10])
            ax.grid()
            ax.axhline(0, color='k')
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        titulo = 'Llegadas L. 3 a la cabecera {}'.format(cabecera_nombre)
        fig.suptitle(titulo, fontsize=20)
        ax.set_xlabel('Hora', fontsize=15)
        ax.set_ylabel('Adelanto / Retraso (Minutos)', fontsize=15)
        ax.legend(loc='center left', bbox_to_anchor=(1.15, 0.5))
        fig.set_size_inches((20, 10))
        fig.autofmt_xdate()
        figura_ruta_relativa = 'cabecera_{}_grafica_{}.png'.format(
            str(cabecera),
            str(grupo_horario))
        figura_ruta = directorio + figura_ruta_relativa
        ax.legend(
            loc='center left',
            bbox_to_anchor=(
                1,
                0.5),
            prop={
                'size': 15})
        fig.savefig(
            figura_ruta,
            bbox_inches='tight')
        cuerpo_informe = "".join((cuerpo_informe,
                                  textos_html_informe_100.apartado_informe.format(
                                      titulo=titulo,
                                      grafico=figura_ruta_relativa)))

# una vez obtenidas las gráficas habría que sacar unas tablas de
# desviación media
columnas = [
    'Cabecera',
    'Coche',
    'Viaje',
    'Dia',
    'Diferencia',
    'Hora_Normalizada']  # , 'Desvio', 'Desvmed']
columnas_mostrar_final = [
    'Intercambiador',
    'Coche',
    'Viaje',
    'Hora Llegada Teórica',
    'Desvio medio (minutos)']
dic_medias = defaultdict(list)
df_global = pd.DataFrame(columns=columnas)
for cabecera, elementos in diccionario_dia_viajes.items():
    cabecera_nombre = 'Sardinero' if cabecera == 516 else 'Valdecilla'
    for grupo_horario, elementos1 in elementos.items():
        for dia, elementos2 in elementos1.items():
            for coche, viaje, diferencia, hora_normalizada in zip(
                    elementos2.coche, elementos2.viaje, elementos2.diferencia, elementos2.hora_normalizada):
                # se filtran los valores fuerw de rango
                if limites_outlayers[0] <= diferencia <= limites_outlayers[1]:
                    df_global.loc[len(df_global)] = [
                        cabecera_nombre, coche, viaje, dia, diferencia, hora_normalizada]

# creado el df hay que hacer una pivot table para agregar los datos
pivot_table = pd.pivot_table(
    df_global, values=['Diferencia'], index=[
        'Cabecera', 'Coche', 'Viaje', 'Hora_Normalizada'], aggfunc=[
            np.mean])
pivot_table.reset_index(inplace=True)
pivot_table.columns = columnas_mostrar_final
pivot_table.sort_values(by=['Intercambiador', 'Hora Llegada Teórica'], inplace=True)
cwd = os.getcwd()
pivot_table.to_csv(
    path_or_buf=cwd + R"\CENTRAL-CSV-DESVIO\{}{}{}_a_{}{}{}.csv".format(dia_inicio.year,
                                                                        dia_inicio.month,
                                                                        dia_inicio.day,
                                                                        dia_fin.year,
                                                                        dia_fin.month,
                                                                        dia_fin.day))

# para dar formato a la fecha
formateadores = [None, None, None, formatea_fecha, None]
tabla_html = pivot_table.to_html(classes='paleBlueRows',
                                 columns=columnas_mostrar_final, index=False,
                                 justify='center',
                                 formatters=formateadores)
# se añade al cuerpo del informe
cuerpo_informe = "".join((cuerpo_informe,
                          textos_html_informe_100.apartado_informe_tabla.format(
                              tabla=tabla_html)))

# se genera un informe de este tipo
with open(directorio + 'informe.html', 'w') as file:
    print(textos_html_informe_100.plantilla_web_estilos +
          textos_html_informe_100.plantilla_web_cuerpo.format(
              dia_inicio=dia_inicio.day,
              dia_fin=dia_fin.day,
              mes_inicio=mes_letra(dia_inicio.month),
              mes_fin=mes_letra(dia_fin.month),
              informe_completo=cuerpo_informe), file=file)
create_pdf(
    directorio + 'informe.html',
    directorio + 'linea_3_desvios_del_{}-{}-{}_al_{}-{}-{}.pdf'.format(dia_inicio.year,
                                                                     dia_inicio.month,
                                                                     dia_inicio.day,
                                                                     dia_fin.year,
                                                                     dia_fin.month,
                                                                     dia_fin.day))
