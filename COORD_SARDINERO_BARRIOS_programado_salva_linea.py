
from openpyxl import Workbook
from openpyxl.compat import range
from openpyxl.utils import get_column_letter
from openpyxl import load_workbook
from datetime import timedelta, datetime,time
import os
##import mysql.connector
import contextlib
import bisect
import filtra_excel
from collections import namedtuple
import MySQLdb
from bisect import bisect
from functools import partial
from itertools import starmap, groupby, chain
import horarios
from collections import defaultdict
import pandas as pd
import numpy as np
import traceback
from functools import reduce
import textos_html_informe
##import pandas_profiling

dia_resta=1
class bar():
    
    hour = minute= second = None
    value = None
    
class datetime_gist(datetime):
    pass

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
números_de_paradas = Números_de_paradas(516, 511, 515, 509, 512, 11, 171, 78, 46, 390)

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

def time2datetime(lista):
    dia=datetime.now().day-dia_resta  ########################################################## ojito
    mes=datetime.now().month
    año=datetime.now().year
    return tuple((datetime_gist(año,mes,dia,parada.hour,parada.minute,parada.second) for parada in lista))

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

class Comprobador():
    
        

    def __init__(
        self,
        horario_linea,
        tiempo_hasta_parada_control,
        margen_tiempo,
        linea
        ):
        self.horario_linea = time2datetime(horario_linea)
        self.tiempo_hasta_parada_control = tiempo_hasta_parada_control
        self.margen_tiempo = margen_tiempo
        self.linea=linea

    def __call__(self, salida_row_anterior, salida, cero_segundos=time()):
##        print('---------')
##        print(salida_row_anterior)
##        print(salida)
        punto_insercion=bisect(self.horario_linea,(salida-self.tiempo_hasta_parada_control))
        diferencia=(salida-self.tiempo_hasta_parada_control)-self.horario_linea[punto_insercion]
        diferencia2=(salida-self.tiempo_hasta_parada_control)-self.horario_linea[punto_insercion-1]
##        print(diferencia)
##        print(self.horario_linea[punto_insercion])
##        print(self.horario_linea[punto_insercion-1])
##        print(abs(diferencia)>self.margen_tiempo)
        if abs(diferencia)>self.margen_tiempo and abs(diferencia2)>self.margen_tiempo: #se perdio la conexion y sale a la hora de paso por valdecilla
##            print(salida_row_anterior)
            salida_row_anterior.linea=self.linea
            return salida_row_anterior
        elif abs(diferencia)>abs(diferencia2):
            #volvemos a comprobar la salida anterior con la teorica para ver cual es mayor y nos quedamos con la mayor
##            print(self.horario_linea[punto_insercion-1] if (self.horario_linea[punto_insercion-1]>salida_row_anterior) else salida_row_anterior)
            self.horario_linea[punto_insercion-1].linea=self.linea
            return self.horario_linea[punto_insercion-1] if (self.horario_linea[punto_insercion-1]>salida_row_anterior) else salida_row_anterior
        else:
##            print(self.horario_linea[punto_insercion] if (self.horario_linea[punto_insercion]>salida_row_anterior) else salida_row_anterior)
            self.horario_linea[punto_insercion].linea=self.linea
            return self.horario_linea[punto_insercion] if (self.horario_linea[punto_insercion]>salida_row_anterior) else salida_row_anterior
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
            (horarios.paradas_3,timedelta(minutes=1, seconds=30), timedelta(minutes=6),3),
            (horarios.paradas_13,timedelta(minutes=2, seconds=0), timedelta(minutes=6),13),
            (horarios.paradas_17,timedelta(minutes=1, seconds=30), timedelta(minutes=6),17),
            (horarios.paradas_C_Int_Sardinero,timedelta(minutes=2, seconds=00), timedelta(minutes=6),100),
            (horarios.paradas_C_Int_Valdecilla,timedelta(minutes=3, seconds=00), timedelta(minutes=6),100)
            )
        )

# open the file
actual=datetime.now()
fecha_inicio=datetime(actual.year,actual.month,actual.day-dia_resta,6,0,0) #######################################
fecha_fin=datetime(actual.year,actual.month,actual.day-dia_resta,22,0,0)  #########################################
paradas_query = " or ".join(f"parada={parada}" for parada in números_de_paradas)
query = (f"SELECT * FROM `pasos_parada` where Instante between '{fecha_inicio}' and '{fecha_fin}' "
         f"and ({paradas_query}) "
         "ORDER BY Linea, Coche, Instante asc"
         )
print(query)

with contextlib.closing(MySQLdb.connect(user='root',
                                                password='madremia902',
                                                host='193.144.208.142',
                                                port=3306,
                                                database='autobuses')
                        ) as conexion:
    with contextlib.closing(conexion.cursor()) as cursor:
        cursor.execute(query)
        datos_row=tuple(cursor)

# lineas 91  repuente sardinero repuente y 92 cueto sardinero cueto de momento vacio todo

llegadas_sardinero={100:list(),91:list(),20:list(), 92: list()}
llegadas_valdecilla={100:list(),3:list(),13:list(),14:list(),17:list()}
salidas_sardinero={100:list(),91:list(),20:list(), 92: list(),'resto':list()}
salidas_valdecilla={100:list(),3:list(),13:list(), 14:list(),17:list(),'resto':list()}


for linea_bus, rows in groupby(datos_row, lambda fila: (fila[0], fila[1])):
    linea=linea_bus[0]
    iterador_filas=iter(rows)
    linea_anterior=next(iterador_filas)
    for row in iterador_filas:
        instante=datetime_gist(row[4].year,row[4].month,row[4].day,row[4].hour,row[4].minute, row[4].second, row[4].microsecond)
        instante_anterior=datetime_gist(linea_anterior[4].year,linea_anterior[4].month,linea_anterior[4].day,linea_anterior[4].hour,linea_anterior[4].minute, linea_anterior[4].second, row[4].microsecond)
        instante.linea=linea
        instante_anterior.linea=linea
        parada=row[3]
        if linea==100:
            if parada==números_de_paradas.Avda_Valdecilla:
                llegadas_valdecilla[100].append(instante)
            if parada==números_de_paradas.San_Fernando:
                salidas_valdecilla[100].append(comprueba_100_valde(instante_anterior,instante))
        if linea==100:
            if parada==números_de_paradas.Sardinero:
                llegadas_sardinero[100].append(instante)
            if parada==números_de_paradas.Vega_Lamera:
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
##            print(instante_llegada_central, ' ', linea)
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
            #print(traceback.format_exc())
##            print(instante_llegada, ' ', linea)
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
##            print(instante_llegada_central, ' ', linea)
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
##            print(instante_llegada, ' ', linea)
            pass
        


def genera_tablas_intercambiador(trayecto, caso_particular, outlayers_time='18 minutes', direccion_centro=False):
    def media_espera(objeto):
        return reduce(timedelta.__add__,objeto)/len(objeto)

    def comprueba_media_mas_50_porciento(row):
        return 1 if row['espera'] > 1.5*table_intercambiador_barrios_espera['espera'].get(int(row['linea'])) else 0
    
    def comprueba_outlayers(row):
        return 1 if row['espera'] > pd.Timedelta(outlayers_time) else 0

    
    # agregamos los datos con pandas :)
    dataframe_intercambiador_barrios=pd.DataFrame(resultados[trayecto],
                                              columns=['linea','linea_real','salida','llegada_central','espera'])

    # eliminamos los reprtidos de la 13 que tiene el doble de frecuencia

    indices_duplicados=dataframe_intercambiador_barrios[dataframe_intercambiador_barrios.linea == caso_particular ].duplicated(['linea', 'salida'],keep='first')
    dataframe_intercambiador_barrios.drop(
        dataframe_intercambiador_barrios.index[
            list(
                indices_duplicados[
                    indices_duplicados != True].index)], inplace=True)
    # retiramos los outlyers a un df aparte
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
    if direccion_centro:
        pass
    resultado_mas_50.columns=['Conexión','Línea','Paso autobús','Línea central','Espera','','']
    resultado_outlayers.columns=['Conexión','Línea','Paso autobús','Línea central','Espera','']
    columnas_mostrar=(['Conexión','Espera Media','Datos empleados','Supera media + 50%'],
              ['Conexión','Línea','Paso autobús','Línea central','Espera'])
    pd.concat([dataframe_intercambiador_barrios,resultado_outlayers]).to_csv(f"{trayecto}.csv")
    return ((resultado,columnas_mostrar[0]),
            (resultado_mas_50.sort_values(by=["Conexión", "Línea", "Línea central"]),columnas_mostrar[1]),
            (resultado_outlayers.sort_values(by=["Conexión", "Línea", "Línea central"]),columnas_mostrar[1]) )


#generamos el informe

def rellena_datos_elemento_informe(intercambiador_sentido,titulo):
    def formatea_linea(numero, nombre= {3:'Ojaiz línea 3',13:'Lluja líneas 13 y 14',17:'Corbán línea 17'
                                        ,92:'Cueto línea 9',20:'Monte líneas 9 y 20'}):
        return nombre[numero]

    def formatea_hora(hora):
        return hora.strftime('%H:%M:%S')
    
    def formatea_espera(espera):
##        print(pd.Timedelta(espera).seconds)
        horas, resto=divmod(pd.Timedelta(espera).seconds,3600)
        minutos, segundos = divmod(resto,60)
        return "".join((str(horas).rjust(2, '0'),':',str(minutos).rjust(2, '0'),':',str(segundos).rjust(2, '0')))
    
    def pandas_html(tabla, columnas, es_tabla_medias=False):
        formateadores= [formatea_linea,formatea_espera,None,None ] if es_tabla_medias else [formatea_linea,None,formatea_hora,formatea_hora,None]

        return tabla.to_html(classes='paleBlueRows',
                             columns=columnas, index=False,
                             justify='center',
                             formatters=formateadores)
    
    return textos_html_informe.apartado_informe.format(tabla_medias=pandas_html(intercambiador_sentido[0][0],intercambiador_sentido[0][1],True),
                                                titulo= titulo,
                                                tabla_supera_media=pandas_html(intercambiador_sentido[1][0],intercambiador_sentido[1][1]),
                                                tabla_anomalos=pandas_html(intercambiador_sentido[2][0],intercambiador_sentido[2][1]))

sardinero_centro=genera_tablas_intercambiador('Barrios_Sardinero', 0,True)
sardinero_barrios=genera_tablas_intercambiador('Sardinero_barrios', 0)
valdecilla_centro=genera_tablas_intercambiador('Barrios_Valdecilla', 0,True)
valdecilla_barrios=genera_tablas_intercambiador('Valdecilla_barrios', 0)

texto_completo_informe=textos_html_informe.plantilla_web_cuerpo

titulos=('BARRIOS -&gt; VALDECILLA -&gt; CENTRO'
         ,'VALDECILLA -&gt; CENTRO -&gt; BARRIOS'
         ,'BARRIOS -&gt; SARDINERO -&gt; CENTRO'
         ,'SARDINERO -&gt; CENTRO -&gt; BARRIOS')

tablas=(valdecilla_centro,valdecilla_barrios,sardinero_centro,sardinero_barrios)


texto_exportar=textos_html_informe.plantilla_web_estilos+texto_completo_informe.format(dia=actual.day,
                              mes=actual.month,
                              ano=actual.year,
                              informe_completo="\n".join((map(rellena_datos_elemento_informe,tablas,titulos))))

with open(f'informe{actual.year}{actual.month}{actual.day}.html','w') as file:
    print(texto_exportar, file=file)


##report=pandas_profiling.ProfileReport(sardinero_centro[2])
##report.to_file("example.html")
