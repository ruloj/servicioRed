from snmp import consultaSNMP, consultaSNMPAll, createRRD,update,graficar
from bd import DataBase
import os
import time
from multiprocessing import Process
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def inicio():
    print("\n------------------------------")
    bd = DataBase(rutaBd)
    bd.crearConexion()
    numAgentes = bd.leer("select count(*) from agentes;").fetchone()[0]
    print("Número de dispositivos en monitoreo:",numAgentes)

    print("Estado de los agentes")
    table = bd.leer("select * from agentes")
    for row in table:
        print("\tAgente:", row[0], " ", end="")
        actualizarRRD(row[0],row[2])
        # if verifConexion(row[0]):
        #     print("(UP)")
        #     numInterfaces = int(consultaSNMP(row[2],row[0],"1.3.6.1.2.1.2.1.0"))
        #     print("\t\tNúmero de interfaces: ", numInterfaces)
        #     for i in range(0,numInterfaces):
        #         descr = consultaSNMP(row[2],row[0],f'1.3.6.1.2.1.2.2.1.2.{(i+1)}')
        #         if "0x" in descr:
        #             descr = bytes.fromhex(descr[2:]).decode("ASCII")
        #         print("\t\t\t",str(i+1),"- ",descr,end=" ")         
        #         status =  int(consultaSNMP(row[2],row[0],f'1.3.6.1.2.1.2.2.1.7.{(i+1)}'))
        #         if status == 1:
        #             print("(UP)")
        #         elif status == 2:
        #             print("(DOWN)")
        #         else:
        #             print("(TESTING)")
        # else:
        #     print("(DOWN)")
    bd.cerrarConexion()

def menu():
    print("Menú:")
    print("1) Agregar agente")
    print("2) Eliminar agente")
    print("3) Generar reporte de un agente")
    print("4) Salir")
    return int(input("Elegir opción: "))

def agregarAgente():
    bd = DataBase(rutaBd)
    bd.crearConexion()
    host = input("Nombre de host/IP: ")
    version = input("Versión SNMP: ")
    comunidad = input("Comunidad: ")
    bd.insertar(f'insert into agentes (host_ip,version,comunidad) values ("{host}",{version},"{comunidad}")')
    bd.cerrarConexion()
    createRRD(host)
    # exportToXml(host)

def eliminarAgente():
    bd = DataBase(rutaBd)
    bd.crearConexion()
    tabla = bd.leer("select host_ip from agentes")
    bd.imprimirTabla(tabla)
    host = input("Seleccione el agente a eliminar (nombre host/ip): ")
    terminarProcess(host)
    bd.borrar(f'delete from agentes where host_ip="{host}"')
    bd.cerrarConexion()
    
    if os.path.exists(f'{host}.rrd'):
        os.remove(f'{host}.rrd')
    if os.path.exists(f'{host}.xml'):
        os.remove(f'{host}.xml')
    
    if os.path.exists(f'{host}_pcksUni.png'):
        os.remove(f'{host}_pcksUni.png')
    if os.path.exists(f'{host}_pcksIP.png'):
        os.remove(f'{host}_pcksIP.png')
    if os.path.exists(f'{host}_msgsICMP.png'):
        os.remove(f'{host}_msgsICMP.png')
    if os.path.exists(f'{host}_sgmtsIn.png'):
        os.remove(f'{host}_sgmtsIn.png')
    if os.path.exists(f'{host}_dtgrmsUDP.png'):
        os.remove(f'{host}_dtgrmsUDP.png')

    if os.path.exists(f'{host}_reporte.pdf'):
        os.remove(f'{host}_reporte.pdf')


def verifConexion(ip):
    response = os.popen(f'ping -c 1 {ip}').read()
    # print(response)
    if "1 received" in response:
        return True
    else:
        return False

def actualizarRRD(host,comunidad):
    if host not in process:
        p = Process(name=host,target=update, args=(host,comunidad))
        process[host] = p
        process[host].start()

def terminarProcess(host):
    process[host].terminate()
    process.pop(host)
    
def terminarProcesses():
    bd = DataBase(rutaBd)
    bd.crearConexion()
    table = bd.leer("select * from agentes")
    for row in table:
        if verifConexion(row[0]):    
            process[row[0]].terminate()
            time.sleep(1)
            process.pop(row[0])

def generarGraficas():
    bd = DataBase(rutaBd)
    bd.crearConexion()
    tabla = bd.leer("select host_ip from agentes")
    bd.imprimirTabla(tabla)
    host = input("Seleccione el agente a generar reporte (nombre host/ip): ")
    #min = int(input("Ingrese cantidad de minutos a graficar: "))
    bd.cerrarConexion()
    #graficar(host,min)
    generarReporte(host)

def generarReporte(host):
    bd = DataBase(rutaBd)
    bd.crearConexion()
    row = bd.leer(f"select * from agentes where host_ip='{host}'").fetchone()
    
    cvs = canvas.Canvas(f"{host}_reporte.pdf", pagesize=letter)
    cvs.setLineWidth(.3)
    cvs.setFont('Helvetica', 14)
    
    # Encabezado
    # infoOS
    info = consultaSNMPAll(row[2],host,"1.3.6.1.2.1.1.1.0")
    if "Ubuntu" in info:
        cvs.drawImage("imgs/ubuntu-logo.png", 30, 705, width=65, height=65)        
    elif "Windows" in info:
        cvs.drawImage("imgs/windows_logo.png", 30, 705, width=65, height=65)        
    aux = int((len(info)/2))
    cvs.drawString(110,765,info[:aux])
    cvs.drawString(110,750,info[aux:])
    cvs.setFont('Helvetica', 11)
    # Ubicación
    info = consultaSNMPAll(row[2],host,"1.3.6.1.2.1.1.6.0")
    info = info.split("=")
    cvs.drawString(110,732, "Ubicación: " + info[1])
    # Número de interfaces
    info = consultaSNMP(row[2],host,"1.3.6.1.2.1.2..1.0")
    cvs.drawString(300,732, "Num. de interfaces de red: " + info)
    # Tiempo de actividad
    info = str(int(consultaSNMP(row[2],host,"1.3.6.1.2.1.1.3.0"))/100)
    cvs.drawString(110,718, "Tiempo Activo: " + info + " s")
    # Comunidad e IP
    cvs.drawString(300,718, "Comunidad: " + row[2])
    cvs.drawString(110,702, "Host/IP: " + row[0])
    cvs.line(20,695,580,695)


    cvs.save()


if __name__ == '__main__':
    rutaBd = "bd.db"
    process = {}
    inicio()
    opc = 0
    while opc != 4:
        print("\n------------------------------")
        opc = menu()
        print()
        if opc == 1:
            print("Agregar agente.")
            agregarAgente()
            inicio()
        elif opc == 2:
            print("Eliminar agente.")
            eliminarAgente()
            inicio()
        elif opc == 3:
            print("Generar reporte")
            generarGraficas()
        elif opc == 4:
            print("Hasta pronto")
            terminarProcesses()
        else:
            print("Opción invalida")


    