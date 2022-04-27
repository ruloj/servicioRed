from snmp import createRRD, updateRRD, graficar
from multiprocessing import Process
from bd import DataBase
import time

def menu():
    print("1) Agregar host/ip")
    print("2) Iniciar monitoreo")
    print("3) Salir")
    return int(input("Ingrese una opción: "))

def agregarAgente():
    bd = DataBase(rutaBd)
    bd.crearConexion()
    # table = bd.leer("select * from agentes;")
    # bd.imprimirTabla(table)
    host = input("Nombre de host/IP: ")
    version = input("Versión SNMP: ")
    comunidad = input("Comunidad: ")
    bd.actualizar(f'''update agentes  
                      set host_ip="{host}", comunidad= "{comunidad}"
                      where version=1;
                    ''')
    # table = bd.leer("select * from agentes;")
    # bd.imprimirTabla(table)
    bd.cerrarConexion()
    createRRD(host)

def monitorizarAgente():
    bd = DataBase(rutaBd)
    bd.crearConexion()
    row = bd.leer("select * from agentes").fetchone()
    print(row)
    host = row[0]
    comunidad = row[2]
    bd.cerrarConexion()
    if host not in process:
        p = Process(name=host,target=updateRRD, args=(host,comunidad))
        process[host] = p
        process[host].start()
    # updateRRD(host,comunidad)

def mandarCorreo():
    bd = DataBase(rutaBd)
    bd.crearConexion()
    tabla = bd.leer("select host_ip from agentes")
    host = tabla.fetchone()[0]
    bd.cerrarConexion()
    while True:
        graficar(host,10)
        time.sleep(2*60)

if __name__ == '__main__':
    process = {}
    rutaBd = "base.db"
    opc = 0
    while opc != 3:
        opc = menu()
        print()
        if opc == 1:
            print("Agregar/cambiar agente")
            agregarAgente()
        elif opc == 2:
            print("Monitorizando agente...")
            monitorizarAgente()
            mandarCorreo()
        elif opc == 3:
            print("Hasta pronto")
        else:
            print("Opcion invalida")
        print()