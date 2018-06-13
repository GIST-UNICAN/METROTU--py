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
import textos_html_informe_trafico
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
import tkinter as tk
import tkcalendar

top = tk.Tk()
locale.setlocale(locale.LC_ALL, '')
list_fechas=list(repeat(None,4))
list_botones=list()
label_fechas=("Fecha inicial comparativa","Fecha final comparativa","Fecha inicia fin comparativa","Fecha final fin comparativa")
labels_fechas_rellenas=list()
comparativa = tk.IntVar(value=1)
fines_semana = tk.IntVar()

def show_calendar(variable_cambiar):
    def getdate():
        list_fechas[variable_cambiar]=cal.selection_get()
        labels_fechas_rellenas[variable_cambiar].configure(text=str(cal.selection_get()))
        win.destroy()
        
    win=tk.Toplevel(top)
    win.wm_title('Elegir fecha')
    cal=tkcalendar.Calendar(win)
    cal.grid(row=0)
    tk.Button(win,text='ok', command=lambda: getdate()).grid(row=2)

def mostrar_fechas():
    if comparativa.get()==0:
        for j in range(2,4):
            list_botones[j].config(state="disabled")
    else:
        for j in range(2,4):
            list_botones[j].config(state="normal")
        
    pass

def ejecutar_informe():
    pass


top.columnconfigure((0,1,2,3), weight=1)
for i in range (0,4):
    tk.Label(top, text=label_fechas[i]).grid(row=i, column=0, padx=2, pady=5)
    list_botones.append(tk.Button(top,text='seleccionar', command=lambda i=i: show_calendar(i)))
    list_botones[i].grid(row=i, column=1)
    labels_fechas_rellenas.append(tk.Label(top, text=""))
    labels_fechas_rellenas[i].grid(row=i, column=2, padx=1, pady=5)
entrada=tk.Entry(top,width=30)
entrada.grid(row=4, column=1, padx=1, pady=5, columnspan=2)
espiras=tk.Label(top, text="Espiras a comparar (,)")
espiras.grid(row=4, column=0, padx=1, pady=5)

titulo=tk.Entry(top,width=30)
titulo.grid(row=5, column=1, padx=1, pady=5, columnspan=2)
tk.Label(top, text="Título del informe").grid(row=5, column=0, padx=1, pady=5)


tk.Checkbutton(top, text='¿Fines de semana?', variable=fines_semana).grid(row=6, column=0, padx=1, pady=5)

tk.Checkbutton(top, text="¿Hacer comparativa?", variable=comparativa, command=mostrar_fechas).grid(row=7, column=0, padx=1, pady=5)

tk.Button(top, text='Ejecutar', command=ejecutar_informe,width=30).grid(row=8, column=0, padx=1, pady=5, columnspan=3)

top.mainloop()







def informe_espiras(espiras, fechas, nombre_titulo):
    # VARIABLES
    espiras_dir_valdecilla = (2036, 2028, 2046, 2013, 1035)
    espiras_dir_sardinero = (2035, 2043, 2019, 2075, 1034)
    espira_cajo = (2002,)
    limite_descarga = (40000, 40000, 8000) #(7500,7500,1500)
    nombres=('Sardinero - Valdecilla', 'Valdecilla - Sardinero', 'Cajo')
    cuerpo_informe = ''
    
    actual = datetime.now()
    dia_resta = 2
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
    def mes_letra(mes):
        return date(1900, mes, 1).strftime('%B')
    
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
                    df=pd.DataFrame(list(cursor), columns=columnas)
                    datos_row[nombre][dia_inicio.year] = df
                    
                    print('datos descargados')
                    
    # CREAMOS EL DIRECTORIO
    directorio = "informe_trafico_de_{}{}{}_a_{}{}{}\\".format(dia_inicio.year,
                                                                                dia_inicio.month,
                                                                                dia_inicio.day,
                                                                                dia_fin.year,
                                                                                dia_fin.month,
                                                                                dia_fin.day)
    archivo = "{}{}{}".format(actual.year,
                              actual.month,
                              actual.day - dia_resta)
    if os.path.exists(directorio):
        pass
    else:
        os.mkdir(directorio)
    copyfile('tabla.css', directorio + 'tabla.css')
    # PROCESO DE DATOS
    #aqui vamos a crear para cada uno de los dos sentidos dos gráficos, uno que sea intensidad ocupación y otro agregando los datos de intensidad
    for destino, datos in datos_row.items():
        fig_int_oc, ax_int_oc = plt.subplots(1,2)
        fig_int_hor, ax_int_hor = plt.subplots()
        ax_int_oc_list = ax_int_oc.ravel()
        n=0
        for año, dataframe in datos.items():
            #empezamos con intensidad ocupacion
            dataframe['intensidad']=dataframe['intensidad'].apply(float)
            dataframe['ocupacion']=dataframe['ocupacion'].apply(float)
            dataframe.plot.scatter(y='intensidad',x='ocupacion', ax=ax_int_oc_list[n])
            ax_int_oc_list[n].set_ylim([0, 1600])
            ax_int_oc_list[n].set_xlim([0, 35])
            ax_int_oc_list[n].grid()
            ax_int_oc_list[n].set_xlabel('Ocupación (%)', fontsize=15)
            ax_int_oc_list[n].set_ylabel('Intensidad (veh/hora)', fontsize=15)
            ax_int_oc_list[n].set_title(str(año), fontsize=20)
            n+=1
            #hacemos lo propio con los de intensidad horaria
            pivot_table=pd.pivot_table(dataframe, values = ['intensidad'], index=['hora'], aggfunc=[np.mean])
            pivot_table.reset_index(inplace=True)
            pivot_table.columns=['Hora', 'Intensidad']
            pivot_table_interpolada=pd.DataFrame()
            #interrpolamos para suaviozar las lineas
            
            horas=tuple(range(0,24))
            f1=interp1d(horas,pivot_table['Intensidad'],kind='cubic')
            pivot_table_interpolada['intensidad_itp']=f1(horas)
            pivot_table_interpolada['Hora']=horas
            pivot_table_interpolada.index=horas
            pivot_table_interpolada.plot(y='intensidad_itp',x='Hora', ax=ax_int_hor, label=str(año))
            ax_int_hor.set_xlabel('Hora del día', fontsize=15)
            ax_int_hor.set_ylabel('Intensidad (veh/hora)', fontsize=15)
            
        fig_int_oc.set_size_inches((15, 7))
        figura_ruta_relativa = 'int_ocup_destino_{}_año_{}.png'.format(
                str(destino),
                str(año))
        figura_ruta = directorio + figura_ruta_relativa
        fig_int_oc.savefig(figura_ruta)
        titulo = 'Gráfico Intensidad Ocupación {} 2017 vs 2018'.format(destino)
        cuerpo_informe = "".join((cuerpo_informe,
                                      textos_html_informe_trafico.apartado_informe.format(
                                          titulo=titulo,
                                          grafico=figura_ruta_relativa)))
        #guardamos el otro grafico tambien
        ax_int_hor.legend(
                loc='center left',
                bbox_to_anchor=(
                    1,
                    0.5),
                prop={
                    'size': 15})
        fig_int_hor.set_size_inches((15, 7))
        figura_ruta_relativa = 'int_horaria_destino_{}_año_{}.png'.format(
                str(destino),
                str(año))
        figura_ruta = directorio + figura_ruta_relativa
        fig_int_hor.savefig(figura_ruta,bbox_inches='tight')
        titulo = 'Gráfico Intensidad Horaria {} 2017 vs 2018'.format(destino)
        cuerpo_informe = "".join((cuerpo_informe,
                                      textos_html_informe_trafico.apartado_informe.format(
                                          titulo=titulo,
                                          grafico=figura_ruta_relativa)))
        print(destino)
    
    
    # SALVADO DEL INFORME
    # se añade al cuerpo del informe
    cuerpo_informe = "".join((cuerpo_informe,
                              textos_html_informe_trafico.apartado_informe_tabla.format(
                                  tabla='')))
    
    # se genera un informe de este tipo
    with open(directorio + 'informe.html', 'w') as file:
        print(textos_html_informe_trafico.plantilla_web_estilos +
              textos_html_informe_trafico.plantilla_web_cuerpo.format(
                  dia_inicio=dia_inicio.day,
                  dia_fin=dia_fin.day,
                  mes_inicio=mes_letra(dia_inicio.month),
                  mes_fin=mes_letra(dia_fin.month),
                  informe_completo=cuerpo_informe), file=file)
    create_pdf(
        directorio + 'informe.html',
        directorio + 'linea_trafico_del_{}-{}-{}_al_{}-{}-{}.pdf'.format(dia_inicio.year,
                                                                         dia_inicio.month,
                                                                         dia_inicio.day,
                                                                         dia_fin.year,
                                                                         dia_fin.month,
                                                                         dia_fin.day))