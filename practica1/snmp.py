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

def createRRD(nombre):
    ret = rrdtool.create(f'{nombre}.rrd',
                        "--start",'N',
                        "--step",'60',
                        "DS:pcksUni:COUNTER:120:U:U",
                        "DS:pcksIP:COUNTER:120:U:U",
                        "DS:msgsICMP:COUNTER:120:U:U",
                        "DS:sgmtsIn:COUNTER:120:U:U",
                        "DS:dtgrmsUDP:COUNTER:120:U:U",
                        "RRA:AVERAGE:0.5:1:24")
    if ret:
        print (rrdtool.error())

def exportToXml(nombre):
    rrdtool.dump(f'{nombre}.rrd',f'{nombre}.xml')

def update(host,comunidad):
    while 1:
        total_pcksUni = int(
            consultaSNMP(comunidad,host,
                        '1.3.6.1.2.1.2.2.1.11.1'))
        total_pcksIP = int(
            consultaSNMP(comunidad,host,
                        '1.3.6.1.2.1.4.3.0'))
        total_msgsICMP = int(
            consultaSNMP(comunidad,host,
                        '1.3.6.1.2.1.5.21.0'))
        total_sgmtsIn = int(
            consultaSNMP(comunidad,host,
                        '1.3.6.1.2.1.6.10.0'))
        total_dtgrmsUDP = int(
            consultaSNMP(comunidad,host,
                        '1.3.6.1.2.1.7.4.0'))
    
        valor = "N:" + str(total_pcksUni) + ':' + str(total_pcksIP) + ':' + str(total_msgsICMP) + ':' + str(total_sgmtsIn) + ':' + str(total_dtgrmsUDP)
        # print (valor)
        try:
            rrdtool.update(f'{host}.rrd', valor)
        except Exception as e:
            print()
        rrdtool.dump(f'{host}.rrd',f'{host}.xml')
        time.sleep(1)


'''
    1) Paquetes unicast que ha recibido una interfaz  
        1.3.6.1.2.1.2.2.1.11.1
    1) Paquetes recibidos a protocolos IPv4, incluyendo los que tienen errores. 
        1.3.6.1.2.1.4.3.0
    1) Mensajes ICMP echo que ha enviado el agente 
        1.3.6.1.2.1.5.21.0
    1) Segmentos recibidos, incluyendo los que se han recibido con errores. 
        1.3.6.1.2.1.6.10.0
    1) Datagramas entregados a usuarios UDP  
        1.3.6.1.2.1.7.4.0
'''

def graficar(host,minutos):
    tiempo_actual = int(time.time())
    tiempo_inicial = tiempo_actual - (minutos*60)

    rrdtool.graph( f'{host}_pcksUni.png',
                    "--start",str(tiempo_inicial),
                    "--end","N",
                    "--vertical-label=Paquetes",
                    "--title=Paquetes unicast que ha recibido una interfaz",
                    f'DEF:pcksUniIn={host}.rrd:pcksUni:AVERAGE',
                    "LINE3:pcksUniIn#FF0000:Paquetes unicast recibidos")

    rrdtool.graph( f'{host}_pcksIP.png',
                    "--start",str(tiempo_inicial),
                    "--end","N",
                    "--vertical-label=Paquetes",
                    "--title=Paquetes recibidos a protocolos IPv4 \n (incluyendo los que tienen errores)",
                    f'DEF:pcksIPIn={host}.rrd:pcksIP:AVERAGE',
                    "LINE3:pcksIPIn#00FF00:Paquetes IPV4 recibidos")

    rrdtool.graph( f'{host}_msgsICMP.png',
                    "--start",str(tiempo_inicial),
                    "--end","N",
                    "--vertical-label=Mensajes",
                    "--title=Mensajes ICMP echo que ha enviado el agente",
                    f'DEF:msgsICMPOut={host}.rrd:msgsICMP:AVERAGE',
                    "LINE3:msgsICMPOut#0000FF:Mensajes ICMP echo enviados")

    rrdtool.graph( f'{host}_sgmtsIn.png',
                    "--start",str(tiempo_inicial),
                    "--end","N",
                    "--vertical-label=Segmentos",
                    "--title=Segmentos recibidos \n (incluyendo los que se han recibido con errores)",
                    f'DEF:sgmtsInX={host}.rrd:sgmtsIn:AVERAGE',
                    "LINE3:sgmtsInX#6C3483:Segmentos recibidos")

    rrdtool.graph( f'{host}_dtgrmsUDP.png',
                    "--start",str(tiempo_inicial),
                    "--end","N",
                    "--vertical-label=Datagramas",
                    "--title=Datagramas entregados a usuarios UDP",
                    f'DEF:dtgrmsUDPOut={host}.rrd:dtgrmsUDP:AVERAGE',
                    "LINE3:dtgrmsUDPOut#3498DB:Datagramas enviados")