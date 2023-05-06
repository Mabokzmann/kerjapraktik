from time import sleep
from datetime import datetime
import serial, struct, traceback

def run():
    port = "/dev/ttyACM0"
    baudrate = 9600
    error = ""

    while True:
        try:
            if (ser.read() == b"&"):
                if (ser.read() == b"*"):
                    if (ser.read() == b"%"):
                        timestamp = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

                        typedata = 'ffffffff'
                        data = ser.read(struct.calcsize(typedata))
                        sensor = list(struct.unpack(typedata, data))
                        sensor.insert(0, timestamp)
                        # ["Timestamp", "PV Voltage (Volt)", "PV Current (Ampere)", "PV Power (Watt)",\
                        # "VAWT Voltage (Volt)", "VAWT Current (Ampere)", "VAWT Power (Watt)", "Anemometer (m/s)",\
                        # "Battery Voltage (Volt)"]

                        print(sensor)
                        sleep(0.1)

        except:
            e = traceback.format_exc()
            if error != e:
                error = e
                print(error)
            try:
                ser = serial.Serial(
                    port = port,
                    baudrate = baudrate,
                    parity = serial.PARITY_NONE,
                    stopbits = serial.STOPBITS_ONE,
                    bytesize = serial.EIGHTBITS,
                    timeout = None
                    )
            except: pass
            sleep(1)

run()
