#   *************************************************************************************
#   *                                                                                   *
#   *   Title:              ToCoolOrNotToCool                                           *
#   *   Description:        Scraping and parsing NordPool data to identify peaks and    *
#   *                       enable relais accordingly to set cooling equipment          *
#   *   Idea By:            Boudewijn Rosmulder                                         *
#   *   Sponsored by:       xxx                                                         *
#   *   Author:             Danny Oldenhave                                             *
#   *   Last modified:      12-12-2024                                                  *
#   *   Dependancies:       schedule, logging, datetime, smbus2 (?), json               *
#   *   Subdependancies:    requests, datetime, NordPoolAPICall.py, BackUpNPDataFile.py *
#   *                                                                                   *
#   *************************************************************************************
import FetchNordPoolData, PeakIdentification
import logging

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

nordPoolData = FetchNordPoolData.get_nordpool_prices(debug=True)

# Get relevant data from JSON, assume data is correct
AVG_PRICE = nordPoolData["areaAverages"][0]["price"]
prices = []
for priceData in nordPoolData["multiAreaEntries"]:
    prices.append(priceData["entryPerArea"]["NL"])

print(PeakIdentification.identifyPeaks(prices, AVG_PRICE, 3))
