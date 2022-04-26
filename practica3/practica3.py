from snmp import createRRD, updateRRD, graficar
from bd import DataBase

def menu():
    print("1) Agregar host/ip")
    print("2) Iniciar monitoreo")
    print("3) Salir")
    return int(input("Ingrese una opción: "))

def agregarAgente():
    bd = DataBase(rutaBd)
    bd.crearConexion()
    host = input("Nombre de host/IP: ")
    version = input("Versión SNMP: ")
    comunidad = input("Comunidad: ")
    bd.insertar(f'insert into agentes (host_ip,version,comunidad) values ("{host}",{version},"{comunidad}")')#Cambiar a update
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
    updateRRD(host,comunidad)

def mandarCorreo():
    bd = DataBase(rutaBd)
    bd.crearConexion()
    tabla = bd.leer("select host_ip from agentes")
    host = tabla.fetchone()[0]
    bd.cerrarConexion()
    graficar(host,5)

if __name__ == '__main__':
    rutaBd = "bd.db"
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
        elif opc == 3:
            print("Hasta pronto")
            mandarCorreo()
        else:
            print("Opcion invalida")