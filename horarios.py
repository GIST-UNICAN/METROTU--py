from datetime import time
def tupla_time(lista):
    return tuple(time(*parada) for parada in lista)

paradas_3 = (
    (7, 10),
    (7, 32),
    (7, 50),
    (7, 51),
    (10, 6),
    (10, 21),
    (10, 38),
    (10, 53),
    (11, 8),
    (11, 21),
    (11, 36),
    (11, 51),
    (12, 8),
    (12, 23),
    (12, 38),
    (16, 38),
    (16, 51),
    (17, 8),
    (17, 21),
    (17, 38),
    (17, 51),
    (18, 8),
    (18, 21),
    (18, 36),
    (18, 51),
    (19, 6),
    (21, 36),
    (21, 51),
    (22, 6),
    (22, 21),
    (22, 36),
)



paradas_13 = (
    (7, 21),
    (7, 51),
    (8, 21),
    (8, 51),
    (9, 21),
    (9, 51),
    (10, 36),
    (11, 6),
    (11, 51),
    (12, 21),
    (12, 51),
    (13, 21),
    (13, 51),
    (14, 21),
    (14, 51),
    (15, 21),
    (15, 51),
    (16, 21),
    (17, 6),
    (17, 36),
    (18, 6),
    (18, 36),
    (19, 6),
    (19, 51),
    (20, 21),
    (20, 51),
    (21, 21),
    (21, 51),
    (22, 21),
)

paradas_17 = (
    (7, 22),
 (7, 36),
 (7, 52),
 (8, 6),
 (8, 22),
 (8, 34),
 (8, 52),
 (9, 6),
 (9, 22),
 (9, 34),
 (9, 52),
 (10, 6),
 (10, 22),
 (10, 34),
 (10, 53),
 (11, 6),
 (11, 20),
 (11, 34),
 (11, 52),
 (12, 6),
 (12, 20),
 (12, 34),
 (12, 52),
 (13, 6),
 (13, 22),
 (13, 36),
 (13, 52),
 (14, 6),
 (14, 22),
 (14, 36),
 (14, 52),
 (15, 6),
 (15, 20),
 (15, 35),
 (15, 53),
 (16, 6),
 (16, 20),
 (16, 34),
 (16, 52),
 (17, 7),
 (17, 21),
 (17, 34),
 (17, 52),
 (18, 6),
 (18, 22),
 (18, 34),
 (18, 53),
 (19, 6),
 (19, 23),
 (19, 36),
 (19, 53),
 (20, 6),
 (20, 23),
 (20, 37),
 (20, 53),
 (21, 8),
 (21, 23),
 (21, 38),
 (21, 53),
 (22, 8))



paradas_17_Avd_Deporte = (
    (7, 22),
    (7, 52),
    (8, 22),
    (8, 52),
    (9, 22),
    (9, 52),
    (10, 22),
    (10, 53),
    (11, 20),
    (11, 52),
    (12, 20),
    (12, 52),
    (13, 22),
    (13, 52),
    (14, 22),
    (14, 52),
    (15, 20),
    (15, 53),
    (16, 20),
    (16, 52),
    (17, 21),
    (17, 52),
    (18, 22),
    (18, 53),
    (19, 23),
    (19, 53),
    (20, 23),
    (20, 53),
    (21, 23),
    (21, 53),
)


paradas_17_B_La_Gloria = (
    (7, 36),
    (8, 6),
    (8, 34),
    (9, 6),
    (9, 34),
    (10, 6),
    (10, 34),
    (11, 6),
    (11, 34),
    (12, 6),
    (12, 34),
    (13, 6),
    (13, 36),
    (14, 6),
    (14, 36),
    (15, 6),
    (15, 35),
    (16, 6),
    (16, 34),
    (17, 7),
    (17, 34),
    (18, 6),
    (18, 34),
    (19, 6),
    (19, 36),
    (20, 6),
    (20, 37),
    (21, 8),
    (21, 38),
    (22, 8),
)


paradas_C_Int_Valdecilla = (
    (7, 8),
    (7, 23),
    (7, 38),
    (7, 53),
    (8, 8),
    (8, 23),
    (8, 38),
    (8, 53),
    (9, 8),
    (9, 23),
    (9, 38),
    (9, 53),
    (10, 8),
    (10, 23),
    (10, 38),
    (10, 53),
    (11, 8),
    (11, 23),
    (11, 38),
    (11, 53),
    (12, 8),
    (12, 23),
    (12, 38),
    (12, 53),
    (13, 8),
    (13, 23),
    (13, 38),
    (13, 53),
    (14, 8),
    (14, 23),
    (14, 38),
    (14, 53),
    (15, 8),
    (15, 23),
    (15, 38),
    (15, 53),
    (16, 8),
    (16, 23),
    (16, 38),
    (16, 53),
    (17, 8),
    (17, 23),
    (17, 38),
    (17, 53),
    (18, 8),
    (18, 23),
    (18, 38),
    (18, 53),
    (19, 8),
    (19, 23),
    (19, 38),
    (19, 53),
    (20, 8),
    (20, 23),
    (20, 38),
    (20, 53),
    (21, 8),
    (21, 23),
    (21, 38),
    (21, 53),
    (22, 8),
    (22, 23),
)



paradas_C_Int_Sardinero = (
    (7, 15),
    (7, 30),
    (7, 45),
    (8, 00),
    (8, 15),
    (8, 30),
    (8, 45),   
    (9, 00),
    (9, 15),
    (9, 30),
    (9, 45),   
    (10, 00),
    (10, 15),
    (10, 30),
    (10, 45),   
    (11, 00),
    (11, 15),
    (11, 30),
    (11, 45),   
    (12, 00),
    (12, 15),
    (12, 30),
    (12, 45),   
    (13, 00),
    (13, 15),
    (13, 30),
    (13, 45),   
    (14, 00),
    (14, 15),
    (14, 30),
    (14, 45),   
    (15, 00),
    (15, 15),
    (15, 30),
    (15, 45),   
    (16, 00),
    (16, 15),
    (16, 30),
    (16, 45),   
    (17, 00),
    (17, 15),
    (17, 30),
    (17, 45),   
    (18, 00),
    (18, 15),
    (18, 30),
    (18, 45),   
    (19, 00),
    (19, 15),
    (19, 30),
    (19, 45),   
    (20, 00),
    (20, 15),
    (20, 30),
    (20, 45),   
    (21, 00),
    (21, 15),
    (21, 30),
    (21, 45),   
    (22, 00),
    (22, 15),
    (22, 30),
)

cabeceras_3 = (
    (6, 53),
    (7, 8),
    (7, 23),
    (7, 38),
    (7, 53),
    (8, 8),
    (8, 23),
    (8, 38),
    (8, 53),
    (9, 8),
    (9, 38),
    (9, 53),
    (10, 8),
    (10, 23),
    (10, 38),
    (10, 53),
    (11, 8),
    (11, 23),
    (11, 38),
    (11, 53),
    (12, 23),
    (12, 38),
    (12, 53),
    (13, 8),
    (13, 23),
    (13, 38),
    (13, 53),
    (14, 8),
    (14, 23)
    ) #incompleta, no hace falta
   
paradas_3, paradas_13, paradas_17, paradas_C_Int_Sardinero, paradas_C_Int_Valdecilla=map(
    tupla_time,
    (paradas_3, paradas_13,
     paradas_17, paradas_C_Int_Sardinero,
     paradas_C_Int_Valdecilla))
