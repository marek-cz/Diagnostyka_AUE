"""
MODUL ZAWIERAJACY BACK-END DO GUI
"""


import serial.tools.list_ports


def ListaPortowCOM():
    porty = list(serial.tools.list_ports.comports())
    result = []
    for i in range( len( porty ) ):
        result.append( porty[i][0] )
    return result
