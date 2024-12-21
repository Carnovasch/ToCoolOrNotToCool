#   ********************************************************************************************
#   *                                                                                          *
#   *   Title:              ToCoolOrNotToCool                                                  *
#   *   Description:        Scraping and parsing NordPool data to identify peaks and           *
#   *                       enable relais accordingly to set cooling equipment                 *
#   *   Idea By:            Boudewijn Rosmulder                                                *
#   *   Sponsored by:       Koelservice Van Tol                                                *
#   *   Author:             Danny Oldenhave                                                    *
#   *   Last modified:      21-12-2024                                                         *
#   *   Dependancies:       schedule, logging, datetime, time, smbus2                          *
#   *   Modules:            FetchNordPoolData, PeakIdentification                              *
#   *   Subdependancies:    requests, json, datetim                                            *
#   *                                                                                          *
#   ********************************************************************************************


import schedule, logging, datetime, time
import smbus
import FetchNordPoolData, PeakIdentification

# Set constances to be used; these can be edited
AVG_PRICE_INC = 15              # Amount (EUR) to increase average price to determine peaks
MAX_PEAK_WIDTH = 3              # Amount of maximum hours a peak shall consist of 
RELAY_TO_SWITCH = 1             # Set which relay to enable / disable; 1, 2, 3 or 4

# Setting constances for Relayshield
DEVICE_BUS = 1
DEVICE_ADDR = 0x10
DEVICE_ON = 0xff
DEVICE_OFF = 0x00
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
nordPoolData = None
relayEnableList = [False] * 24


def CalcNewAvgPrice(prices, peaks) -> float:
    filtered_values = [value for value, include in zip(prices, peaks) if not include] # Get only prices when not in peak

    #Calculate new average and return, return 0 when lists are empty (catch when divide by 0)
    if filtered_values:
        average = round(sum(filtered_values) / len(filtered_values), 2)
    else:
        average = 0.0
    return average


# Main function to get and parse NordPool Data to get a relayEnableList to enable/disable relays
def FetchAndParseNPData() -> None:
    logging.info("Start fetching data from Nordpool")

    global nordPoolData    
    nordPoolData = FetchNordPoolData.get_nordpool_prices()

    if nordPoolData["backup"] == False:
        logging.info("Nordpool data fetched succesfully")
    else:
        logging.info("Couldn't fetch Nordpool data, using Backupfile")
     
    # Get relevant data from JSON, assume data is correct
    OLD_AVG_PRICE = nordPoolData["areaAverages"][0]["price"]
    AVG_PRICE = OLD_AVG_PRICE + AVG_PRICE_INC

    logging.info("Average price for today: E %s", OLD_AVG_PRICE)

    prices = []
    for priceData in nordPoolData["multiAreaEntries"]:
        prices.append(priceData["entryPerArea"]["NL"])

    # Get enablelist for enabling relays
    global relayEnableList
    relayEnableList = PeakIdentification.identifyPeaks(prices, AVG_PRICE, MAX_PEAK_WIDTH)

    # Calculate new average price for today and log
    newAVGPrice = CalcNewAvgPrice(prices, relayEnableList)

    logging.info("New average price for today is: E %s, improvement of: E %s", newAVGPrice, round(OLD_AVG_PRICE-newAVGPrice, 2))
    logging.info("Calculated savings for today: E %s", round(newAVGPrice * 24, 2))


def TurnAllRelaysOff() -> None:
    for i in range(1,5):
            bus.write_byte_data(DEVICE_ADDR, i, DEVICE_OFF)    

# Main function to set relays based on relayEnableList
def setRelays() -> None:
    logging.info("Start of new hour, getting ready to set Relays")
    logging.info("Turn all relays off")

    TurnAllRelaysOff()

    hour = datetime.datetime.now().hour

    global relayEnableList
    enable = relayEnableList[hour]
    
    logging.info("Hour is %s, relay enable is %s", hour, enable)

    if enable == True:
        logging.info("Enable relay %s", RELAY_TO_SWITCH)
        bus.write_byte_data(DEVICE_ADDR, RELAY_TO_SWITCH, DEVICE_ON)
  

if __name__ == "__main__":
    logging.info("Started the program")

    # Default to 1, if RELAY_TO_SWITCH is not set properly
    if RELAY_TO_SWITCH not in range(1, 5):
        RELAY_TO_SWITCH = 1

    TurnAllRelaysOff()

    # Get initial data from Nordpool at startup of the program and set relay accordingly
    FetchAndParseNPData()
    setRelays()

    # Set scheduling scheme
    schedule.every().day.at("00:01").do(FetchAndParseNPData)    # At beginning of each day, get new list from parsed NordPool data  
    schedule.every().hour.at(":05").do(setRelays)   # At beginning of each hour use the relaysEnableList to enable/disable relays

    while True:
        schedule.run_pending()
        time.sleep(1)