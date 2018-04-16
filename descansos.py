from datetime import time
def tupla_time(lista):
    return tuple(time(*parada) for parada in lista)

descansos_3 = (
    (9, 36),
    (12, 21),
    (17, 51),
    (21, 6)
    )

descansos_9_Repuente = (
    (9, 47),
    (11, 32),
    (17, 47),
    (19, 32)
    )

descansos_9_Cueto = (
    (9, 26),
    (11, 11),
    (17, 26),
    (19, 11)
    )

descansos_13 = (
    (10, 21),
    (11, 36),
    (16, 51),
    (19, 36)
)

descansos_17_Deporte = (
    ()
)

descansos_17_Gloria = (
    ()
)

descansos_20_Rectorado = (
    (10, 54),
    (12, 9),
    (16, 54),
    (19, 9)
)

descansos_20_PCTCAN = (
    (10, 25),
    (11, 40),
    (16, 25),
    (18, 40)
)

