import sqlite3

class DataBase:

    def __init__(self, bd_path):
        self.__bd_path = bd_path

    def crearConexion(self):
        self.__conexion = sqlite3.connect(self.__bd_path)
        self.__cursor = self.__conexion.cursor()

    def cerrarConexion(self):
        self.__conexion.close()

    def leer(self,query):
        try:
            return self.__cursor.execute(query)
        except Exception as error:
            print("Error al leer")
            print(error)

    def actualizar(self,query):
        try:
            self.__cursor.execute(query)
            self.__conexion.commit()
        except Exception as error:
            print("Error al actualizar")
            print(error)

    def insertar(self,query):
        try:
            self.__cursor.execute(query)
            self.__conexion.commit()
            print("Operación realizada correctamente")
        except Exception as error:
            print("Error al insertar")
            print(error)

    def borrar(self,query):
        try:
            self.__cursor.execute(query)
            self.__conexion.commit()
            print("Operación realizada correctamente")
        except Exception as error:
            print("Error al borrar")
            print(error)
        
    def imprimirTabla(self,table):
        print("(",end="")
        for columnName in table.description:
            print(columnName[0], end=",")
        print(")")
        for row in table:
            print(row)

# conexion=sqlite3.connect("bd.db")
# try:
#     conexion.execute("drop table agentes;")
#     conexion.execute("""create table agentes (
#                               host_ip text,
#                               version integer,
#                               comunidad text
#                         )""")
#     print("se creo la tabla agentes")                        
# except sqlite3.OperationalError:
#     print("La tabla agentes ya existe")                    
# conexion.close()