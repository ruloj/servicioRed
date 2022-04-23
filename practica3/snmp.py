from this import d
from pysnmp.hlapi import *
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
                        "--step",'300',
                        "DS:CPUload:GAUGE:60:0:100",
                        "DS:RAM:GAUGE:60:0:U",
                        "DS:DISK:GAUGE:60:0:U",
                        "RRA:AVERAGE:0.5:1:100")
    if ret:
        print (rrdtool.error())


def updateRRD(fileName):
    while 1:
        carga_CPU = int(consultaSNMP('comunidadRulo','localhost','1.3.6.1.2.1.25.3.3.1.2.196608'))
        ram = int(consultaSNMP('comunidadRulo','localhost','1.3.6.1.2.1.25.3.3.1.2.196608'))
        disk = int(consultaSNMP('comunidadRulo','localhost','1.3.6.1.2.1.25.3.3.1.2.196608'))
        valor = "N:" + str(carga_CPU) + ':' + str(ram) + ':' + str(disk)
        # print (valor)
        try:
            rrdtool.update('RRD/'+fileName+'.rrd', valor)
        except Exception as e:
            print(e)
        rrdtool.dump('RRD/'+fileName+".rrd",'RRD/'+fileName+'.xml')
        time.sleep(1)