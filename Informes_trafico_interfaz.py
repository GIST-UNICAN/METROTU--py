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
from tkinter import messagebox
import tkcalendar
datf=None
top = tk.Tk()
locale.setlocale(locale.LC_ALL, '')
list_fechas=list(repeat(None,4))
list_botones=list()
label_fechas=("Fecha inicial comparativa","Fecha final comparativa","Fecha inicia fin comparativa","Fecha final fin comparativa")
labels_fechas_rellenas=list()
comparativa = tk.IntVar(value=1)
fines_semana = tk.IntVar()
info_intro_espiras='Para obtener datos agregados introducir espiras separadas por comas \n ejemplo 1001,1002... \n para Obtener datos por separado introducir nombre: espira1,espira2; \n ejemplo Paseo Pereda: 1001,1002,1003; San Fernando: 1006; Los Ciruelos:1005,1008'  


def mensaje_error(msg):
    messagebox.showerror('ERROR', msg)

def mensaje_info(msg=info_intro_espiras):
    messagebox.showinfo('INFO', msg)
    
def show_calendar(variable_cambiar):
    def getdate():
        list_fechas[variable_cambiar]=cal.selection_get()
        if variable_cambiar in (0,2):
            list_fechas[variable_cambiar]=datetime.combine(cal.selection_get(), datetime.min.time())
        else: 
            list_fechas[variable_cambiar]=datetime.combine(cal.selection_get(), datetime.max.time())
            
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
def format_date(dt):
    return datetime.strftime(dt,'%d-%m-%Y')
def ejecutar_informe():
    # hay que sacar todos los datos para llamar a la funcion de generar informe
    continuar=True
    espiras_agrupadas=False
    try:
        tupla_espiras=tuple((x.lstrip(), tuple(int(a) for a in y.split(','))) for x,y in tuple(x.split(':') for x in a))
        espiras_agrupadas=True
    except Exception:
        #si no son varias probamos con que solo quiera una espira sin agregar
        try:
            tupla_espiras=tuple(int(x) for x in entrada.get().split(','))
        except Exception:
            continuar=False
            mensaje_error('El formato de las espiras no es correcto, por favor introduzca números separados por comas o con el formato múltiple correcto')
    try:
        titulo_informe=str(titulo.get())
    except Exception:
        continuar=False
        mensaje_error('El título no es correcto')
    try:
        if comparativa.get()==1:
            if list_fechas[1]<list_fechas[0] or list_fechas[3]<list_fechas[2]:
                mensaje_error('Las no son correctas compruebe que la finalización es posterior al comienzo')
                continuar=False
        else:
             if list_fechas[1]<list_fechas[0]:
                mensaje_error('Las no son correctas compruebe que la finalización es posterior al')
                continuar=False
    except Exception:
        mensaje_error('Rellene las fechas del informe')
        continuar=False
    fs= True if fines_semana.get()==1 else False
    comp = True if comparativa.get()==1 else False
    if continuar:
       informe_espiras(tupla_espiras, list_fechas, titulo_informe, fs, comp) 
        
    pass

def informe_espiras(espiras, fechas, nombre_titulo, fines_semana, comparativa, espiras_agrupadas):
    # VARIABLES
    if not espi
    nombres=list()
    espiras_dir_valdecilla=list()
    limite_descarga=list()
    for elemento in espiras
    if espiras_agrupadas:
        nombres,
        espiras_dir_valdecilla
        limite_descarga
    else:
        espiras
    espiras_dir_valdecilla = espiras
    if comparativa:
        limite_descarga = int(len(espiras_dir_valdecilla)*60*24*max((fechas[1]-fechas[0]).days+1,(fechas[3]-fechas[2]).days+1))
    else:
         limite_descarga = int(len(espiras_dir_valdecilla)*60*24*((fechas[1]-fechas[0]).days+1)) #(7500,7500,1500)
         
    print(limite_descarga)
    nombres=nombre_titulo
    cuerpo_informe = ''
    
    actual = datetime.now()
    dia_resta = 2
    dia_inicio = fechas[0]
    
    dia_fin = fechas[1]
    un_minuto = timedelta(minutes=1)
    dia_control = dia_inicio
    un_dia = timedelta(days=1)
    # esto seria recomendable cambiarlo cuando hay bisisestos
    un_año = timedelta(days=366)
    lista_dias = []
    dias_excluir = (100,)
    if comparativa:
        dia_inicio_anterior = fechas[2]
        dia_fin_anterior = fechas[3]
        descargas_a_realizar = {(dia_inicio, dia_fin): (espiras_dir_valdecilla, limite_descarga, nombres),
                                (dia_inicio_anterior, dia_fin_anterior): (espiras_dir_valdecilla, limite_descarga, nombres)}
       
    else:
         descargas_a_realizar = {(dia_inicio, dia_fin): (espiras_dir_valdecilla, limite_descarga, nombres)}
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
    
    datos_row=defaultdict(lambda: defaultdict(pd.DataFrame))
    for dias, valores in descargas_a_realizar.items():
        query_fines_semana=" and weekday(fecha) not  in (6,5)" if fines_semana  else ""
        dia_inicio = dias[0]
        dia_fin = dias[1]
        espiras=valores[0]
        limite=valores[1]
        nombre=valores[2]
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
                                    {}
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
                                        dia,Hora""".format(query_fines_semana,espiras, limite))
        
        with contextlib.closing(MySQLdb.connect(user='root',
                                                password='madremia902',
                                                host='193.144.208.142',
                                                port=3306,
                                                database='Trafico_Santander'
                                                )) as conexion:
            with contextlib.closing(conexion.cursor()) as cursor:
                exhaust_map(cursor.execute, querie)
                df=pd.DataFrame(list(cursor), columns=columnas)
                datos_row[nombre][(dia_inicio, dia_fin)] = df
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
        fig_int_oc, ax_int_oc = plt.subplots(1,2) if comparativa else plt.subplots(1,1)
        fig_int_hor, ax_int_hor = plt.subplots()
        
        ax_int_oc_list = ax_int_oc.ravel() if comparativa else (ax_int_oc,)
        n=0
        print(len(datos.items()))
        for año, dataframe in datos.items():
            label = '{} al {}'.format(format_date(año[0]),format_date(año[1]))
            #empezamos con intensidad ocupacion
            dataframe['intensidad']=dataframe['intensidad'].apply(float)
            dataframe['ocupacion']=dataframe['ocupacion'].apply(float)
            dataframe.plot.scatter(y='intensidad',x='ocupacion', ax=ax_int_oc_list[n])
            ax_int_oc_list[n].set_ylim([0, 1600])
            ax_int_oc_list[n].set_xlim([0, 35])
            ax_int_oc_list[n].grid()
            ax_int_oc_list[n].set_xlabel('Ocupación (%)', fontsize=15)
            ax_int_oc_list[n].set_ylabel('Intensidad (veh/hora)', fontsize=15)
            ax_int_oc_list[n].set_title(label, fontsize=20)
            n+=1
            #hacemos lo propio con los de intensidad horaria
            pivot_table=pd.pivot_table(dataframe, values = ['intensidad'], index=['hora'], aggfunc=[np.mean])
            pivot_table.reset_index(inplace=True)
            pivot_table.columns=['Hora', 'Intensidad']
           
            pivot_table.plot(y='Intensidad',x='Hora', ax=ax_int_hor, label=label)
            ax_int_hor.set_xlabel('Hora del día', fontsize=15)
            ax_int_hor.set_ylabel('Intensidad (veh/hora)', fontsize=15)
            
        fig_int_oc.set_size_inches((15, 7))
        figura_ruta_relativa = 'int_ocup_destino_{}_año_{}.png'.format(
                str(destino),
                str(año))
        figura_ruta = directorio + figura_ruta_relativa
        fig_int_oc.savefig(figura_ruta)
        titulo = 'Gráfico Intensidad Ocupación'
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
        titulo = 'Gráfico Intensidad Horaria'
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
        directorio + 'trafico_del_{}-{}-{}_al_{}-{}-{}.pdf'.format(dia_inicio.year,
                                                                         dia_inicio.month,
                                                                         dia_inicio.day,
                                                                         dia_fin.year,
                                                                         dia_fin.month,
                                                                         dia_fin.day))
top.columnconfigure((0,1,2,3), weight=1)
for i in range (0,4):
    tk.Label(top, text=label_fechas[i]).grid(row=i, column=0, padx=2, pady=5)
    list_botones.append(tk.Button(top,text='seleccionar', command=lambda i=i: show_calendar(i)))
    list_botones[i].grid(row=i, column=1)
    labels_fechas_rellenas.append(tk.Label(top, text=""))
    labels_fechas_rellenas[i].grid(row=i, column=2, padx=1, pady=5)
entrada=tk.Entry(top,width=30)
entrada.grid(row=4, column=1, padx=1, pady=5, columnspan=2)
tk.Label(top, text="Espiras a comparar (,)").grid(row=4, column=0, padx=1, pady=5)
tk.Button(top,text='info',command=mensaje_info).grid(row=4, column=3, padx=1, pady=5)
titulo=tk.Entry(top,width=30)
titulo.grid(row=5, column=1, padx=1, pady=5, columnspan=2)
tk.Label(top, text="Título del informe").grid(row=5, column=0, padx=1, pady=5)


tk.Checkbutton(top, text='¿Fines de semana?', variable=fines_semana).grid(row=6, column=0, padx=1, pady=5)

tk.Checkbutton(top, text="¿Hacer comparativa?", variable=comparativa, command=mostrar_fechas).grid(row=7, column=0, padx=1, pady=5)

tk.Button(top, text='Ejecutar', command=ejecutar_informe,width=30).grid(row=8, column=0, padx=1, pady=5, columnspan=3)


top.mainloop()








