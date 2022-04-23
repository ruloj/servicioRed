import sys
import rrdtool
from  Notify import send_alert_attached
import time
rrdpath = 'RRD/'
imgpath = 'IMG/'

ultima_lectura = int(rrdtool.last(rrdpath+"trend.rrd"))
tiempo_final = ultima_lectura
tiempo_inicial = tiempo_final - 600

ret = rrdtool.graphv( imgpath+"deteccion.png",
                     "--start",str(tiempo_inicial),
                     "--end",str(tiempo_final),
                     "--vertical-label=Cpu load",
                    '--lower-limit', '0',
                    '--upper-limit', '100',
                    "--title=Uso del CPU del agente Usando SNMP y RRDtools \n Detección de umbrales",

                    "DEF:cargaCPU="+rrdpath+"trend.rrd:CPUload:AVERAGE",

                     "VDEF:cargaMAX=cargaCPU,MAXIMUM",
                     "VDEF:cargaMIN=cargaCPU,MINIMUM",
                     "VDEF:cargaSTDEV=cargaCPU,STDEV",
                     "VDEF:cargaLAST=cargaCPU,LAST",

                     #"CDEF:cargaEscalada=cargaCPU,8,*"

                     "CDEF:umbral55=cargaCPU,55,LT,0,cargaCPU,IF",
                     "AREA:cargaCPU#00FF00:Carga del CPU",
                     "AREA:umbral55#DD0000:Carga CPU mayor que 55",
                     "HRULE: 55#FF00FF:Umbral 1 - 55%",

                     "CDEF:umbral63=cargaCPU,63,LT,0,cargaCPU,IF",
                     "AREA:umbral63#450001:Carga CPU mayor que 63",
                     "HRULE: 63#FF0000:Umbral 1 - 63%",
 

                     "PRINT:cargaLAST:%6.2lf",
                     "GPRINT:cargaMIN:%6.2lf %SMIN",
                     "GPRINT:cargaSTDEV:%6.2lf %SSTDEV",
                     "GPRINT:cargaLAST:%6.2lf %SLAST" )
print (ret)

ultimo_valor=float(ret['print[0]'])
if ultimo_valor>4:
    send_alert_attached("Sobrepasa Umbral línea base")
    print("Sobrepasa Umbral línea base")