import time
import rrdtool
from getSNMP import consultaSNMP
rrdpath = 'RRD/'
carga_CPU = 0

while 1:
    carga_CPU = int(consultaSNMP('comunidadRulo','localhost','1.3.6.1.2.1.25.3.3.1.2.196608'))
    valor = "N:" + str(carga_CPU)
    print (valor)
    rrdtool.update(rrdpath+'trend.rrd', valor)
    rrdtool.dump(rrdpath+'trend.rrd','trend.xml')
    time.sleep(1)

if ret:
    print (rrdtool.error())
    time.sleep(300)