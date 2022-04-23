import rrdtool
ret = rrdtool.create("RRD/trend.rrd",
                     "--start",'N',
                     "--step",'300',
                     "DS:CPUload:GAUGE:60:0:100",
                     "RRA:AVERAGE:0.5:1:100",
                     "DS:RAM:GAUGE:60:0:100",
                     "RRA:AVERAGE:0.5:1:100",
                     "DS:DISK:GAUGE:60:0:100",
                     "RRA:AVERAGE:0.5:1:100")
if ret:
    print (rrdtool.error())
