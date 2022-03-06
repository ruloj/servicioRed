from snmp import consultaSNMP, createRRD,update,graficar
from bd import DataBase
import os
import time
from multiprocessing import Process

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
    min = int(input("Ingrese cantidad de minutos a graficar: "))
    graficar(host,min)
    
    bd.cerrarConexion()

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


    