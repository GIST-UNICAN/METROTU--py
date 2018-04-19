from openpyxl import Workbook, load_workbook 
import os
import time
from datetime import datetime, date
import contextlib
import MySQLdb
# 0 llegadas 1 salidas
paradas={516:{0:(100,),1:None},
              511:{0:(8,9,20,1,2),1:(100,)},
              515:{0:None,1:(8,9,20)},
              509:{0:(100,),1:(3,13,14,17)},
              512:{0:(3,13,14,17),1:(1,2,72,100)}}
def slices(
    args=(0, 31, 37, 45, 51, 58,67,75, 87, 92, 98,129,153, 177,196,201,203,205,-1),
    wanted_columns = {1, 3, 5, 7, 9, 11,12,13}
    #args=(0, 24, 30, 36, 43,104,111, 119,138,143,150,152,-1),
    #wanted_columns = {1,2,3,4,5,7,9,10}
    ):
    try:
        for column in wanted_columns:
            yield s[args[column]:args[column+1]].rstrip()
    except IndexError:
        return

def filtra_excel(
    ruta_entrada
    ):
    query_append=list()
    c_rr=0
    c_rm=0
    #ruta_entrada=os.getcwd()+datos_row.archivo
##    libro_entrada = load_workbook(ruta_entrada)
##    hoja_entrada = libro_entrada.active
    with open(ruta_entrada, "r", encoding="utf-8") as archivo_entrada:
        iter_archivo = iter(archivo_entrada)
        next(iter_archivo)
        next(iter_archivo)
        
        for raw_row in iter_archivo:
            try:
                c_rr+=1
                row=list(slices(raw_row))
                row[0] = int(row[0])
                row[1] = int(row[1])
                row[2] = int(row[2])
                row[3] = int(row[3])
                row[4] = int(row[4])
                if row[5]== 'NULL':
                    row[5]='Null'
                else:
                    row[5] = datetime.strptime(str(row[5]), "%Y-%m-%d %H:%M:%S.%f")
                if row[6]== 'NULL':
                    row[6]='Null'
                else:
                    row[6] = datetime.strptime(str(row[6]), "%Y-%m-%d %H:%M:%S.%f")
                if row[7]== 'NULL':
                    row[7]='Null'
                else:
                    row[7] = datetime.strptime(str(row[7]), "%Y-%m-%d %H:%M:%S.%f")
                #insertamos en la bd
                query_append.append("({},{},{},{},'{}','{}',{},'{}')".format(
                        row[0],row[1],row[4],row[2],row[5],row[3],row[6],row[7]))
            except ValueError as e:
                print(e)
                c_rm+=1
                print("Row mala")
                print(row)
                continue
    for fila in row:
        if fila[0] in paradas[fila[3][0]]:
            print('llegadas')
        if fila[0] in paradas[fila[3][1]]:
            print('salidas')
        
#    querie="INSERT INTO `pasos_parada` (`Linea`, `Coche`, `Viaje`, `Parada`, `Instante`, `Nombre`, `PSuben`, `Fecha`) VALUES " +str(query_append)[1:-1].replace('"',"")
#    try:
#        with contextlib.closing(MySQLdb.connect(
#                host='193.144.208.142',
#                user="root",
#                passwd="madremia902",
#                db="autobuses")) as cnx:
#            with contextlib.closing(cnx.cursor()) as crs:
#                crs.execute(querie)
#                cnx.commit()
#    except Exception as e:
#        print('sql error' + str(e))
    print(c_rr)
    print(c_rm)
    



filtra_excel(
    r"D:\Users\Andres\OneDrive\OneDrive - Universidad de Cantabria\Recordar GIST - VARIOS\datos_tus\17vh.txt"
    )


