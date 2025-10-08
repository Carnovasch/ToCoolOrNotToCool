#   ********************************************************************************************
#   *                                                                                          *
#   *   Title:              ToCoolOrNotToCool                                                  *
#   *   Description:        Scraping and parsing NordPool data to identify peaks and           *
#   *                       enable relais accordingly to set cooling equipment                 *
#   *   Idea By:            Boudewijn Rosmulder                                                *
#   *   Sponsored by:       Koelservice Van Tol                                                *
#   *   Author:             Danny Oldenhave                                                    *
#   *   Last modified:      07-10-2025                                                         *
#   *   Dependancies:       json, schedule, logging, datetime, time, smbus2                    *
#   *   Modules:            FetchNordPoolData, PeakIdentification                              *
#   *   Subdependancies:    requests, json, datetime                                           *
#   *                                                                                          *
#   ********************************************************************************************


import json, schedule, logging, datetime, time
import smbus
import FetchNordPoolData, PeakIdentification

# Loading server config data from file
with open("/home/boudewijn/ToCoolOrNotToCool/ServerConfig.json", "r") as server_config:
# with open("./ServerConfig.json", "r") as server_config:
    SERVER_DATA = json.load(server_config)

AVG_PRICE_INC: int = SERVER_DATA["GeneralConfig"]["AVG_PRICE_INC"]      # Amount (EUR) to increase average price to determine peaks
MAX_PEAKS_DAY: int = SERVER_DATA["GeneralConfig"]["MAX_PEAKS_DAY"]      # Amount of maximum peaks a day
MAX_PEAK_LEN: int = SERVER_DATA["GeneralConfig"]["MAX_PEAK_LEN"]        # How many 'fifteen minutes' a peak shall consist of
QRT_OFF: int = SERVER_DATA["GeneralConfig"]["QRT_OFF"]                  # How many 'fifteen minutes' the relais will turn off before and after a peak
RELAY_TO_SWITCH: int = SERVER_DATA["GeneralConfig"]["RELAY_TO_SWITCH"]   # Set which relay to enable / disable; 1, 2, 3 or 4

fetch_Success: bool = False

# Setting constances for Relayshield
DEVICE_BUS: int = SERVER_DATA["RelayShieldConfig"]["DEVICE_BUS"]
DEVICE_ADDR = 0x10 
DEVICE_ON = 0xff    
DEVICE_OFF = 0x00 
bus = smbus.SMBus(1)

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
def FetchAndParseNPData(state:str) -> None:
    global fetch_Success

    if state == "inital" or state == "new":
        logging.info("Start fetching data from Nordpool")
        fetch_Success = False
    elif state == "secondary" and fetch_Success == False:
        logging.info("Try fetching data from Nordpool again after failure")
    else:   # Do not fetch and parse Nordpool data and create a new peaklist when this function was a succes at beginning of a new day
        return

    global nordPoolData
    nordPoolData = FetchNordPoolData.get_nordpool_prices()

    if nordPoolData["backup"] == False:
        logging.info("Nordpool data fetched succesfully")
        if not state == "initial":    # Only set fetch sucess to True at beginning of each day, not when program starts
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
    relayEnableList = PeakIdentification.identifyPeaks(prices, AVG_PRICE, MAX_PEAKS_DAY, MAX_PEAK_LEN, QRT_OFF)

    # Get the indices of the '15-minutes' the relais will be enabled for logging
    enabled_for_logging: list = []
    for i in range(len(relayEnableList)):
        if relayEnableList[i] == True:
            enabled_for_logging.append(i)

    # Calculate new average price for today and log
    newAVGPrice: float = CalcNewAvgPrice(prices, relayEnableList)

    logging.info("New average price for today is: E %s, improvement of: E %s", newAVGPrice, round(OLD_AVG_PRICE-newAVGPrice, 2))
    logging.info("Possible savings for today: E %s", round((OLD_AVG_PRICE - newAVGPrice) * 24, 2))
    logging.info("Relais will be enabled on the following '15-minutes' for today: %s", enabled_for_logging)


def TurnAllRelaysOff() -> None:
    logging.info("Turn all relays off")
    for i in range(1,5):
            # print("Turning Relays Off")
            bus.write_byte_data(DEVICE_ADDR, i, DEVICE_OFF)    


# Main function to set relays based on relayEnableList
def setRelays() -> None:
    logging.info("Start of new '15-minutes', getting ready to set Relays")
  
    TurnAllRelaysOff()

    # Get current '15-minutes' of the day in range 0 upto 96
    current_datetime = datetime.datetime.now()
    hour:int = current_datetime.hour
    minute:int = current_datetime.minute
    qrt_of_day:int = int((hour * 60 + minute) // 15)

    global relayEnableList
    enable:bool = relayEnableList[qrt_of_day]
    
    logging.info("Time is %s, '15-th minute' of day is %s, relay enable is %s", current_datetime, qrt_of_day, enable)

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
    FetchAndParseNPData("inital")
    setRelays()

    # Set scheduling scheme, for each schedule a minute added for security
    schedule.every().day.at("00:01").do(FetchAndParseNPData, state="new")           # At beginning of each day, parse and get new list from NordPool data  
    schedule.every().day.at("00:02").do(FetchAndParseNPData, state="secondary")     # When applicable, secondary try of parse and get new list from NordPool data 
    # Every 15 minutes use the relaysEnableList to enable/disable relays 
    schedule.every().hour.at(":01").do(setRelays)
    schedule.every().hour.at(":16").do(setRelays)
    schedule.every().hour.at(":31").do(setRelays)
    schedule.every().hour.at(":46").do(setRelays)
    #schedule.every(15).minutes.do(setRelays)                                        # Every 15 minutes use the relaysEnableList to enable/disable relays
    #schedule.every().hour.at(":05").do(setRelays)                                  # At beginning of each hour use the relaysEnableList to enable/disable relays

    while True:
        schedule.run_pending()
        time.sleep(1)