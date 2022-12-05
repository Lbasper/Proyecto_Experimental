"""

Código creado para el grupo de Materiales Cuánticos.

Colaboración entre los estudiantes:
- Juan Pablo Nicolas Cruz Castiblanco (Estudiante de Maestría en Física)
- Luciano Bastidas Peralta (Estudiantes de Pregrado en Física)

Se adjunta 1 funcion sweep_dense.
    La cual requiere una lista de limites alrededor de las resonancias.
        -Generada en lista_limites() donde con la lista de resonancias genera limites para el barrido.
    una lista binaria [importancia] que dicta cuando realizar un barrido denso en el sistema lock-in amplifier H2FLI

"""


"""
Librerias requeridas
"""

import matplotlib.pyplot as plt
import numpy as np
import time
import zhinst.ziPython as zi
"""

Registro del equipo

"""
daq = zi.ziDAQServer('127.0.0.1', 8005, 1)
sweeper = daq.sweep()
Start=1e6
Stop=5e6







def lista_limites(resonancias,delta=10e3):
    """
    retorna los limites de los barridos densos y no densos 
    
    """
    longitud=len(resonancias) #
    limites=np.zeros(longitud*2+2) # limites de los intervalos de frecuecia 
    importancia = np.zeros(longitud*2+2) # un indice que caracteriza la importancia del intervalo: 0 no denso, 1 denso 
    #delta=10e3 # 10 kHz el delta de los intervalos
    
    for i in range(len(limites)):
        if i==0:
            limites[i]=Start
            importancia[i]=0
        elif i==len(limites)-1:
            limites[i]=Stop
            importancia[i]=0
        else:
            if i%2==0:
                delt=resonancias[int((i-1)/2)]+delta
                importancia[i]=0
            else:
                delt=resonancias[int((i-1)/2)]-delta
                importancia[i]=1
            limites[i]=delt
            
    return  limites, importancia

def sweep_dense(limites,importancia, rho_intermedio = 0.05e-3, rho_resonancia = 2e-3, nprom=20):
    """
    Realiza un barrido denso en las zonas donde estan presentes resonancias, y un barrido no denso en zonas donde no hay 
    presentes resonancias
    """
    t0 = time.time()
    
    Denso_Freq=[]
    Denso_X=[]
    Denso_Y=[]
    
    #rho_intermedio = 0.05e-3 # densidad de puntos entre rec 0.8 puntos/kHZ
    #rho_resonancia = 2e-3 # densidad de puntos en la resonancia 2.5 puntos/kHZ
    
    daq.setDouble('/dev1941/sigouts/0/amplitudes/6', 1) # Voltaje de salida 1 V
    
    for i in range(len(limites)-1):
        Start=limites[i]
        Stop=limites[i+1]
        # se ajusta el número de pasos si hay o no resonancia en el intervalo
        if importancia[i]==0: 
            pasos=int(rho_intermedio*(Stop-Start))
        if importancia[i]==1:
            pasos=int(rho_resonancia*(Stop-Start))
            
        sweeper.subscribe('/dev1941/demods/0/sample')

        # limites del barrido
        
        sweeper.set('start', Start)
        sweeper.set('stop', Stop)
        sweeper.set('averaging/sample', nprom) # numero de veces que es tomado cada dato
        sweeper.set('samplecount', pasos) # numero de pasos    
        sweeper.execute() 
        result = 0
        while not sweeper.finished():
            time.sleep(1)
            result = sweeper.read(True)
        sweeper.finish()
        sweeper.unsubscribe('*')
        
        Datos=result
        Freq=Datos['/dev1941/demods/0/sample'][0][0]["frequency"]
        X=Datos['/dev1941/demods/0/sample'][0][0]["x"]
        Y=Datos['/dev1941/demods/0/sample'][0][0]["y"] 
        Denso_Freq=np.append(Denso_Freq,Freq)
        Denso_X=np.append(Denso_X,X)
        Denso_Y=np.append(Denso_Y,Y)
        
    tf = time.time()
    print(f'tiempo de ejecución {(tf-t0)/60} minutos')
    return Denso_Freq,Denso_X,Denso_Y