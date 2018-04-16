from logging import basicConfig, debug, info, error, DEBUG, ERROR
import os
os.environ['QT_QPA_PLATFORM']='offscreen'

basicConfig(level=DEBUG)#, filename=os.getcwd()+ "\\log.txt")


from openpyxl import Workbook, load_workbook
from openpyxl.compat import range
from openpyxl.utils import get_column_letter
from datetime import timedelta, datetime,time

import contextlib
##import bisect
from collections import namedtuple, defaultdict
import MySQLdb
from bisect import bisect, bisect_left
from functools import partial
from itertools import starmap, groupby, chain, repeat
import pandas as pd
import numpy as np
import traceback
from functools import reduce
import textos_html_informe
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from shutil import copyfile
from pdfkit import from_file as create_pdf
from pprint import pformat


import horarios

dia_resta=2
#generamos el directorio de salvado
actual=datetime.now()
##actual_aux=actual-timedelta(days=1)
##lista_dias=(actual_aux-timedelta(days=day) for day in range(25,28) )
##for actual in lista_dias:
directorio="{}{}{}_bis/".format(actual.year,actual.month,actual.day-dia_resta)
if os.path.exists(directorio):
    pass
else:
    os.mkdir(directorio)

copyfile('tabla.css',directorio+'tabla.css')

    
class datetime_gist(datetime):
    pass

class Comprobador():

    class DiscrepanciaDatos(Exception):
        pass

    @staticmethod
    def time2datetime(lista):
        dia=actual.day-dia_resta  ########################################################## ojito
        mes=actual.month
        año=actual.year
        return tuple((datetime_gist(año,mes,dia,parada.hour,parada.minute,parada.second) for parada in lista))

    @staticmethod
    def datetime2datetimegist(dt):
        return datetime_gist(dt.year,dt.month,dt.day,dt.hour,dt.minute,dt.second,dt.microsecond)
    
    def __init__(
        self,
        linea,
        horario_linea,
        Δt_hasta_parada_control_moda,
        Δt_hasta_parada_control_min=None,
        Δt_hasta_parada_control_max=None,
        reduccion=0.5,
        ampliacion=2
        ):
        self.linea=linea
        self.horario_linea = Comprobador.time2datetime(horario_linea)
        self.Δt_hasta_parada_control_moda = Δt_hasta_parada_control_moda
        self.Δt_hasta_parada_control_min = (
            Δt_hasta_parada_control_min if Δt_hasta_parada_control_min
            else reduccion*Δt_hasta_parada_control_moda
            )
        self.Δt_hasta_parada_control_max = (
            Δt_hasta_parada_control_max if Δt_hasta_parada_control_max
            else ampliacion*Δt_hasta_parada_control_moda
            )

    def calcula_salida_fuera_horario(
        self,
        paso_cabecera_SAE,
        paso_parada_siguiente
        ):
        salida_teorica_moda = (
            paso_parada_siguiente
            - self.Δt_hasta_parada_control_moda
                          )
        if salida_teorica_moda > paso_cabecera_SAE:
            #Es un valor válido, después del registro de paso del SAE.
            salida_teorica_moda = Comprobador.datetime2datetimegist(salida_teorica_moda)
            salida_teorica_moda.linea = self.linea
            return salida_teorica_moda
        else:
            #Probamos a ver si es posible con el Δt mínimo entre
            #paradas.
            salida_teorica_minima = (
                paso_parada_siguiente
                - self.Δt_hasta_parada_control_min
                )
            if salida_teorica_minima > paso_cabecera_SAE:
                #Ok, es posible, con suerte.
                salida_teorica_minima = Comprobador.datetime2datetimegist(salida_teorica_minima)
                salida_teorica_minima.linea = self.linea
                return salida_teorica_minima
            else:
                #No es posible. O bien los datos del SAE no son
                #correctos, o el bus tarda a veces menos entre las paradas.
                info(
                    "Los datos del SAE reflejan que en la línea "
                    f"{self.linea} el bus pasó por cabecera a las "
                    f"{paso_cabecera_SAE.ctime()} y por la parada "
                    f"siguiente a las {paso_parada_siguiente.ctime()}, "
                    " pero el Δt mínimo entre ambas es de "
                    f"{self.Δt_hasta_parada_control_min}."
                    )
                salida_teorica_moda = Comprobador.datetime2datetimegist(salida_teorica_moda)
                salida_teorica_moda.linea = self.linea
                return salida_teorica_moda
        

    def __call__(
        self,
        paso_cabecera_SAE,
        paso_parada_siguiente,
        cero_segundos=time()
        ):
        punto_insercion=bisect_left(self.horario_linea, paso_cabecera_SAE)
        salida_teorica_horario = self.horario_linea[punto_insercion]

        
        if (
            #No nos creemos que el bus haya tardado tanto, salió más tarde
            paso_parada_siguiente-salida_teorica_horario
            > self.Δt_hasta_parada_control_max
            ) or (
                #No nos creemos que el bus tardara tan poco, salió antes
                paso_parada_siguiente-salida_teorica_horario
                  < self.Δt_hasta_parada_control_min
                ):
            return self.calcula_salida_fuera_horario(
                paso_cabecera_SAE,
                paso_parada_siguiente
                )
        else:
            salida_teorica_horario.linea = self.linea
            return salida_teorica_horario
        diferencia=(paso_parada_siguiente-self.tiempo_hasta_parada_control)-self.horario_linea[punto_insercion]
        diferencia2=(paso_parada_siguiente-self.tiempo_hasta_parada_control)-self.horario_linea[punto_insercion-1]
##        if self.linea==100:
##            print(' paso_parada_siguiente: ',paso_parada_siguiente, ' salida row anterior: ',paso_cabecera_SAE,' diferencia: ',diferencia,' horario considerado '
##                  ,self.horario_linea[punto_insercion],' diferencia2: ', diferencia2,' horario considerado '
##                  ,self.horario_linea[punto_insercion-1]
##                  ,' punto insercion ', punto_insercion)
##            print('check p insercion tipo', type(paso_parada_siguiente-self.tiempo_hasta_parada_control), ' resta ', paso_parada_siguiente-self.tiempo_hasta_parada_control)
##            print('---------------------------------------')
        if abs(diferencia)>self.margen_tiempo and abs(diferencia2)>self.margen_tiempo: #se perdio la conexion y sale a la hora de paso por valdecilla
            paso_cabecera_SAE.linea=self.linea #AQUÍ
            return paso_cabecera_SAE
        elif abs(diferencia)>abs(diferencia2):
            #volvemos a comprobar la salida anterior con la teorica para ver cual es mayor y nos quedamos con la mayor
            self.horario_linea[punto_insercion-1].linea=self.linea
            return self.horario_linea[punto_insercion-1] if (self.horario_linea[punto_insercion-1]>paso_cabecera_SAE) else paso_cabecera_SAE
        else:
            self.horario_linea[punto_insercion].linea=self.linea
            return self.horario_linea[punto_insercion] if (self.horario_linea[punto_insercion]>paso_cabecera_SAE) else paso_cabecera_SAE
            #devolvemos la salida según el horario programado

(
    comprueba_3,
    comprueba_13,
    comprueba_17,
    comprueba_100_sardi,
    comprueba_100_valde
    )= starmap(
        Comprobador,
        (
            (3, horarios.paradas_3,timedelta(minutes=1, seconds=20)),
            (13, horarios.paradas_13,timedelta(minutes=2, seconds=0)),
            (17, horarios.paradas_17,timedelta(minutes=1, seconds=30)),
            (100, horarios.paradas_C_Int_Sardinero,timedelta(minutes=2, seconds=00)),
            (100, horarios.paradas_C_Int_Valdecilla,timedelta(minutes=3, seconds=00))
            )
        )

Números_de_paradas = namedtuple(
    "Números_de_paradas",
    (
        "Sardinero",
        "Sardinero1",
        "Sardinero2",
        "Valdecilla",
        "Avda_Valdecilla",
        "San_Fernando",
        "Vega_Lamera",
        "Cajo2",
        "TQuevedo22",
        "Albericia18")
    )


def entrecomilla(s):
    return "".join("'", s, "'")

def datetime2time(fecha):
    return time(fecha.hour,fecha.minute,fecha.second)

def comparatiempos(t1, t2): #devuelve da diferencia ABSOLUTA
    t1=t1.hour*3600+t1.minute*60+t1.second
    t2=t2.hour*3600+t2.minute*60+t2.second
    diferencia= abs(t1-t2)
    horas, resto=divmod(diferencia,3600)
    minutos, segundos =divmod(resto,60)
    return time(horas,minutos,segundos)

def restatiempos(t1, t2): 
    t1=t1.hour*3600+t1.minute*60+t1.second
    t2=t2.hour*3600+t2.minute*60+t2.second
    diferencia= t1-t2
    horas, resto=divmod(diferencia,3600)
    minutos, segundos =divmod(resto,60)
    return time(horas,minutos,segundos)

def ordena_diccionario(dic):
    for k,v in dic.items():
        dic[k] = tuple(x for x,y in groupby(sorted(v)))
    return dic

def filtra_llegadas(lista, margen_tiempo=timedelta(minutes=2)):
    devuelve_lista=list()
    elemento_anterior=datetime(1900,1,1,0,0,0)
    for elemento in lista:
        if elemento - elemento_anterior > margen_tiempo:
            devuelve_lista.append(elemento)
        elemento_anterior=elemento
    return devuelve_lista

def genera_informe(
    fecha_inicio=None,
    fecha_fin=None,
    números_de_paradas = Números_de_paradas(516, 511, 515, 509, 512, 11, 171, 78, 46, 390)
    ):
    if not (fecha_inicio and fecha_fin):
        fecha_inicio=datetime(actual.year,actual.month,actual.day-dia_resta,6,0,0)
        fecha_fin=datetime(actual.year,actual.month,actual.day-dia_resta,22,0,0)
    
    # open the file
    
##    fecha_inicio=datetime(actual.year,actual.month,actual.day-dia_resta,6,0,0) #######################################
##    fecha_fin=datetime(actual.year,actual.month,actual.day-dia_resta,22,0,0)  #########################################
    paradas_query = " or ".join("parada={}".format(parada) for parada in números_de_paradas)
    queries = (
        "create temporary table tabla_1 as (SELECT Linea, Coche,Viaje, Parada, Instante, Nombre  FROM `pasos_parada` where Instante between '{0}' and '{1}' and ({2}))".format(fecha_inicio,fecha_fin,paradas_query),
        "create temporary table tabla_2 as (SELECT Linea, Coche, Viaje FROM `pasos_parada` where Instante between '{0}' and '{1}' and parada in(11, 44) and linea in (3,17))".format(fecha_inicio,fecha_fin),
        "SELECT * FROM tabla_1 t1 WHERE not EXISTS ( SELECT * FROM tabla_2 t2 where t2.Linea=t1.Linea and t2.Viaje=t1.Viaje and t1.Coche=t2.Coche order by Linea, instante)"
    )
    
##             "drop table tabla_1; "
##             "drop table tabla_2; ")
    

##        "SELECT * FROM `pasos_parada` where Instante between '{0}' and '{1}' "
##             "and ({2}) "
##             "ORDER BY Linea, Coche, Instante asc"
##             ).format(fecha_inicio,fecha_fin,paradas_query)
##    debug("query:\n" + query + "\n")
    with contextlib.closing(MySQLdb.connect(user='root',
                                            password='madremia902',
                                            host='193.144.208.142',
                                            port=3306,
                                            database='autobuses'
                                            )
                            ) as conexion:
        with contextlib.closing(conexion.cursor()) as cursor:
            for query in queries:
                cursor.execute(query)
            datos_row=tuple(cursor)
##    debug("datos_row\n"+ str(datos_row))

    # lineas 91  repuente sardinero repuente y 92 cueto sardinero cueto
    llegadas_sardinero={100:list(),91:list(),20:list(), 92: list()}
    llegadas_valdecilla={100:list(),3:list(),13:list(),14:list(),17:list()}
    salidas_sardinero={100:list(),91:list(),20:list(), 92: list(),'resto':list()}
    salidas_valdecilla={100:list(),3:list(),13:list(), 14:list(),17:list(),'resto':list()}

    Columnas = namedtuple("Columnas", ("linea", "coche", "viaje", "parada", "instante", "nombre"))
    cols = Columnas(*range(6))
    
    for linea_bus, rows in groupby(datos_row, lambda fila: (fila[cols.linea], fila[cols.coche])):
        linea=linea_bus[0]
        iterador_filas=iter(rows)
        linea_anterior=next(iterador_filas)
        for row in iterador_filas:
##            debug(str(row))
##            debug(str(row[4]))
##            debug("\n")
            instante=datetime_gist(row[cols.instante].year,row[cols.instante].month,row[cols.instante].day,row[cols.instante].hour,row[cols.instante].minute, row[cols.instante].second, row[cols.instante].microsecond)
            instante_anterior=datetime_gist(linea_anterior[cols.instante].year,linea_anterior[cols.instante].month,linea_anterior[cols.instante].day,linea_anterior[cols.instante].hour,linea_anterior[cols.instante].minute, linea_anterior[cols.instante].second, row[cols.instante].microsecond)
            instante.linea=linea
            instante_anterior.linea=linea
            parada=row[cols.parada]
            if linea==100:
                debug("\n")
                debug("Caso del 100")
                debug("instante_anterior")
                debug(str(instante_anterior))
                debug("instante")
                debug(str(instante))
                debug("\n")
                if parada==números_de_paradas.Avda_Valdecilla:
                    llegadas_valdecilla[100].append(instante)
                elif parada==números_de_paradas.San_Fernando:
                    salidas_valdecilla[100].append(comprueba_100_valde(instante_anterior,instante))
##            if linea==100:
                elif parada==números_de_paradas.Sardinero:
                    llegadas_sardinero[100].append(instante)
                elif parada==números_de_paradas.Vega_Lamera:
                    salidas_sardinero[100].append(comprueba_100_sardi(instante_anterior,instante))
            if linea==3:
                if parada==números_de_paradas.Valdecilla:
                    llegadas_valdecilla[3].append(instante)
                if parada==números_de_paradas.Cajo2:
                    salidas_valdecilla[3].append(comprueba_3(instante_anterior,instante))
            if linea==13:
                if parada==números_de_paradas.Valdecilla:
                    llegadas_valdecilla[13].append(instante)
                if parada==números_de_paradas.TQuevedo22:
                    salidas_valdecilla[13].append(comprueba_13(instante_anterior,instante))
            if linea==14:
                if parada==números_de_paradas.Valdecilla:
                    llegadas_valdecilla[13].append(instante)
                if parada==números_de_paradas.Avda_Valdecilla:
                    salidas_valdecilla[13].append(instante)
            if linea==17:
                if parada==números_de_paradas.Valdecilla:
                    llegadas_valdecilla[17].append(instante)
                if parada==números_de_paradas.Albericia18:
                    salidas_valdecilla[17].append(comprueba_17(instante_anterior,instante))
            if linea==20:
                if parada==números_de_paradas.Sardinero1:
                    llegadas_sardinero[20].append(instante)
                if parada==números_de_paradas.Sardinero2:
                    salidas_sardinero[20].append(instante)
            if linea==9:
                if parada==números_de_paradas.Sardinero1:
                    llegadas_sardinero[91].append(instante)
                    salidas_sardinero[92].append(instante)
                if parada==números_de_paradas.Sardinero2:
                    llegadas_sardinero[92].append(instante)
                    salidas_sardinero[91].append(instante)
            if linea in (1,2,72):
                if parada==números_de_paradas.Sardinero1:
                    salidas_sardinero['resto'].append(instante)
                if parada==números_de_paradas.Valdecilla:
                    salidas_valdecilla['resto'].append(instante)
            linea_anterior=row
    debug("salidas_sardinero" + "\n" + str(salidas_sardinero))
    debug("salidas_valdecilla" + "\n" + str(salidas_valdecilla))
    lineas_acaban_sardinero = (92, 20) #(91, 92, 20)
    lineas_acaban_valdecilla = (3, 13, 17)


    #ordenamos los diccionarios con llegadas y salidas
    (
        llegadas_sardinero,
        llegadas_valdecilla,
        salidas_sardinero,
        salidas_valdecilla
        ) = map(ordena_diccionario,
                (
                    llegadas_sardinero,
                    llegadas_valdecilla,
                    salidas_sardinero,
                    salidas_valdecilla
                    )
                )
    # generamos unas listas con las corresondencias para cada intercambiador

    resultados = {
        "Valdecilla_barrios": [],
        "Barrios_Valdecilla": [],
        "Sardinero_barrios": [],
        "Barrios_Sardinero": []
        }

    llegadas_valdecilla[100]=filtra_llegadas(llegadas_valdecilla[100])
    for instante_llegada_central in llegadas_valdecilla[100]:
        for linea in lineas_acaban_valdecilla:
            try:
                posición_salida_linea = bisect(salidas_valdecilla[linea], instante_llegada_central)
                instante_salida_linea = salidas_valdecilla[linea][posición_salida_linea]
                tiempo_espera = instante_salida_linea - instante_llegada_central
                resultados["Valdecilla_barrios"].append((linea,# sentido
                                                        instante_salida_linea.linea,# sacamos la propiedad linea
                                                        instante_salida_linea,
                                                        instante_llegada_central,
                                                        tiempo_espera)
                                                        )
            except IndexError:
                pass

    for linea in lineas_acaban_valdecilla:
        for instante_llegada in llegadas_valdecilla[linea]:
            try:
                posición_salida_central = bisect(salidas_valdecilla[100], instante_llegada)
                instante_salida_central = salidas_valdecilla[100][posición_salida_central]
                tiempo_espera = instante_salida_central - instante_llegada
                if tiempo_espera<timedelta(hours=2):
                    resultados["Barrios_Valdecilla"].append((linea,# sentido
                                                             instante_llegada.linea,# sacamos la propiedad linea
                                                             instante_llegada,
                                                             instante_salida_central,
                                                             tiempo_espera))
            except IndexError:
                pass
            
    salidas_sardinero[92]=filtra_llegadas(salidas_sardinero[92], timedelta(minutes=1)) ##¿?       
    llegadas_sardinero[91]=filtra_llegadas(llegadas_sardinero[91], timedelta(minutes=1))
    #juntamos las líneas 91 y 20 que van hacia monte porque estan "coordinadas"
    salidas_sardinero[20] = sorted(chain(salidas_sardinero[91], salidas_sardinero[20]))
    llegadas_sardinero[20] = sorted(chain(llegadas_sardinero[91], llegadas_sardinero[20]))
    llegadas_sardinero[100]=filtra_llegadas(llegadas_sardinero[100])
    for instante_llegada_central in llegadas_sardinero[100]:
        for linea in lineas_acaban_sardinero:
            try:
                posición_salida_linea = bisect(salidas_sardinero[linea], instante_llegada_central)
                instante_salida_linea = salidas_sardinero[linea][posición_salida_linea]
                tiempo_espera = instante_salida_linea - instante_llegada_central
                resultados["Sardinero_barrios"].append((linea,# sentido
                                                        instante_salida_linea.linea,# sacamos la propiedad linea
                                                        instante_salida_linea,
                                                        instante_llegada_central,
                                                        tiempo_espera)
                                                        )
            except IndexError:
                pass

            
    for linea in lineas_acaban_sardinero:
        for instante_llegada in llegadas_sardinero[linea]:
            try:
                posición_salida_central = bisect(salidas_sardinero[100], instante_llegada)
                instante_salida_central = salidas_sardinero[100][posición_salida_central]
                tiempo_espera = instante_salida_central - instante_llegada
                if tiempo_espera<timedelta(hours=2):
                    resultados["Barrios_Sardinero"].append((linea,# sentido
                                                             instante_llegada.linea,# sacamos la propiedad linea
                                                             instante_llegada,
                                                             instante_salida_central,
                                                             tiempo_espera))
            except IndexError:
                pass
            


    def genera_tablas_intercambiador(trayecto, caso_particular, outlayers_time='15 minutes', direccion_centro=False):
        def media_espera(objeto):
            return reduce(timedelta.__add__,objeto)/len(objeto)

        def comprueba_media_mas_50_porciento(row):
            return 1 if row['espera'] > 1.5*table_intercambiador_barrios_espera['espera'].get(int(row['linea'])) else 0
        
        def comprueba_outlayers(row):
            return 1 if row['espera'] > pd.Timedelta(outlayers_time) else 0
        
        def alternativas_horarios_dataframe(df):
            df.reset_index(inplace=True, drop=True)
            if direccion_centro:
                df['alternativa']=''
                df['espera_alternativa']=''
                if trayecto=='Barrios_Sardinero':
                    lista_bisect=salidas_sardinero['resto']
                if trayecto=='Barrios_Valdecilla':
                    lista_bisect=salidas_valdecilla['resto']
                    
                for index,row in df[["salida","linea","espera"]].iterrows():
                    try:
                        posición_salida_otra_linea = bisect(lista_bisect, row["salida"]) # ojo que salida es llegada
                        instante_salida_otra_linea = lista_bisect[posición_salida_otra_linea]
                        tiempo_espera = instante_salida_otra_linea - row["salida"]
                        if tiempo_espera<row["espera"]:
                            df.iloc[index,df.columns.get_loc('alternativa')]=instante_salida_otra_linea.linea
                            df.iloc[index,df.columns.get_loc('espera_alternativa')]=tiempo_espera
                            
                    except IndexError:
                        pass
                # ponemos las columnas en el dataframe teniendo en cuenta que el de outlayers y el de + 50 son diferentes y devolvemos las columnas a mostrar
                try:
                    df.columns=['Conexión','Línea','Paso autobús','Línea central','Espera','','','Línea alternativa','Espera alternativa']
                except:
                    df.columns=['Conexión','Línea','Paso autobús','Línea central','Espera','','Línea alternativa','Espera alternativa']
                return (['Conexión','Espera Media','Datos empleados','Supera media + 50%'],
                        ['Conexión','Línea','Paso autobús','Línea central','Espera','Línea alternativa','Espera alternativa'])
            else: # SI NO ES DIRECCION CENTRO HAy que poner las columnas sin las alternativas
                try: # para poner 7 columnas
                    df.columns=['Conexión','Línea','Paso autobús','Línea central','Espera','','']
                except: # para poner el caso de 6 columnas volvemos de la excepcion anterior
                    df.columns=['Conexión','Línea','Paso autobús','Línea central','Espera','']
                return (['Conexión','Espera Media','Datos empleados','Supera media + 50%'],
                        ['Conexión','Línea','Paso autobús','Línea central','Espera']) # devolvemos los nombres a mostrar

        
        # agregamos los datos con pandas :)
        dataframe_intercambiador_barrios=pd.DataFrame(resultados[trayecto],
                                                  columns=['linea','linea_real','salida','llegada_central','espera'])
        debug("resultados[trayecto]")
        debug(str(resultados[trayecto]))
        debug("\n")

        # eliminamos los reprtidos de la 13 que tiene el doble de frecuencia

        indices_duplicados=dataframe_intercambiador_barrios[dataframe_intercambiador_barrios.linea == caso_particular ].duplicated(['linea', 'salida'],keep='first')
        dataframe_intercambiador_barrios.drop(
            dataframe_intercambiador_barrios.index[
                list(
                    indices_duplicados[
                        indices_duplicados != True].index)], inplace=True)
        # retiramos los outlyers a un df aparte
        debug(str(dataframe_intercambiador_barrios))
        dataframe_intercambiador_barrios['outlayers']=dataframe_intercambiador_barrios.apply(comprueba_outlayers,axis=1)
        resultado_outlayers=dataframe_intercambiador_barrios[dataframe_intercambiador_barrios.outlayers == 1]
        indices_outlayers=dataframe_intercambiador_barrios[dataframe_intercambiador_barrios.outlayers == 1 ].index.values
        dataframe_intercambiador_barrios.drop(
            dataframe_intercambiador_barrios.index[
                indices_outlayers], inplace=True)

        
        table_intercambiador_barrios_espera=pd.pivot_table(
            dataframe_intercambiador_barrios,
            values=['espera'],
            index=['linea'],
            aggfunc=media_espera)
        #añadimos una columna para reflejar los tiempos mayores al 50% de la media
        dataframe_intercambiador_barrios['espera_mas_50']=dataframe_intercambiador_barrios.apply(comprueba_media_mas_50_porciento,axis=1)
        
        table_intercambiador_barrios_cuenta_50=pd.pivot_table(
            dataframe_intercambiador_barrios,
            values=['espera_mas_50'],
            index=['linea'],
            aggfunc=[np.sum])
        table_intercambiador_barrios_cuenta=pd.pivot_table(
            dataframe_intercambiador_barrios,
            values=['espera_mas_50'],
            index=['linea'],
            aggfunc=[np.size])
        resultado=pd.concat([table_intercambiador_barrios_espera,
                             table_intercambiador_barrios_cuenta,
                             table_intercambiador_barrios_cuenta_50],
                            axis=1).reset_index()
        resultado.columns=['Conexión','Espera Media','Datos empleados','Supera media + 50%']
        resultado_mas_50=dataframe_intercambiador_barrios[dataframe_intercambiador_barrios.espera_mas_50 == 1]
        
        #hay que comprobar con estas conexiones perdidas si pudieron coger un 1 o un 2 o un 7 en el caso de valdecilla
        alternativas_horarios_dataframe(resultado_mas_50)
        columnas_mostrar = alternativas_horarios_dataframe(resultado_outlayers)
        #guardamos en csv
        # pintamos espera en minutos
        dataframe_intercambiador_barrios['espera minutos']=dataframe_intercambiador_barrios['espera']/pd.Timedelta('1 minute')
        dataframe_intercambiador_barrios['hora salida']=[float(pd.Timestamp.strftime(item, '%H.%M')) for item in dataframe_intercambiador_barrios['salida']]
    ##    dataframe_intercambiador_barrios.set_index('hora salida', inplace=True)
        grupo=dataframe_intercambiador_barrios.sort_values(by=['salida']).groupby('linea_real')
        ncols=1
        nrows=1 #int(np.ceil(grupo.ngroups/ncols))
        fig, axes = plt.subplots(nrows=nrows, ncols=ncols)
        fig = plt.figure(figsize=(10,5))
        plt.grid(True)
        for key in grupo.groups.keys():
            x=grupo.get_group(key)['hora salida']
            y=grupo.get_group(key)['espera minutos']
            plt.scatter(x,y)
            plt.plot(x,y)
            plt.ylim(0,20)
            plt.xlim(7,23.5)
        plt.xlabel('Hora del día')
        plt.ylabel('Minutos de transbordo')
        plt.legend([x for x in grupo.groups.keys()], loc=1,title='Líneas')
        plt.savefig(directorio+trayecto)
        return ((resultado,columnas_mostrar[0]),
                (resultado_mas_50.sort_values(by=["Conexión", "Línea", "Línea central"]),columnas_mostrar[1]),
                (resultado_outlayers.sort_values(by=["Conexión", "Línea", "Línea central"]),columnas_mostrar[1]) )


    #generamos el informe

    def rellena_datos_elemento_informe(intercambiador_sentido,titulo,nombre_foto):
        def formatea_linea(numero, nombre= {3:'Ojaiz línea 3',13:'Lluja líneas 13 y 14',17:'Corbán línea 17'
                                            ,92:'Cueto línea 9',20:'Monte líneas 9 y 20'}):
            return nombre[numero]

        def formatea_hora(hora):
            return hora.strftime('%H:%M:%S')
        
        def formatea_espera(espera):
            horas, resto=divmod(pd.Timedelta(espera).seconds,3600)
            minutos, segundos = divmod(resto,60)
            return "".join((str(horas).rjust(2, '0'),':',str(minutos).rjust(2, '0'),':',str(segundos).rjust(2, '0')))
        
        def pandas_html(tabla, columnas, es_tabla_medias=False):
            lista_formatos_base=[formatea_linea,None,formatea_hora,formatea_hora,None]
            formatos_no_medias=lista_formatos_base+ list(repeat(None,len(columnas)-len(lista_formatos_base)))
            formateadores= [formatea_linea,formatea_espera,None,None ] if es_tabla_medias else formatos_no_medias
            return tabla.to_html(classes='paleBlueRows',
                                 columns=columnas, index=False,
                                 justify='center',
                                 formatters=formateadores)
        
        return textos_html_informe.apartado_informe.format(tabla_medias=pandas_html(intercambiador_sentido[0][0],intercambiador_sentido[0][1],True),
                                                    titulo= titulo,
                                                    tabla_supera_media=pandas_html(intercambiador_sentido[1][0],intercambiador_sentido[1][1]),
                                                    grafico="".join((nombre_foto,'.png')),
                                                    tabla_anomalos=pandas_html(intercambiador_sentido[2][0],intercambiador_sentido[2][1]))

    #elemento para guardar las imagenes
    sardinero_centro=genera_tablas_intercambiador('Barrios_Sardinero', 0,direccion_centro=True)
    sardinero_barrios=genera_tablas_intercambiador('Sardinero_barrios', 0)
    valdecilla_centro=genera_tablas_intercambiador('Barrios_Valdecilla', 0,direccion_centro=True)
    valdecilla_barrios=genera_tablas_intercambiador('Valdecilla_barrios', 0)

    texto_completo_informe=textos_html_informe.plantilla_web_cuerpo

    titulos=('BARRIOS -&gt; VALDECILLA -&gt; CENTRO'
             ,'CENTRO -&gt; VALDECILLA -&gt; BARRIOS'
             ,'BARRIOS -&gt; SARDINERO -&gt; CENTRO'
             ,'CENTRO -&gt; SARDINERO -&gt; BARRIOS')

    tablas=(valdecilla_centro,valdecilla_barrios,sardinero_centro,sardinero_barrios)

    nombres_fotos=('Barrios_Valdecilla','Valdecilla_barrios','Barrios_Sardinero','Sardinero_barrios')

    texto_exportar=textos_html_informe.plantilla_web_estilos+texto_completo_informe.format(dia=actual.day-dia_resta,
                                  mes=actual.month,
                                  ano=actual.year,
                                  informe_completo="\n".join((map(rellena_datos_elemento_informe,tablas,titulos,nombres_fotos))))

    with open(directorio+'informe{}{}{}_bis.html'.format(actual.year,actual.month,actual.day-dia_resta),'w') as file:
        print(texto_exportar, file=file)

    create_pdf(
        directorio+'informe{}{}{}_bis.html'.format(actual.year,actual.month,actual.day-dia_resta),
        directorio+'{}-{}-{}.pdf'.format(actual.year,actual.month,actual.day-dia_resta)
        )

if __name__ == "__main__":
    genera_informe()
