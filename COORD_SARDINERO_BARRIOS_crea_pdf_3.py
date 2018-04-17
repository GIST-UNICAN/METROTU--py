from logging import basicConfig, debug, info, error, DEBUG, ERROR
import os
os.environ['QT_QPA_PLATFORM']='offscreen'

from sys import stdout
basicConfig(level=DEBUG)
##basicConfig(level=DEBUG, filename=, "".join((os.getcwd(),"\\log.txt")))

from openpyxl import Workbook, load_workbook
from openpyxl.compat import range
from openpyxl.utils import get_column_letter
from datetime import timedelta, datetime,time
import contextlib
##import bisect
from collections import namedtuple, defaultdict, OrderedDict
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
from tools import exhaust_map, create_objects, pretty_output
import horarios

dia_resta = 6
#generamos el directorio de salvado
actual=datetime.now()
##actual_aux=actual-timedelta(days=1)
##lista_dias=(actual_aux-timedelta(days=day) for day in range(25,28) )
##for actual in lista_dias:
directorio="{}{}{}_bis/".format(actual.year,
                                actual.month,
                                actual.day-dia_resta)
if os.path.exists(directorio):
    pass
else:
    os.mkdir(directorio)
copyfile('tabla.css', directorio+'tabla.css')


class Dict_de_listas(defaultdict):
    def __init__(self):
        return super().__init__(list)

class datetime_gist(datetime):
    pass


class Comprobador():


    @staticmethod
    def time2datetime(lista):
        dia=actual.day - dia_resta  ##################################### ojito
        mes=actual.month
        año=actual.year
        return tuple((datetime_gist(año,
                                    mes,
                                    dia,
                                    parada.hour,
                                    parada.minute,
                                    parada.second) for parada in lista))

    @staticmethod
    def datetime2datetimegist(dt):
        return datetime_gist(dt.year,
                             dt.month,
                             dt.day,
                             dt.hour,
                             dt.minute,
                             dt.second,
                             dt.microsecond)
    
    def __init__(self,
                 linea,
                 horario_linea,
                 Δt_hasta_parada_control_moda,
                 Δt_hasta_parada_control_min=None,
                 Δt_hasta_parada_control_max=None,
                 reduccion=3/5,
                 ampliacion=2):
        self.linea=linea
        self.horario_linea = Comprobador.time2datetime(horario_linea)
        self.Δt_hasta_parada_control_moda = Δt_hasta_parada_control_moda
        self.Δt_hasta_parada_control_min = (
            Δt_hasta_parada_control_min if Δt_hasta_parada_control_min
            else reduccion*Δt_hasta_parada_control_moda)
        self.Δt_hasta_parada_control_max = (
            Δt_hasta_parada_control_max if Δt_hasta_parada_control_max
            else ampliacion*Δt_hasta_parada_control_moda)

    def calcula_salida_fuera_horario(self,
                                     paso_cabecera_SAE,
                                     paso_parada_siguiente):
        salida_teorica_moda = (paso_parada_siguiente
                               - self.Δt_hasta_parada_control_moda)
        if salida_teorica_moda > paso_cabecera_SAE:
            #Es un valor válido, después del registro de paso del SAE.
            salida_teorica_moda = Comprobador.datetime2datetimegist(
                salida_teorica_moda)
            salida_teorica_moda.linea = self.linea
            return salida_teorica_moda
        else:
            #Probamos a ver si es posible con el Δt mínimo entre
            #paradas.
            salida_teorica_minima = (paso_parada_siguiente
                                     - self.Δt_hasta_parada_control_min)
            if salida_teorica_minima > paso_cabecera_SAE:
                #Ok, es posible, con suerte.
                salida_teorica_minima = Comprobador.datetime2datetimegist(
                    salida_teorica_minima)
                salida_teorica_minima.linea = self.linea
                return salida_teorica_minima
            else:
                #No es posible. O bien los datos del SAE no son
                #correctos, o el bus tarda a veces menos entre las paradas.
                info(pretty_output("Los datos del SAE reflejan que en la línea"
                     " {} el bus pasó por cabecera a las "
                     "{} y por la parada "
                     "siguiente a las {}, "
                     " pero el Δt mínimo entre ambas es de ".format(
                         self.linea,
                         paso_cabecera_SAE.ctime(),
                         paso_parada_siguiente.ctime())))
                salida_teorica_moda = Comprobador.datetime2datetimegist(
                    salida_teorica_moda)
                salida_teorica_moda.linea = self.linea
                return salida_teorica_moda

    def __call__(self,
                 paso_cabecera_SAE,
                 paso_parada_siguiente,
                 cero_segundos=time()):
        punto_insercion=bisect_left(self.horario_linea, paso_cabecera_SAE)
        try:
            salida_teorica_horario = self.horario_linea[punto_insercion]
        except IndexError:
            salida_teorica_horario = self.horario_linea[-1]
            info(pretty_output(
                "El bus de la linea {} está registrado que pasó por"
                " cabecera a {}, pero la última salida "
                "programada, que será la que tomemos como teórica fue a "
                "{}".format(
                    self.linea,
                    paso_cabecera_SAE.ctime(),
                    salida_teorica_horario.ctime())))
        if (#No nos creemos que el bus haya tardado tanto, salió más tarde
            paso_parada_siguiente-salida_teorica_horario
            > self.Δt_hasta_parada_control_max
            or #No nos creemos que el bus tardara tan poco, salió antes
            paso_parada_siguiente-salida_teorica_horario
            < self.Δt_hasta_parada_control_min):
            return self.calcula_salida_fuera_horario(paso_cabecera_SAE,
                                                     paso_parada_siguiente)
        else:
            salida_teorica_horario.linea = self.linea
            return salida_teorica_horario

(comprueba_3,
 comprueba_13,
 comprueba_17,
 comprueba_100_sardi,
 comprueba_100_valde)= starmap(Comprobador,
                               ((3,
                                 horarios.paradas_3,
                                 timedelta(minutes=0, seconds=40)),
                                (13,
                                 horarios.paradas_13,
                                 timedelta(minutes=1, seconds=17)),
                                (17,
                                 horarios.paradas_17,
                                 timedelta(minutes=1, seconds=4)),
                                (100,
                                 horarios.paradas_C_Int_Sardinero,
                                 timedelta(minutes=1, seconds=36)),
                                (100,
                                 horarios.paradas_C_Int_Valdecilla,
                                 timedelta(minutes=2, seconds=00))))



def entrecomilla(s):
    return "".join("'", s, "'")

def datetime2time(fecha):
    return time(fecha.hour, fecha.minute, fecha.second)

def comparatiempos(t1, t2): #devuelve da diferencia ABSOLUTA
    t1=t1.hour*3600 + t1.minute*60 + t1.second
    t2=t2.hour*3600 + t2.minute*60 + t2.second
    diferencia= abs(t1 - t2)
    horas, resto=divmod(diferencia, 3600)
    minutos, segundos =divmod(resto, 60)
    return time(horas, minutos, segundos)

def restatiempos(t1, t2): 
    t1=t1.hour*3600 + t1.minute*60 + t1.second
    t2=t2.hour*3600 + t2.minute*60 + t2.second
    diferencia= t1 - t2
    horas, resto=divmod(diferencia, 3600)
    minutos, segundos =divmod(resto, 60)
    return time(horas, minutos, segundos)

def ordena_diccionario(dic):
    for k,v in dic.items():
        dic[k] = tuple(x for x,y in groupby(sorted(v)))
    return dic

def filtra_llegadas(lista, margen_tiempo=timedelta(minutes=2)):
    #Creo que hay cierta redundancia en los filtros.
    devuelve_lista=list()
    elemento_anterior=datetime(1900, 1, 1, 0, 0, 0)
    for elemento in lista:
        if elemento-elemento_anterior > margen_tiempo:
            devuelve_lista.append(elemento)
            elemento_anterior = elemento
    return devuelve_lista

##def filtra_salidas(lista, margen_tiempo=timedelta(minutes=2)):
##    devuelve_lista=list()
##    elemento_anterior=datetime(1900, 1, 1, 0, 0, 0)
##    for elemento in lista:
##        if elemento-elemento_anterior <= margen_tiempo:
##            devuelve_lista.pop()
##        devuelve_lista.append(elemento)
##        elemento_anterior = elemento
##    return devuelve_lista

Números_de_paradas = namedtuple("Números_de_paradas",
                                ("Sardinero",
                                 "Sardinero1",
                                 "Sardinero2",
                                 "Valdecilla",
                                 "Avda_Valdecilla",
                                 "San_Fernando",
                                 "Vega_Lamera",
                                 "Cajo2",
                                 "TQuevedo22",
##                                 "Albericia18",
                                 "Pedro_S_Martin_8",
                                 "ies_llamas",
                                 "san_fernando_vuelta"))
def genera_informe(
    fecha_inicio = None,
    fecha_fin = None,
    números_de_paradas = Números_de_paradas(Sardinero=516,
                                            Sardinero1=511,
                                            Sardinero2=515,
                                            Valdecilla=509,
                                            Avda_Valdecilla=512,
                                            San_Fernando=11,
                                            Vega_Lamera=171,
                                            Cajo2=78,
                                            TQuevedo22=46,
##                                            390,
                                            Pedro_S_Martin_8=436,
                                            ies_llamas=194,
                                            san_fernando_vuelta=44)):

    (llegadas_sardinero,
     llegadas_valdecilla,
     salidas_sardinero,
     salidas_valdecilla,
     resultados) = create_objects(Dict_de_listas, 5)

    def comprueba_llegada_intercambiador(num_parada_interc,
                                         lista_llegadas, linea):
        return (parada == num_parada_interc
                and (num_parada_interc != linea_anterior[cols.parada]
                     or (instante-lista_llegadas[linea][-1] > un_minuto
                         if len(lista_llegadas[linea]) else True)))

    comprueba_llegada_valdecilla = partial(comprueba_llegada_intercambiador,
                                           números_de_paradas.Valdecilla,
                                           llegadas_valdecilla)

    comprueba_llegada_sardinero = partial(comprueba_llegada_intercambiador,
                                          números_de_paradas.Sardinero,
                                          llegadas_sardinero)

    comprueba_llegada_avda_valdecilla = partial(
        comprueba_llegada_intercambiador,
        números_de_paradas.Avda_Valdecilla,
        llegadas_valdecilla)

    comprueba_llegada_sardinero1 = partial(comprueba_llegada_intercambiador,
                                           números_de_paradas.Sardinero1,
                                           llegadas_sardinero)

    if not (fecha_inicio and fecha_fin):
        fecha_inicio = datetime(actual.year,
                                actual.month,
                                actual.day-dia_resta,
                                6,
                                0,
                                0)
        fecha_fin=datetime(actual.year,
                           actual.month,
                           actual.day-dia_resta,
                           23,
                           0,
                           0)
    queries = ("CREATE TEMPORARY TABLE pasos_utiles AS (SELECT Linea, Coche, "
               "Viaje, Parada, Instante, Nombre "
               "FROM `pasos_parada` "
               "WHERE Instante BETWEEN '{0}' AND '{1}' "
               "AND parada IN {2})".format(fecha_inicio,
                                           fecha_fin,
                                           tuple(números_de_paradas)),
               "CREATE TEMPORARY TABLE viajes_directos AS (SELECT Linea, "
               "Coche, Viaje "
               "FROM `pasos_parada` "
               "WHERE Instante between '{0}' AND '{1}' "
               "AND (parada IN (11, 44) "
               "AND linea IN (3,17)) or (parada in (171, 194) and linea in (8,9)))".format(fecha_inicio,
                                             fecha_fin),
               "SELECT * FROM pasos_utiles "
               "WHERE NOT EXISTS (SELECT * FROM viajes_directos "
               "WHERE viajes_directos.Linea=pasos_utiles.Linea "
               "AND viajes_directos.Viaje=pasos_utiles.Viaje "
               "AND pasos_utiles.Coche=viajes_directos.Coche) "
               "ORDER BY Linea, Coche, Instante")
    for q in queries:
        print(q)
    with contextlib.closing(MySQLdb.connect(user='root',
                                            password='madremia902',
                                            host='193.144.208.142',
                                            port=3306,
                                            database='autobuses'
                                            )) as conexion:
        with contextlib.closing(conexion.cursor()) as cursor:
            exhaust_map(cursor.execute, queries)
            datos_row=tuple(cursor)

    # lineas 91  repuente sardinero repuente y 92 cueto sardinero cueto

    Columnas = namedtuple("Columnas",
                          ("linea",
                           "coche",
                           "viaje",
                           "parada",
                           "instante",
                           "nombre"))
    cols = Columnas(*range(6))
    un_minuto = timedelta(minutes=1)
    for linea_bus, rows in groupby(datos_row,
                                   lambda fila: (fila[cols.linea],
                                                 fila[cols.coche])):
        linea=linea_bus[0]
##        iterador_filas=iter(rows)
##        linea_anterior=next(iterador_filas)
        linea_anterior = (None,
                          None,
                          None,
                          None,
                          datetime_gist(1999,
                                        1,
                                        1,
                                        0,
                                        0,
                                        0,
                                        0),
                          None,
                          None)
##        first_loop = True
        for row in rows:
##            debug(str(row))
##            debug(str(row[4]))
##            debug("\n")
            instante=datetime_gist(row[cols.instante].year,
                                   row[cols.instante].month,
                                   row[cols.instante].day,
                                   row[cols.instante].hour,
                                   row[cols.instante].minute,
                                   row[cols.instante].second,
                                   row[cols.instante].microsecond)
            instante_anterior=datetime_gist(
                linea_anterior[cols.instante].year,
                linea_anterior[cols.instante].month,
                linea_anterior[cols.instante].day,
                linea_anterior[cols.instante].hour,
                linea_anterior[cols.instante].minute,
                linea_anterior[cols.instante].second,
                row[cols.instante].microsecond)
            instante.linea=linea
            instante_anterior.linea=linea
            parada=row[cols.parada]
            if linea==100:
                if comprueba_llegada_avda_valdecilla(100):
                    llegadas_valdecilla[100].append(instante)
                elif parada==números_de_paradas.San_Fernando:
                    salidas_valdecilla[100].append(comprueba_100_valde(
                        instante_anterior,instante))
##            if linea==100:
                elif comprueba_llegada_sardinero(100):
                    llegadas_sardinero[100].append(instante)
                elif parada==números_de_paradas.Vega_Lamera:
                    salidas_sardinero[100].append(comprueba_100_sardi(
                        instante_anterior,instante))
            elif linea==3:
                if comprueba_llegada_valdecilla(3):
                    llegadas_valdecilla[3].append(instante)
                elif parada==números_de_paradas.Cajo2:
                    salidas_valdecilla[3].append(comprueba_3(
                        instante_anterior,instante))
            elif linea==13:
                if comprueba_llegada_valdecilla(13):
                    llegadas_valdecilla[13].append(instante)
                elif parada==números_de_paradas.TQuevedo22:
                    salidas_valdecilla[13].append(comprueba_13(
                        instante_anterior,instante))
            elif linea==14:
                if comprueba_llegada_valdecilla(14):
                    llegadas_valdecilla[13].append(instante)
                elif parada==números_de_paradas.Avda_Valdecilla:
                    salidas_valdecilla[13].append(instante)
            elif linea==17:
                #Cambios 17:
                    #Ahora acaba en Avda. Valdecilla, y comienza en Valdecilla.
                    #La primera parada tras salir es Pedro San Martín.
                if comprueba_llegada_avda_valdecilla(17):
                    llegadas_valdecilla[17].append(instante)
                elif parada==números_de_paradas.Pedro_S_Martin_8:
                    salidas_valdecilla[17].append(comprueba_17(
                        instante_anterior,instante))
            elif linea==20:
                if comprueba_llegada_sardinero1(20):
                    llegadas_sardinero[20].append(instante)
                elif parada==números_de_paradas.Sardinero2:
                    if (linea_anterior[cols.parada]
                        == números_de_paradas.Sardinero2
                        and instante-salidas_sardinero[20][-1]
                        < un_minuto):
                        #Ya estaba registrada la salida, pero unos segundos
                        #prematuramente.
                        salidas_sardinero[20].pop()
                    salidas_sardinero[20].append(instante)
            elif linea==8:
                if comprueba_llegada_sardinero1(8):
                    llegadas_sardinero[8].append(instante)
                elif parada==números_de_paradas.Sardinero2:
                    if (linea_anterior[cols.parada]
                        == números_de_paradas.Sardinero2
                        and instante-salidas_sardinero[8][-1]
                        < un_minuto):
                        #Ya estaba registrada la salida, pero unos segundos
                        #prematuramente.
                        salidas_sardinero[8].pop()
                    salidas_sardinero[8].append(instante)
            elif linea==9:
                if comprueba_llegada_sardinero1(9):
                    llegadas_sardinero[9].append(instante)
                elif parada==números_de_paradas.Sardinero2:
                    if (linea_anterior[cols.parada]
                        == números_de_paradas.Sardinero2
                        and instante-salidas_sardinero[9][-1]
                        < un_minuto):
                        #Ya estaba registrada la salida, pero unos segundos
                        #prematuramente.
                        salidas_sardinero[9].pop()
                    salidas_sardinero[9].append(instante)
#            elif linea==9:
#                if parada==números_de_paradas.Sardinero1:
#                    if (linea_anterior[cols.parada]
#                        ==números_de_paradas.Sardinero1
#                        and instante-salidas_sardinero[92][-1]
#                        < un_minuto):
#                        #Si vienen dos registros de Sard1 seguidos,
#                        #hay que quedarse con el primero como llegada de la 91,
#                        #y con el segundo como salida de la 92.
#                        salidas_sardinero[92].pop()
#                    else:
#                        llegadas_sardinero[91].append(instante)
#                    salidas_sardinero[92].append(instante)
#                elif parada==números_de_paradas.Sardinero2:
#                    if (linea_anterior[cols.parada]
#                        ==números_de_paradas.Sardinero2
#                        and instante-salidas_sardinero[91][-1]
#                        < un_minuto):
#                        #Si vienen dos registros de Sard2 seguidos,
#                        #hay que quedarse con el primero como llegada de la 92,
#                        #y con el segundo como salida de la 91.
#                        #No ocurre en la pequeña muestra que he analizado, pero
#                        #no me cuesta mucho añadir la comprobación.
#                        salidas_sardinero[91].pop()
#                    else:
#                        llegadas_sardinero[92].append(instante)
#                    salidas_sardinero[91].append(instante)
            elif linea in (1,2,72):
                if parada==números_de_paradas.Sardinero1:
                    salidas_sardinero['resto'].append(instante)
                elif parada==números_de_paradas.Valdecilla:
                    salidas_valdecilla['resto'].append(instante)
            linea_anterior=row
##            first_loop = False
##    debug(pretty_output("llegadas_sardinero", llegadas_sardinero[100]))
##    debug(pretty_output("salidas_sardinero", salidas_sardinero[100]))
##    debug(pretty_output("llegadas_valdecilla", llegadas_valdecilla[100]))
##    debug(pretty_output("salidas_valdecilla", salidas_valdecilla[100]))
    lineas_acaban_sardinero = (20, 8) #(91, 92, 20)
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

##    debug(pretty_output("llegadas_sardinero_ordenadas", salidas_sardinero[100]))
##    debug(pretty_output("salidas_sardinero_ordenadas", salidas_sardinero[100]))
##    debug(pretty_output("llegadas_valdecilla_ordenadas", salidas_sardinero))
##    debug(pretty_output("salidas_valdecilla_ordenadas", salidas_valdecilla[100]))    
    
    
    # generamos unas listas con las corresondencias para cada intercambiador

##    resultados = {
##        "Valdecilla_barrios": [],
##        "Barrios_Valdecilla": [],
##        "Sardinero_barrios": [],
##        "Barrios_Sardinero": []
##        }
    
    llegadas_valdecilla[100]=filtra_llegadas(llegadas_valdecilla[100])
##    debug(pretty_output("llegadas_valdecilla_filtradas", llegadas_valdecilla[100]))
    for instante_llegada_central in llegadas_valdecilla[100]:
        for linea in lineas_acaban_valdecilla:
            try:
                posición_salida_linea = bisect(salidas_valdecilla[linea],
                                               instante_llegada_central)
                instante_salida_linea = (
                    salidas_valdecilla[linea][posición_salida_linea])
                tiempo_espera = instante_salida_linea-instante_llegada_central
                resultados["Valdecilla_barrios"].append(
                    (linea,# sentido
                     instante_salida_linea.linea,# sacamos la propiedad linea
                     instante_salida_linea,
                     instante_llegada_central,
                     tiempo_espera))
            except IndexError:
                pass
##    debug(pretty_output('resultados["Valdecilla_barrios"]',
##                        resultados["Valdecilla_barrios"]))
    for linea in lineas_acaban_valdecilla:
        for instante_llegada in llegadas_valdecilla[linea]:
            try:
                posición_salida_central = bisect(salidas_valdecilla[100],
                                                 instante_llegada)
                instante_salida_central = (
                    salidas_valdecilla[100][posición_salida_central])
                tiempo_espera = instante_salida_central - instante_llegada
                if tiempo_espera<timedelta(hours=2):
                    resultados["Barrios_Valdecilla"].append(
                        (linea,# sentido
                         instante_llegada.linea,# sacamos la propiedad linea
                         instante_llegada,
                         instante_salida_central,
                         tiempo_espera))
            except IndexError:
                pass
##    debug(pretty_output('resultados["Barrios_Valdecilla"]',
##                        resultados["Barrios_Valdecilla"]))
            
    salidas_sardinero[9]=filtra_llegadas(salidas_sardinero[9],
                                          timedelta(minutes=1)) #Creo que ya
                                                                #hace falta.
    llegadas_sardinero[9]=filtra_llegadas(llegadas_sardinero[9],
                                           timedelta(minutes=1))
    
    llegadas_sardinero[8]=filtra_llegadas(llegadas_sardinero[8],
                                           timedelta(minutes=1))
    
    llegadas_sardinero[8]=filtra_llegadas(llegadas_sardinero[8],
                                           timedelta(minutes=1))
    #juntamos las líneas 91 y 20 que van hacia monte porque estan "coordinadas"
    salidas_sardinero[20] = sorted(chain(salidas_sardinero[9],
                                         salidas_sardinero[20]))
    llegadas_sardinero[20] = sorted(chain(llegadas_sardinero[9],
                                          llegadas_sardinero[20]))
    llegadas_sardinero[100]=filtra_llegadas(llegadas_sardinero[100])
    for instante_llegada_central in llegadas_sardinero[100]:
        for linea in lineas_acaban_sardinero:
            try:
                posición_salida_linea = bisect(salidas_sardinero[linea],
                                               instante_llegada_central)
                instante_salida_linea = (
                    salidas_sardinero[linea][posición_salida_linea])
                tiempo_espera = (
                    instante_salida_linea - instante_llegada_central)
                resultados["Sardinero_barrios"].append(
                    (linea,# sentido
                     instante_salida_linea.linea,# sacamos la propiedad linea
                     instante_salida_linea,
                     instante_llegada_central,
                     tiempo_espera))
            except IndexError:
                pass
##    debug(pretty_output('resultados["Sardinero_barrios"]',
##                        resultados["Sardinero_barrios"]))

            
    for linea in lineas_acaban_sardinero:
        for instante_llegada in llegadas_sardinero[linea]:
            try:
                posición_salida_central = bisect(salidas_sardinero[100],
                                                 instante_llegada)
                instante_salida_central = (
                    salidas_sardinero[100][posición_salida_central])
                tiempo_espera = instante_salida_central - instante_llegada
                if tiempo_espera<timedelta(hours=2):
                    resultados["Barrios_Sardinero"].append(
                        (linea,# sentido
                         instante_llegada.linea,# sacamos la propiedad linea
                         instante_llegada,
                         instante_salida_central,
                         tiempo_espera))
            except IndexError as e:
                print(e)
                pass
##    debug(pretty_output('resultados["Barrios_Sardinero"]',
##                        resultados["Barrios_Sardinero"]))

    #Guarda, para una línea, lo que es necesario para poder cortarla en dos al
    #dibujarla cuando no coordina con el intercambiador
##    Caract_corte = namedtuple("Características_corte",
##                                       ("hora", "color"))

    def genera_tablas_intercambiador(trayecto,
                                     caso_particular,
                                     outlayers_time='15 minutes',
                                     tiempo_no_valido="30 minutes",
                                     direccion_centro=False,
                                     cortes={3: 14,
                                             17: 14,
                                             8: 14,
                                             9: 14},
                                     colores=dict(zip((3,
                                                       13,
                                                       14,
                                                       17,
                                                       8,
                                                       9,
                                                       20),
                                                      ("b",
                                                       "g",
                                                       "r",
                                                       "c",
                                                       "g",
                                                       "m",
                                                       "y",
                                                       "k")))):
        def media_espera(objeto):
            return reduce(timedelta.__add__,objeto)/len(objeto)

        def comprueba_media_mas_50_porciento(row):
##            return True
            return 1 if row['espera']>un_minuto*6 else 0
#            return 1 if row['espera']>1.5*table_intercambiador_barrios_espera[
#                'espera'].get(int(row['linea'])) else 0
        
        def comprueba_outlayers(row):
            return 1 if row['espera'] > pd.Timedelta(outlayers_time) else 0

        def comprueba_gordos(row):
            return 1 if row['espera'] > pd.Timedelta(tiempo_no_valido) else 0
        
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
                        posición_salida_otra_linea = bisect(lista_bisect,
                                                            row["salida"])
                        # ojo que salida es llegada
                        instante_salida_otra_linea = (
                            lista_bisect[posición_salida_otra_linea])
                        tiempo_espera = (
                            instante_salida_otra_linea - row["salida"])
                        if tiempo_espera < row["espera"]:
                            df.iloc[index,df.columns.get_loc('alternativa')]=(
                                instante_salida_otra_linea.linea)
                            df.iloc[index,df.columns.get_loc(
                                'espera_alternativa')]=tiempo_espera
                            
                    except IndexError:
                        pass
                # ponemos las columnas en el dataframe teniendo en cuenta que
                #el de outlayers y el de + 50 son diferentes y devolvemos las
                #columnas a mostrar
                try:
                    df.columns=['Conexión',
                                'Línea',
                                'Paso autobús',
                                'Línea central',
                                'Espera',
                                '',
                                '',
                                'Línea alternativa',
                                'Espera alternativa']
                except:
                    df.columns=['Conexión',
                                'Línea',
                                'Paso autobús',
                                'Línea central',
                                'Espera',
                                '',
                                'Línea alternativa',
                                'Espera alternativa']
                return (['Conexión',
                         'Espera Media',
                         'Datos empleados',
                         'Supera media + 50%'],
                        ['Conexión',
                         'Línea',
                         'Paso autobús',
                         'Línea central',
                         'Espera',
                         'Línea alternativa',
                         'Espera alternativa'])
            else: # SI NO ES DIRECCION CENTRO HAy que poner las columnas sin
                #las alternativas
                try: # para poner 7 columnas
                    df.columns=['Conexión',
                                'Línea',
                                'Paso autobús',
                                'Línea central',
                                'Espera',
                                '',
                                '']
                except: # para poner el caso de 6 columnas volvemos de la
                    #excepcion anterior
                    df.columns=['Conexión',
                                'Línea',
                                'Paso autobús',
                                'Línea central',
                                'Espera',
                                '']
                return (['Conexión',
                         'Espera Media'
                         ,'Datos empleados',
                         'Supera media + 50%'],
                        ['Conexión',
                         'Línea',
                         'Paso autobús',
                         'Línea central',
                         'Espera']) # devolvemos los nombres a mostrar

        
        # agregamos los datos con pandas :)
        df_interc_barrios = pd.DataFrame(
            resultados[trayecto],
            columns=['linea',
                     'linea_real',
                     'salida',
                     'llegada_central',
                     'espera'])
        # eliminamos los reprtidos de la 13 que tiene el doble de frecuencia
        indices_duplicados=df_interc_barrios[
            df_interc_barrios.linea==caso_particular].duplicated(['linea',
                                                                  'salida'],
                                                                 keep='first')
        df_interc_barrios.drop(
            df_interc_barrios.index[
                list(
                    indices_duplicados[
                        indices_duplicados != True].index)], inplace=True)
        #retiramos los valores muy, muy, gordos completamente
        df_interc_barrios['gordos']=df_interc_barrios.apply(
            comprueba_gordos,axis=1)
        resultado_gordos=df_interc_barrios[df_interc_barrios.gordos==1]
        indices_gordos=df_interc_barrios[
            df_interc_barrios.gordos==1].index.values
        df_interc_barrios.drop(df_interc_barrios.index[indices_gordos],
                               inplace=True)
        del df_interc_barrios["gordos"]
        df_interc_barrios.reset_index(inplace=True, drop=True)
        # retiramos los outlyers a un df aparte
        df_interc_barrios['outlayers']=df_interc_barrios.apply(
            comprueba_outlayers,axis=1)
        resultado_outlayers=df_interc_barrios[df_interc_barrios.outlayers==1]
        indices_outlayers=df_interc_barrios[
            df_interc_barrios.outlayers==1].index.values
        df_interc_barrios.drop(df_interc_barrios.index[indices_outlayers],
                               inplace=True)
        table_intercambiador_barrios_espera=pd.pivot_table(
            df_interc_barrios,
            values=['espera'],
            index=['linea'],
            aggfunc=media_espera)
        #añadimos una columna para reflejar los tiempos mayores al 50% de la
        #media
        df_interc_barrios['espera_mas_50']=df_interc_barrios.apply(
            comprueba_media_mas_50_porciento,axis=1)
        
        table_intercambiador_barrios_cuenta_50=pd.pivot_table(
            df_interc_barrios,
            values=['espera_mas_50'],
            index=['linea'],
            aggfunc=[np.sum])
        table_intercambiador_barrios_cuenta=pd.pivot_table(
            df_interc_barrios,
            values=['espera_mas_50'],
            index=['linea'],
            aggfunc=[np.size])
        resultado = pd.concat([table_intercambiador_barrios_espera,
                             table_intercambiador_barrios_cuenta,
                             table_intercambiador_barrios_cuenta_50],
                            axis=1).reset_index()
        resultado.columns = ['Conexión',
                             'Espera Media',
                             'Datos empleados',
                             'Supera media + 50%']
        resultado_mas_50 = df_interc_barrios[
            df_interc_barrios.espera_mas_50==1]
        #hay que comprobar con estas conexiones perdidas si pudieron coger
        #un 1 o un 2 o un 7 en el caso de valdecilla
        alternativas_horarios_dataframe(resultado_mas_50)
        columnas_mostrar = alternativas_horarios_dataframe(resultado_outlayers)
        #guardamos en csv
        # pintamos espera en minutos
        df_interc_barrios['espera minutos'] = (df_interc_barrios['espera']
                                               / pd.Timedelta('1 minute'))
        df_interc_barrios['hora salida']=[
            float(pd.Timestamp.strftime(item, '%H.%M'))
            for item in df_interc_barrios['salida']]
        grupo = df_interc_barrios.sort_values(
            by=['salida']).groupby('linea_real')
        ncols = 1
        nrows = 1 #int(np.ceil(grupo.ngroups/ncols))
##        fig, axes = plt.subplots(nrows=nrows, ncols=ncols)
        fig = plt.figure(figsize=(10,5))
        ax = plt.gca()
##        legend = ax.get_legend()
        plt.grid(True)
        handles = []
        labels = []
        for key in grupo.groups.keys():
            if key in cortes:
##                x=grupo.get_group(key)['hora salida']
##                debug(pretty_output("key", key))
##                debug(pretty_output("x", x))
##                debug(pretty_output("type(x)", type(x)))
                franja_mañana = (grupo.get_group(key)["hora salida"]
                                 < cortes[key])
                franja_tarde = (grupo.get_group(key)["hora salida"]
                                >= cortes[key])
##                debug(str(franja_mañana))
                grupo_mañana = grupo.get_group(key)[franja_mañana]
                grupo_tarde = grupo.get_group(key)[franja_tarde]
                x_s = (g["hora salida"] for g in (grupo_mañana, grupo_tarde))
                y_s = (g["espera minutos"] for g in (grupo_mañana, grupo_tarde))
                for x, y in zip(x_s, y_s):
                    plt.scatter(x,y, color=colores[key])
                    handle, = plt.plot(x,y, color=colores[key])
            else:
                x = grupo.get_group(key)['hora salida']
                y = grupo.get_group(key)['espera minutos']
                plt.scatter(x,y, color=colores[key])
                handle, = plt.plot(x,y, color=colores[key])
            handles.append(handle)
            labels.append(key)
##            print(type(ultimo_plot))
##            artistas[str(key)] = ultimo_plot
##            ultimo_plot.set_label=str(key)
            plt.ylim(0,20)
            plt.xlim(7,23.5)
##        print(ax.get_legend_handles_labels())
        plt.xlabel('Hora del día')
        plt.ylabel('Minutos de transbordo')
        plt.legend(handles, labels,
                   loc=1,
                   title='Líneas') #, 
        plt.savefig(directorio+trayecto)
        return ((resultado,columnas_mostrar[0]),
                (resultado_mas_50.sort_values(by=["Conexión",
                                                  "Línea",
                                                  "Línea central"]),
                 columnas_mostrar[1]),
                (resultado_outlayers.sort_values(by=["Conexión",
                                                     "Línea",
                                                     "Línea central"]),
                 columnas_mostrar[1]))

    #generamos el informe
    def rellena_datos_elemento_informe(intercambiador_sentido,
                                       titulo,
                                       nombre_foto):
        def formatea_linea(numero, nombre = {3:'Ojaiz línea 3',
                                             13:'Lluja líneas 13 y 14',
                                             17:'Corbán línea 17',
                                             8:'Cueto línea 8',
                                             9: 'Monte linea 9',
                                             20:'Monte líneas 9 y 20'}):
            return nombre[numero]

        def formatea_hora(hora):
            return hora.strftime('%H:%M:%S')

        def formatea_espera(espera):
            horas, resto = divmod(pd.Timedelta(espera).seconds,3600)
            minutos, segundos = divmod(resto, 60)
            return "".join((str(horas).rjust(2, '0'),':',
                            str(minutos).rjust(2, '0'),':',
                            str(segundos).rjust(2, '0')))
        
        def pandas_html(tabla, columnas, es_tabla_medias=False):
            lista_formatos_base=[formatea_linea,
                                 None,
                                 formatea_hora,
                                 formatea_hora,
                                 None]
            formatos_no_medias=lista_formatos_base + list(
                repeat(None, len(columnas)-len(lista_formatos_base)))
            formateadores = [formatea_linea,
                             formatea_espera,
                             None,
                             None] if es_tabla_medias else formatos_no_medias
            return tabla.to_html(classes='paleBlueRows',
                                 columns=columnas, index=False,
                                 justify='center',
                                 formatters=formateadores)
        
        return textos_html_informe.apartado_informe.format(
            tabla_medias = pandas_html(intercambiador_sentido[0][0],
                                       intercambiador_sentido[0][1],
                                       True),
            titulo = titulo,
            tabla_supera_media = pandas_html(intercambiador_sentido[1][0],
                                             intercambiador_sentido[1][1]),
            grafico = "".join((nombre_foto,'.png')),
            tabla_anomalos = pandas_html(intercambiador_sentido[2][0],
                                         intercambiador_sentido[2][1]))

    #elemento para guardar las imagenes
    sardinero_centro  =genera_tablas_intercambiador('Barrios_Sardinero',
                                                    0,
                                                    direccion_centro=True)
    sardinero_barrios = genera_tablas_intercambiador('Sardinero_barrios', 0)
    valdecilla_centro = genera_tablas_intercambiador('Barrios_Valdecilla',
                                                     0,
                                                     direccion_centro=True)
    valdecilla_barrios = genera_tablas_intercambiador('Valdecilla_barrios', 0)
    texto_completo_informe = textos_html_informe.plantilla_web_cuerpo
    titulos = ('BARRIOS -&gt; VALDECILLA -&gt; CENTRO',
               'CENTRO -&gt; VALDECILLA -&gt; BARRIOS',
               'BARRIOS -&gt; SARDINERO -&gt; CENTRO',
               'CENTRO -&gt; SARDINERO -&gt; BARRIOS')
    tablas = (valdecilla_centro,
              valdecilla_barrios,
              sardinero_centro,
              sardinero_barrios)
    nombres_fotos = ('Barrios_Valdecilla',
                     'Valdecilla_barrios',
                     'Barrios_Sardinero',
                     'Sardinero_barrios')
    texto_exportar = (textos_html_informe.plantilla_web_estilos
                      +texto_completo_informe.format(
                          dia=actual.day-dia_resta,
                          mes=actual.month,
                          ano=actual.year,
                          informe_completo="\n".join(
                              (map(rellena_datos_elemento_informe,
                                   tablas,
                                   titulos,
                                   nombres_fotos)))))
    with open(directorio+'informe{}{}{}_bis.html'.format(actual.year,
                                                         actual.month,
                                                         actual.day-dia_resta),
              'w') as file:
        print(texto_exportar, file=file)
    create_pdf(
        directorio+'informe{}{}{}_bis.html'.format(actual.year,
                                                   actual.month,
                                                   actual.day-dia_resta),
        directorio+'{}-{}-{}.pdf'.format(actual.year,
                                         actual.month,
                                         actual.day-dia_resta))

if __name__ == "__main__":
    genera_informe()
