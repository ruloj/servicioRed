from ast import Or
from calendar import c
from fileinput import filename
from this import d
from pysnmp.hlapi import *
from notify import send_alert_attached
import rrdtool
import time

def consultaSNMP(comunidad,host,oid):
    errorIndication, errorStatus, errorIndex, varBinds = next(
        getCmd(SnmpEngine(),
               CommunityData(comunidad),
               UdpTransportTarget((host, 161)),
               ContextData(),
               ObjectType(ObjectIdentity(oid))))

    if errorIndication:
        print(errorIndication)
    elif errorStatus:
        print('%s at %s' % (errorStatus.prettyPrint(),errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
    else:
        for varBind in varBinds:
            varB=(' = '.join([x.prettyPrint() for x in varBind]))
            resultado= varB.split()[2]
    return resultado

def createRRD(fileName):
    ret = rrdtool.create(f"RRD/{fileName}.rrd",
                        "--start",'N',
                        "--step",'120',
                        "DS:CPUload:GAUGE:60:0:100",
                        "DS:DISK:GAUGE:60:0:U",
                        "DS:RAM:GAUGE:60:0:U",
                        "RRA:AVERAGE:0.5:1:100")
    if ret:
        print (rrdtool.error())


def updateRRD(host,comunidad):
    fileName = host
    while 1:
        carga_CPU =  int(consultaSNMP(comunidad,host,'1.3.6.1.2.1.25.3.3.1.2.196608'))
        uBytesDisk = int(consultaSNMP(comunidad,host,'1.3.6.1.2.1.25.2.3.1.4.36'))
        disk =       int(consultaSNMP(comunidad,host,'1.3.6.1.2.1.25.2.3.1.6.36'))
        diskUsed = "{:.2f}".format(disk * uBytesDisk * 1e-9)
        ram = int(consultaSNMP('comunidadRulo','localhost','1.3.6.1.4.1.2021.4.6.0'))
        ramUsed = "{:.2f}".format(ram * 1e-6)
        valor = "N:" + str(carga_CPU) + ':' + str(diskUsed) + ':' + str(ramUsed)
        # print (valor)
        try:
            rrdtool.update('RRD/'+fileName+'.rrd', valor)
        except Exception as e:
            print(e)
        rrdtool.dump('RRD/'+fileName+".rrd",'RRD/'+fileName+'.xml')
        time.sleep(1)

def graficar(fileName,minutos):
    ultima_lectura = int(rrdtool.last("RRD/"+fileName+".rrd"))
    tiempo_final = ultima_lectura
    tiempo_inicial = tiempo_final  - (minutos*60*2)
    umbrales = {
        'cpuLoad': False,
        'disk': False,
        'ram': False,
    }

    ret = rrdtool.graphv( "GRAPHS/CPULoad.png",
                        "--start",str(tiempo_inicial),
                        "--end",str(tiempo_final),
                        "--vertical-label=Cpu load",
                        '--lower-limit', '0',
                        '--upper-limit', '100',
                        "--title=Uso del CPU del agente \n Detección de umbrales",

                        "DEF:cargaCPU=RRD/"+fileName+".rrd:CPUload:AVERAGE",

                        "VDEF:cargaMAX=cargaCPU,MAXIMUM",
                        "VDEF:cargaMIN=cargaCPU,MINIMUM",
                        "VDEF:cargaSTDEV=cargaCPU,STDEV",
                        "VDEF:cargaLAST=cargaCPU,LAST",

                        "AREA:cargaCPU#00FF00:Carga del CPU",

                        "CDEF:umbral55=cargaCPU,55,LT,0,cargaCPU,IF",
                        "AREA:umbral55#DD0000:Carga CPU mayor que 55",
                        "HRULE: 55#FF00FF:Umbral 1 - 55%",

                        "CDEF:umbral60=cargaCPU,60,LT,0,cargaCPU,IF",
                        "AREA:umbral60#E65220:Carga CPU mayor que 60",
                        "HRULE: 60#FF142F:Umbral 1 - 60%",

                        "CDEF:umbral63=cargaCPU,63,LT,0,cargaCPU,IF",
                        "AREA:umbral63#450001:Carga CPU mayor que 63",
                        "HRULE: 63#FF0000:Umbral 1 - 63%",

                        "PRINT:cargaLAST:%6.2lf",
                        "GPRINT:cargaMIN:%6.2lf %SMIN",
                        "GPRINT:cargaSTDEV:%6.2lf %SSTDEV",
                        "GPRINT:cargaLAST:%6.2lf %SLAST" )
    # print (ret)

    ultimo_valor=float(ret['print[0]'])
    if ultimo_valor>55:
        umbrales['cpuLoad'] = True
    #     send_alert_attached("Sobrepasa Umbral línea base")
    #     print("Sobrepasa Umbral línea base")

    ret = rrdtool.graphv( "GRAPHS/DISK.png",
                        "--start",str(tiempo_inicial),
                        "--end",str(tiempo_final),
                        "--vertical-label=Almacenamiento",
                        '--lower-limit', '0',
                        # '--upper-limit', '',
                        "--title=Uso del almacenamiento del agente \n Detección de umbrales",

                        "DEF:usoDISK=RRD/"+fileName+".rrd:DISK:AVERAGE",

                        "VDEF:usoMAX=usoDISK,MAXIMUM",
                        "VDEF:usoMIN=usoDISK,MINIMUM",
                        "VDEF:usoSTDEV=usoDISK,STDEV",
                        "VDEF:usoLAST=usoDISK,LAST",

                        "AREA:usoDISK#00FF00:Uso de almacenamiento",

                        "CDEF:umbral55=usoDISK,13.69,LT,0,usoDISK,IF",
                        "AREA:umbral55#DD0000:Almacenamiento mayor que 13.69 GB",
                        "HRULE: 13.69#FF00FF:Umbral 1 - 13.69 GB",

                        "CDEF:umbral20=usoDISK,20,LT,0,usoDISK,IF",
                        "AREA:umbral20#E65220:Almacenamiento mayor que 20 GB",
                        "HRULE: 20#FF142F:Umbral 1 - 20 GB",

                        "CDEF:umbral63=usoDISK,35,LT,0,usoDISK,IF",
                        "AREA:umbral63#450001:Almacenamiento mayor que 35 GB",
                        "HRULE: 35#FF0000:Umbral 1 - 35 GB",

                        "PRINT:usoLAST:%6.2lf",
                        "GPRINT:usoMIN:%6.2lf %SMIN",
                        "GPRINT:usoSTDEV:%6.2lf %SSTDEV",
                        "GPRINT:usoLAST:%6.2lf %SLAST" )
    # print (ret)

    ultimo_valor=float(ret['print[0]'])
    if ultimo_valor>13.69:
        umbrales['disk'] = True
    # send_alert_attached("Sobrepasa Umbral línea base")
        # print("Sobrepasa Umbral línea base")

    ret = rrdtool.graphv( "GRAPHS/RAM.png",
                        "--start",str(tiempo_inicial),
                        "--end",str(tiempo_final),
                        "--vertical-label=Uso de RAM",
                        '--lower-limit', '0',
                        # '--upper-limit', '',
                        "--title=Uso de la RAM del agente \n Detección de umbrales",

                        "DEF:usoRAM=RRD/"+fileName+".rrd:RAM:AVERAGE",

                        "VDEF:usoMAX=usoRAM,MAXIMUM",
                        "VDEF:usoMIN=usoRAM,MINIMUM",
                        "VDEF:usoSTDEV=usoRAM,STDEV",
                        "VDEF:usoLAST=usoRAM,LAST",

                        "AREA:usoRAM#00FF00:Uso de la RAM",

                        "CDEF:umbral55=usoRAM,2,LT,0,usoRAM,IF",
                        "AREA:umbral55#DD0000:Uso mayor que 2 GB",
                        "HRULE:2#FF00FF:Umbral 1 - 2 GB",

                        "CDEF:umbral5=usoRAM,2.5,LT,0,usoRAM,IF",
                        "AREA:umbral5#DD0000:Uso mayor que 2.5 GB",
                        "HRULE:2.5#FF142F:Umbral 0 - 2.5 GB",

                        "CDEF:umbral63=usoRAM,2.9,LT,0,usoRAM,IF",
                        "AREA:umbral63#450001:Almacenamiento mayor que 2.9 GB",
                        "HRULE: 2.9#FF0000:Umbral 1 - 2.9 GB",

                        "PRINT:usoLAST:%6.2lf",
                        "GPRINT:usoMIN:%6.2lf %SMIN",
                        "GPRINT:usoSTDEV:%6.2lf %SSTDEV",
                        "GPRINT:usoLAST:%6.2lf %SLAST" )
    # print (ret)

    ultimo_valor=float(ret['print[0]'])
    if ultimo_valor>2:
        umbrales['ram'] = True
        # print("Sobrepasa Umbral línea base")
    if umbrales['cpuLoad'] or umbrales['disk'] or umbrales['ram']:
        send_alert_attached(umbrales,minutos)
    umbrales = {}