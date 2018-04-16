from MySQLdb import connect as connecto_to_db
from contextlib import closing
from collections import namedtuple
from itertools import groupby
from datetime import timedelta
from logging import basicConfig, debug, info, error, DEBUG, ERROR
from tools import pretty_output
basicConfig(level=DEBUG)

#Es un generador, que devuelve un iterador sobre los viajes detectados.
def encuentra_viajes(
    línea,
    viaje,
    inicio, #"2018-02-03T06:00:00"
    fin, #"2018-03-30T23:59:59"
    laborables=True,
    festivos=True,
    petición="""SELECT
Coche, Parada, Instante, Nombre
FROM `pasos_parada`
WHERE Instante BETWEEN '{ini}' AND '{fin}'
{filtra_día}
AND parada IN {paradas}
AND Linea={línea}
ORDER BY Linea, Coche, Instante;""",
    texto_tipo_día="AND DAYOFWEEK(Instante) IN {}",
    índices_laborables=tuple(range(2,7)),
    índices_festivos=(7, 1),
    parámetros_conexión={"user": 'root',
                         "password": 'madremia902',
                         "host": '193.144.208.142',
                         "port": 3306,
                         "database": 'autobuses'},
    columnas_respuesta=namedtuple("Columnas_respuesta",
                                  ("Coche", "Parada", "Instante", "Nombre"))(
                                      *range(4)),
    Δt_min_viaje=timedelta(0),
    Δt_máx_viaje=timedelta(hours=2)):
    if not (laborables or festivos):
        raise ValueError("Es necesario al menos un tipo de día.")
    viaje = namedtuple("Viaje", ("inicio", "fin"))(*viaje)
    #Nos traemos los datos de nuestra db
    with closing(connecto_to_db(**parámetros_conexión)) as conexión:
        with closing(conexión.cursor()) as cursor:
            cursor.execute(petición.format(
                línea=línea,
                ini=inicio,
                fin=fin,
                paradas=tuple(viaje),
                filtra_día= ("" if laborables and festivos
                             else texto_tipo_día.format(índices_laborables
                                                        if laborables
                                                        else festivos))))
            pasos_línea = tuple(cursor)
    #Buscamos los viajes de cada vehículo
    for vehículo, pasos_vehículo in groupby(
        pasos_línea,
        lambda r: r[columnas_respuesta.Coche]):
        t_salida = None
        for paso_vehículo in pasos_vehículo:
            if (paso_vehículo[columnas_respuesta[
                    columnas_respuesta.Parada]]
                == viaje.inicio):
                #Es una fila de comienzo de viaje, recordarlo y pedir otra.
                t_salida = paso_vehículo[columnas_respuesta.Instante]
            else:
                #Es una fila de fin de viaje
                if t_salida:
                    #Hemos encontrado un posible viaje
                    Δt_viaje = (
                        paso_vehículo[columnas_respuesta.Instante]
                        - t_salida)
                    if Δt_min_viaje < Δt_viaje < Δt_máx_viaje:
                        #El viaje tiene una duración válida
                        yield (
                            t_salida,
                            paso_vehículo[columnas_respuesta.Instante],
                            Δt_viaje) 
                    else:
                        #El viaje no se considera válido, por su
                        #duración.
                        info(pretty_output(
                            "Se ignora el viaje entre los "
                            "pasos por parada {} y {} por "
                            "tener una duración no válida: "
                            "{}".format(
                                t_salida,
                                paso_vehículo[columnas_respuesta.Instante],
                                Δt_viaje)))
                    #Recordamos que esta fila fue un fin de viaje.
                    t_salida = None

def guarda_viajes_en_excel(nombre_archivo,
                           nombre_hoja,
                           línea,
                           viaje,
                           inicio,
                           fin,
                           laborables=True,
                           festivos=True,
                           cabecera=("t_origen", "t_destino", "Δt")):
    from os import getcwd
    from openpyxl import Workbook
    from tools import exhaust_map

    ruta_archivo = "".join((getcwd(), "\\", nombre_archivo, ".xlsx"))
    libro = Workbook(write_only=True)
    hoja = libro.create_sheet(title=nombre_hoja)
    hoja.append(cabecera)
    exhaust_map(hoja.append,
                encuentra_viajes(línea,
                                 viaje,
                                 inicio,
                                 fin,
                                 laborables,
                                 festivos))
    libro.save(ruta_archivo)    
                

if __name__ == "__main__":
    #Ejemplo de uso.
    línea = 18
    viaje = (42, 370)
    inicio = "2018-02-05T06:00:00"
    fin = "2018-03-30T23:59:59"
    laborables = True,
    festivos = False,
    nombre_archivo = "L18 laborables Jesús de Monasterio 2 a Corbanera 95"
    nombre_hoja = "L18_lab_JM2-Corb95"
    guarda_viajes_en_excel(nombre_archivo,
                           nombre_hoja,
                           línea,
                           viaje,
                           inicio,
                           fin,
                           laborables,
                           festivos)
