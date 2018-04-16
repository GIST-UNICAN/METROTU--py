from parsea_viaje import guarda_viajes_en_excel

línea = 18
viaje = (372, 12)
inicio = "2018-02-05T06:00:00"
fin = "2018-03-30T23:59:59"
laborables = True,
festivos = False,
nombre_archivo = "L18 laborables Corbanera 162 a Jesús de Monasterio 21"
nombre_hoja = "L18__lab_Corb162-JM21"
guarda_viajes_en_excel(nombre_archivo,
                       nombre_hoja,
                       línea,
                       viaje,
                       inicio,
                       fin,
                       laborables,
                       festivos)

