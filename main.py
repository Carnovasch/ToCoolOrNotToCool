#   ********************************************************************************************
#   *                                                                                          *
#   *   Title:              ToCoolOrNotToCool                                                  *
#   *   Description:        Scraping and parsing NordPool data to identify peaks and           *
#   *                       enable relais accordingly to set cooling equipment                 *
#   *   Idea By:            Boudewijn Rosmulder                                                *
#   *   Sponsored by:       Koelservice Van Tol                                                *
#   *   Author:             Danny Oldenhave                                                    *
#   *   Last modified:      03-01-2025                                                         *
#   *   Dependancies:       json, schedule, logging, datetime, time, smbus2                    *
#   *   Modules:            FetchNordPoolData, PeakIdentification                              *
#   *   Subdependancies:    requests, json, datetime                                           *
#   *                                                                                          *
#   ********************************************************************************************


import json, schedule, logging, datetime, time
import smbus
import FetchNordPoolData, PeakIdentification

# Loading server config data from file
with open("./ServerConfig.json", "r") as server_config:
    SERVER_DATA = json.load(server_config)

AVG_PRICE_INC: int = SERVER_DATA["GeneralConfig"]["AVG_PRICE_INC"]       # Amount (EUR) to increase average price to determine peaks
MAX_PEAK_WIDTH: int = SERVER_DATA["GeneralConfig"]["MAX_PEAK_WIDTH"]     # Amount of maximum hours a peak shall consist of 
RELAY_TO_SWITCH: int = SERVER_DATA["GeneralConfig"]["RELAY_TO_SWITCH"]   # Set which relay to enable / disable; 1, 2, 3 or 4

fetch_Success: bool = False

# Setting constances for Relayshield
DEVICE_BUS: int = SERVER_DATA["RelayShieldConfig"]["DEVICE_BUS"]
DEVICE_ADDR = "0x10" #SERVER_DATA["RelayShieldConfig"]["DEVICE_ADDR"]
DEVICE_ON = "0xff" #SERVER_DATA["RelayShieldConfig"]["DEVICE_ON"]
DEVICE_OFF = "0x00" #SERVER_DATA["RelayShieldConfig"]["DEVICE_OFF"]
bus = smbus.SMBus(DEVICE_BUS)

# Initialize logging
logging.basicConfig(
    filename="ToCoolOrNotToCool.log",
    encoding="utf-8",
    filemode="w",
    format="{asctime} - {levelname} - {message}",
    style="{",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO
)

# Initialize global variables
nordPoolData: dict = None
relayEnableList: list = [False] * 24


def CalcNewAvgPrice(prices, peaks) -> float:
    filtered_values: list = [value for value, include in zip(prices, peaks) if not include] # Get only prices when not in peak

    #Calculate new average and return, return 0 when lists are empty (catch when divide by 0)
    average: float = 0.0
    if filtered_values:
        average = round(sum(filtered_values) / len(filtered_values), 2)
    return average


# Main function to get and parse NordPool Data to get a relayEnableList to enable/disable relays
def FetchAndParseNPData(initial: bool=False) -> None:
    global fetch_Success

    if initial == False and fetch_Success == True:  # Only run function when program starts, beginning of each day, or when fetchig failed first time at beginning of the day
        return
    if fetch_Success == False and initial == False:
        logging.info("Try fetching data from Nordpool again after failure")
    else:
        logging.info("Start fetching data from Nordpool")

    fetch_Success = False

    global nordPoolData
    nordPoolData = FetchNordPoolData.get_nordpool_prices()

    if nordPoolData["backup"] == False:
        logging.info("Nordpool data fetched succesfully")
        if initial == False:    # Only set fetch sucess to True at beginning of each day, not when program starts
            fetch_Success = True       
    elif "e" in nordPoolData : # An error has occured fetching data from Nordpool
        logging.info("Couldn't fetch Nordpool data, using Backupfile")
        logging.info("Error: %s", nordPoolData["e"])
    else: # Debugging mode
        logging.info("Debug mode, using Backupfile")
     
    # Get relevant data from JSON, assume data is correct
    OLD_AVG_PRICE: float = nordPoolData["areaAverages"][0]["price"]
    AVG_PRICE: float = OLD_AVG_PRICE + AVG_PRICE_INC

    logging.info("Average price for today: E %s", OLD_AVG_PRICE)

    prices: list = []
    for priceData in nordPoolData["multiAreaEntries"]:
        prices.append(priceData["entryPerArea"]["NL"])

    # Get enablelist for enabling relays
    global relayEnableList
    relayEnableList = PeakIdentification.identifyPeaks(prices, AVG_PRICE, MAX_PEAK_WIDTH)

    # Calculate new average price for today and log
    newAVGPrice: float = CalcNewAvgPrice(prices, relayEnableList)

    logging.info("New average price for today is: E %s, improvement of: E %s", newAVGPrice, round(OLD_AVG_PRICE-newAVGPrice, 2))
    logging.info("Calculated savings for today: E %s", round(newAVGPrice * 24, 2))


def TurnAllRelaysOff() -> None:
    logging.info("Turn all relays off")
    for i in range(1,5):
            bus.write_byte_data(DEVICE_ADDR, i, DEVICE_OFF)    


# Main function to set relays based on relayEnableList
def setRelays() -> None:
    logging.info("Start of new hour, getting ready to set Relays")
  
    TurnAllRelaysOff()

    hour:int = datetime.datetime.now().hour

    global relayEnableList
    enable:bool = relayEnableList[hour]
    
    logging.info("Hour is %s, relay enable is %s", hour, enable)

    if enable == True:
        logging.info("Enable relay %s", RELAY_TO_SWITCH)
        bus.write_byte_data(DEVICE_ADDR, RELAY_TO_SWITCH, DEVICE_ON)
  

if __name__ == "__main__":
    logging.info("Started the program")

    TurnAllRelaysOff()

    # Default to 1, if RELAY_TO_SWITCH is not set properly
    if RELAY_TO_SWITCH not in range(1, 5):
        RELAY_TO_SWITCH = 1
  
    # Get initial data from Nordpool at startup of the program and set relay accordingly
    FetchAndParseNPData(True)
    setRelays()

    # Set scheduling scheme
    schedule.every().day.at("00:01").do(FetchAndParseNPData)    # At beginning of each day, get new list from parsed NordPool data  
    schedule.every().day.at("00:02").do(FetchAndParseNPData)    # At beginning of each day, get new list from parsed NordPool data  
    schedule.every().hour.at(":05").do(setRelays)               # At beginning of each hour use the relaysEnableList to enable/disable relays

    while True:
        schedule.run_pending()
        time.sleep(1)