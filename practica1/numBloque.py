import datetime

fec_nacimiento = datetime.datetime.strptime('25/10/1999','%d/%m/%Y')
fec_establecida = datetime.datetime.strptime('23/02/2022','%d/%m/%Y')
dias = (fec_establecida-fec_nacimiento).days
print("Bloque:", str((dias%3)+1))