import serial
import serial.tools.list_ports
import time

COMPORTS={s:s for s in ("Java","Python","C","C++")}

SERIAL:serial.Serial=None

def updateComPorts():
    global COMPORTS
    COMPORTS={}
    ports=serial.tools.list_ports.comports()
    for port_info in ports:
        COMPORTS[str(port_info.device)]=port_info

"""
下面的代码基于https://github.com/Benzoin96485/Combust修改
"""

def DOpenPort(portx,bps=1200,timeout=None):
    global SERIAL
    if SERIAL and not SERIAL.closed:
        SERIAL.close()
    try:
        SERIAL=serial.Serial(portx,bps,timeout=timeout)
        if SERIAL.is_open:
            return True
    except Exception as e:
        print("---异常---：", e)
    return False

def DClosePort():
    global SERIAL
    SERIAL.close()

def backendLoop(portx):
    DOpenPort(portx)
    s=str(SERIAL.read(7).hex())
    print(s)
    endtime=time.time()
    loc=s.find("ff")
    if loc:
        s+=SERIAL.read(loc//2).hex()
        endtime=time.time()
    s=s[-14:]
    print(s)
    DClosePort()
    return s,endtime