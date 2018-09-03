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
matplotlib.use('Agg')
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
dia_resta = 2
dia_inicio = actual-timedelta(days=(dia_resta+6))
dia_fin = actual-timedelta(days=dia_resta)
un_minuto = timedelta(minutes=1)

tamaño_correcto_tupla_valde_sardi = 9
tamaño_correcto_tupla_sardi_valde = 8

dia_control = dia_inicio
un_dia = timedelta(days=1)
lista_dias = []
dias_excluir=(30,)
while dia_control <= dia_fin:
    if dia_control.weekday() < 5 and dia_control.day not in dias_excluir:
        lista_dias.append(dia_control.day)
    dia_control += un_dia

print(lista_dias)
intervalos_horarios = (0, 6, 9, 12, 15, 18, 21, 24)
#intervalos_horarios = (0, 24)

distancia_valdecilla_sardinero = (
    0, 900, 2000, 2350, 2600, 3050, 3350, 4400, 5000)
distancia_sardinero_valdecilla = (0, 800, 1900, 2400, 2750, 3050, 3950, 5000)

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
directorio = "informe_lcentral_de_{}{}{}_a_{}{}{}\\".format(dia_inicio.year,
                                                            dia_inicio.month,
                                                            dia_inicio.day,
                                                            dia_fin.year,
                                                            dia_fin.month,
                                                            dia_fin.day)
archivo = "{}{}{}".format(actual.year,
                          actual.month,
                          actual.day-dia_resta)

colores = ("b",
           "g",
           "r",
           "c",
           "g",
           "m",
           "y",
           "k")


def filtro_valdecilla_sardinero(clave_lista,
                                tamaño_correcto_tupla_valde_sardi=tamaño_correcto_tupla_valde_sardi):
    return (tamaño_correcto_tupla_valde_sardi != len(clave_lista)
            # Comprobamos que la lista sea creciente.
            or any(a >= b for a, b in zip(clave_lista[:-1], clave_lista[1:])))


def filtro_sardinero_valdecilla(clave_lista,
                                tamaño_correcto_tupla_sardi_valde=tamaño_correcto_tupla_sardi_valde):
    return (tamaño_correcto_tupla_sardi_valde != len(clave_lista)
            or any(a >= b for a, b in zip(clave_lista[:-1], clave_lista[1:])))


def normaliza_fecha(fecha):
    return datetime(2000, 1, 1, fecha.hour, fecha.minute, fecha.second)


def devuelve_intervalo(datetime, intervalos_horarios=intervalos_horarios):
    return bisect(intervalos_horarios, datetime.hour)


def mes_letra(mes):
    return date(1900, mes, 1).strftime('%B')


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

paradas_a_sardinero_nombres = ("Valdecilla",
                               "San_Fernando", "Jesus_Monasterio_7",
                               "Correos_plaza", "Jardines_Pereda",
                               "Puerto_Chico", "Casimiro_Sainz_6", "Ies_Llamas",
                               "Int_Sardinero")
paradas_a_valdecilla_nombres = ("Int_Sardinero_1",
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

# viajes_ordenado[coche][sentido][intervalo][dia][viaje] = [instante_0,
#                                                           instante_1...]
viajes_ordenado = defaultdict(
        lambda: defaultdict(
                lambda: defaultdict(
                        lambda: defaultdict(
                                lambda: defaultdict(
                                        list)))))

# si la parada es alguna de las de las cabeceras vamos a usar la consulta de la otra db
for coche_viaje, rows in groupby(datos_row, lambda fila: (fila[cols.coche],
                                                          fila[cols.viaje])):
    Sentido = namedtuple(
        "Sentido", ("Valdecilla_Sardinero", 'Sardinero_Valdecilla'))
    sentido = Sentido(*range(2))
    sentido_viaje = ''
    for fila in rows:
#        print("fila", fila)
        if fila[cols.instante].day in dias_excluir:
            continue
        if fila[cols.parada] == paradas.Valdecilla:
            viajes_ordenado[coche_viaje[0]]['Valdecilla_Sardinero'][devuelve_intervalo(fila[cols.instante])][fila[cols.instante].day][coche_viaje[1]
                                                                                                                                      ].append(normaliza_fecha(fila[cols.instante]))
            sentido_viaje = sentido.Valdecilla_Sardinero
        elif fila[cols.parada] == paradas.Int_Sardinero_1:
            viajes_ordenado[coche_viaje[0]]['Sardinero_Valdecilla'][devuelve_intervalo(fila[cols.instante])][fila[cols.instante].day][coche_viaje[1]
                                                                                                                                      ].append(normaliza_fecha(fila[cols.instante]))
            sentido_viaje = sentido.Sardinero_Valdecilla
        elif fila[cols.parada] in paradas_a_sardinero:
            viajes_ordenado[coche_viaje[0]]['Valdecilla_Sardinero'][devuelve_intervalo(fila[cols.instante])][fila[cols.instante].day][coche_viaje[1]
                                                                                                                                      ].append(normaliza_fecha(fila[cols.instante]))
        elif fila[cols.parada] in paradas_a_valdecilla:
            viajes_ordenado[coche_viaje[0]]['Sardinero_Valdecilla'][devuelve_intervalo(fila[cols.instante])][fila[cols.instante].day][coche_viaje[1]
                                                                                                                                      ].append(normaliza_fecha(fila[cols.instante]))
# filtro para borrar los malos

viajes_ordenado_filtrado = deepcopy(viajes_ordenado)

for key, d1 in viajes_ordenado.items():
    for sentido, d2 in d1.items():
        for grupo_hora, d3 in d2.items():
            for dia, d4 in d3.items():
                for viaje, lista in d4.items():
                    if sentido == 'Valdecilla_Sardinero':
                        if filtro_valdecilla_sardinero(lista):
                            del viajes_ordenado_filtrado[key][sentido][grupo_hora][dia][viaje]
                    elif sentido == 'Sardinero_Valdecilla':
                        if filtro_sardinero_valdecilla(lista):
                            del viajes_ordenado_filtrado[key][sentido][grupo_hora][dia][viaje]


# montamos otro diccionario mas cocreto con los distintos df a pintar
for coche, valores in viajes_ordenado_filtrado.items():
#    if coche != 1:
#        pass
    for sentido, valores2 in valores.items():
        if sentido == 'Valdecilla_Sardinero':
            continue
        #        inicia_plot = True
        sentido_opuesto = 'Sardinero_Valdecilla' if sentido == 'Valdecilla_Sardinero' else 'Valdecilla_Sardinero'
        tamaño = tamaño_correcto_tupla_valde_sardi if sentido == 'Valdecilla_Sardinero' else tamaño_correcto_tupla_sardi_valde
        tamaño_opuesto = tamaño_correcto_tupla_sardi_valde if sentido == 'Valdecilla_Sardinero' else tamaño_correcto_tupla_valde_sardi
        nombres = paradas_a_sardinero_nombres if sentido == 'Valdecilla_Sardinero' else paradas_a_valdecilla_nombres
        nombres_opuesto = paradas_a_valdecilla_nombres if sentido == 'Valdecilla_Sardinero' else paradas_a_sardinero_nombres
        distancias = distancia_valdecilla_sardinero if sentido == 'Valdecilla_Sardinero' else distancia_sardinero_valdecilla
        distancias_opuesto = distancia_sardinero_valdecilla if sentido == 'Valdecilla_Sardinero' else distancia_valdecilla_sardinero
        # hay que dividir los viajes si son muchos para que se pinten en grupos más pequeños y se vea mejor
        num_grafica = 0
        for grupo_hora, valores3 in sorted(valores2.items(), key=operator.itemgetter(0)):
            inicia_plot = True
            num_grafica += 1
            for dia, valores4 in valores3.items():
#                print("dia y valores4", dia, valores4)
                df = pd.DataFrame.from_dict(
                    viajes_ordenado_filtrado[coche][sentido][grupo_hora][dia], orient='columns', dtype=None)
                df2 = pd.DataFrame.from_dict(
                    viajes_ordenado_filtrado[coche][sentido_opuesto][grupo_hora][dia], orient='columns', dtype=None)
                if df.empty or df2.empty:
                    print("Sentido", sentido)
                    print("Sentido_opuesto", sentido_opuesto)
                    if df.empty:
                        print("DF vacío")
                    if df2.empty:
                        print("DF2 vacío")
                    continue
                else:
#                    print("###########DF NO VACÍO#########")
                    color = colores[lista_dias.index(dia)]
    #                handles.append(str(dia))
                    df['paradas'] = distancias
                    df2['paradas'] = list(5000-x for x in distancias_opuesto)
                    #df['pasos_parada']=df.apply(tuple, axis=1)
                    columnas = list(df.columns.values)
                    columnas_opuesto = list(df2.columns.values)
        #            ax = df.plot(x=columnas[0], y='paradas',
        #                         label='Viaje {}'.format(str(columnas[0])), figsize=(20, 10))
                    if inicia_plot:
                        texto_label = f"Dia {dia} viaje {columnas[0]}"
                        ax = df.plot(x=columnas[0], y='paradas',
                                     color=color, label=texto_label, figsize=(15, 10))
                        ax2 = ax.twinx()
                        texto_label = f"Dia {dia} viaje {columnas_opuesto[0]}"
                        df2.plot(x=columnas_opuesto[0], y='paradas', ax=ax2,
                                 color=color, label=texto_label)
                        inicia_plot = False
                    else:
                        texto_label = f"Dia {dia} viaje {columnas[0]}"
                        df.plot(x=columnas[0], y='paradas',
                                ax=ax, color=color,  label=texto_label)
                        texto_label = f"Dia {dia} viaje {columnas_opuesto[0]}"
                        df2.plot(x=columnas_opuesto[0], y='paradas', ax=ax2,
                                 color=color, label=texto_label)
                    for viaje in columnas[1:-1]:
                        texto_label = f"Dia {dia} viaje {viaje}"
                        df.plot(x=viaje, y='paradas', ax=ax,
                                color=color, label=texto_label)
                    for viaje in columnas_opuesto[1:-1]:
                        texto_label = f"Dia {dia} viaje {viaje}"
                        df2.plot(x=viaje, y='paradas', ax=ax2,
                                 color=color, label=texto_label)
# se crea el dibujo para la vuelta en el otro eje

                    ax.set_yticks(distancias)
                    ax.set_yticklabels(nombres)
                    ax2.set_yticks(list(5000-x for x in distancias_opuesto))
                    ax2.set_yticklabels(nombres_opuesto)

                    titulo = 'Coche {} grafica {}'.format(
                        str(coche),
                        str(num_grafica))
                    ax.set_title(titulo, color='black')
                    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
                    ax.set_ylim([0, 5000])
                    ax2.set_ylim([0, 5000])
                    ax.legend(loc='center left', bbox_to_anchor=(1.15, 0.5))
                    lgd = ax2.legend(loc='center left',
                                     bbox_to_anchor=(1.3, 0.5))
                    ax.grid()
                    ax2.grid()
                    fig = ax.get_figure()
                    figura_ruta_relativa = 'coche_{}_grafica_{}.png'.format(
                        str(coche),
                        str(num_grafica))
                    figura_ruta = directorio+figura_ruta_relativa
            try:
                fig.savefig(
                    figura_ruta,
                    bbox_extra_artists=(lgd,), bbox_inches='tight')
            except NameError:
                print(f"No hay figura para grupo_hora {grupo_hora}.")
            else:
                cuerpo_informe = "".join((cuerpo_informe,
                                          textos_html_informe_100.apartado_informe.format(
                                              titulo=titulo,
                                              grafico=figura_ruta_relativa)))

# una vez obtenidas las gráficas habría que sacar unas tablas de desviación media
columnas = ['sentido', 'coche', 'dia', 'viaje', 'tv', 'v_comercial']
columnas_mostrar_final = ['coche', 'sentido', 'viaje', 'media tiempo viaje (minutos)',
                          'media velocidad comercial (km/h)', 'desviación tiempo viaje',
                          'desviación velocidad comercial']
df_mean = pd.DataFrame(columns=columnas)
for coche, valores in viajes_ordenado_filtrado.items():
    for sentido, valores2 in valores.items():
        for grupo_hora, valores3 in sorted(valores2.items(), key=operator.itemgetter(0)):
            for dia, valores4 in valores3.items():
                for viaje, valores5 in valores4.items():
                    tv = sorted(valores5)[-1]-sorted(valores5)[0]
                    v = 3.6*4900/tv.seconds
                    df_mean.loc[len(df_mean)] = [
                        sentido, coche, dia, viaje, tv, v]
# creado el df hay que hacer una pivot table para agregar los datos

df_mean['tv_minutes'] = df_mean['tv'].apply(lambda x: x.seconds/60)

pivot_table = pd.pivot_table(df_mean, values=['v_comercial', 'tv_minutes'],
                             index=['coche', 'sentido', 'viaje'],
                             aggfunc=[np.mean, np.std])
pivot_table.reset_index(inplace=True)
pivot_table.columns = columnas_mostrar_final
pivot_table.sort_values(['coche', 'viaje'], inplace=True)
cwd=os.getcwd()
pivot_table.to_csv(
    path_or_buf=cwd+R"\CENTRAL-CSV\{}{}{}_a_{}{}{}.csv".format(dia_inicio.year,
                                                                                       dia_inicio.month,
                                                                                       dia_inicio.day,
                                                                                       dia_fin.year,
                                                                                       dia_fin.month,
                                                                                       dia_fin.day))
tabla_html = pivot_table.to_html(classes='paleBlueRows',
                                 columns=columnas_mostrar_final, index=False,
                                 justify='center')
# se añade al cuerpo del informe
cuerpo_informe = "".join((cuerpo_informe,
                          textos_html_informe_100.apartado_informe_tabla.format(
                              tabla=tabla_html)))

# se genera un informe de este tipo
with open(directorio+'informe.html', 'w') as file:
    print(textos_html_informe_100.plantilla_web_estilos +
          textos_html_informe_100.plantilla_web_cuerpo.format(
              dia_inicio=dia_inicio.day,
              dia_fin=dia_fin.day,
              mes_inicio=mes_letra(dia_inicio.month),
              mes_fin=mes_letra(dia_fin.month),
              informe_completo=cuerpo_informe), file=file)
    create_pdf(
        directorio+'informe.html',
        directorio+'linea_central_del_{}-{}-{}_al_{}-{}-{}.pdf'.format(dia_inicio.year,
                                                     dia_inicio.month,
                                                     dia_inicio.day,
                                                     dia_fin.year,
                                                     dia_fin.month,
                                                     dia_fin.day))
