#   ********************************************************************************************
#   *                                                                                          *
#   *   Title:              ToCoolOrNotToCool                                                  *
#   *   Description:        Scraping and parsing NordPool data to identify peaks and           *
#   *                       enable relais accordingly to set cooling equipment                 *
#   *   Idea By:            Boudewijn Rosmulder                                                *
#   *   Sponsored by:       Koelservice Van Tol                                                *
#   *   Author:             Danny Oldenhave                                                    *
#   *   Last modified:      12-12-2024                                                         *
#   *   Dependancies:       schedule, logging, datetime, FetchNordPoolData, PeakIdentification *
#   *   Subdependancies:    requests, json, datetim                                            *
#   *                                                                                          *
#   ********************************************************************************************


import schedule, logging, datetime
import FetchNordPoolData, PeakIdentification


# Set constances to be used; these can be edited
AVG_PRICE_INC = 15              # Amount (EUR) to increase average price to determine peaks
MAX_PEAK_WIDTH = 3              # Amount of maximum hours a peak shall consist of 

# Enable logging
logging.basicConfig(
    filename="ToCoolOrNotToCool.log",
    encoding="utf-8",
    filemode="a",
    format="{asctime} - {levelname} - {message}",
    style="{",
    datefmt="%Y-%m-%d %H:%M"
)

logging.info("Started")

# Initialize global variables
nordPoolData = None
relayEnableList = [False] * 24


# Main function to get and parse NordPool Data to get a relayEnableList to enable/disable relays
def FetchAndParseNPData():
    global nordPoolData
    nordPoolData = FetchNordPoolData.get_nordpool_prices(debug=True)

    # Get relevant data from JSON, assume data is correct
    AVG_PRICE = nordPoolData["areaAverages"][0]["price"] + AVG_PRICE_INC
    prices = []
    for priceData in nordPoolData["multiAreaEntries"]:
        prices.append(priceData["entryPerArea"]["NL"])

    # Get enablelist for enabling relays
    global relayEnableList
    relayEnableList = PeakIdentification.identifyPeaks(prices, AVG_PRICE, MAX_PEAK_WIDTH)

    print(prices)


# Main function to set relays based on relayEnableList
def setRelays():
    hour = datetime.datetime.now().hour

    global relayEnableList
    enable = relayEnableList[hour]
    
    print("Settting relays based on", relayEnableList)
    print("Hour is", hour, "relay enable is", enable)



# Set scheduling scheme
# At beginning of each day, get new list from parsed NordPool data
#schedule.every().day.at("00:01").do(FetchAndParseNPData())
# At beginning of each hour use the relaysEnableList to enable/disable relays
#schedule.every().hour.at(":05").do(setRelays)


# Start loop to run schedules jobs
#while True:
#    schedule.run_pending()
#    time.sleep(1)


FetchAndParseNPData()
print(relayEnableList)