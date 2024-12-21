import time as t
import smbus
import sys
import schedule

DEVICE_BUS = 1
DEVICE_ADDR = 0x10
bus = smbus.SMBus(DEVICE_BUS)



def Relay():
    try:
        for i in range(1,5):
                bus.write_byte_data(DEVICE_ADDR, i, 0xFF)
                t.sleep(1)
                bus.write_byte_data(DEVICE_ADDR, i, 0x00)
                t.sleep(1)
    except KeyboardInterrupt as e:
            print("Exit")
            sys.exit()


# Set scheduling scheme
# At beginning of each day, get new list from parsed NordPool data
schedule.every().day.at("14:55").do(Relay)
# At beginning of each hour use the relaysEnableList to enable/disable relays
#schedule.every().hour.at(":06").do(setRelays)


# Start loop to run schedules jobs
while True:
    schedule.run_pending()
    t.sleep(1)


