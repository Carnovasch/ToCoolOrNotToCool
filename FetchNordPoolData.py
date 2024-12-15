#   *********************************************************************
#   *                                                                   *
#   *   Function:       NodPoolAPICall                                  *
#   *   Description:    Get 'DayAhead' data from NordPool for tomorrow  *
#   *                   in Euro's for Netherlands                       *
#   *   Author:         Danny Oldenhave                                 *
#   *   Used within:    ToCoolOrNotToCool                               *
#   *   Dependancies:   requests, datetime                              *
#   *                                                                   *
#   *********************************************************************

import requests
from datetime import date

def get_nordpool_prices():
    url = "https://dataportal-api.nordpoolgroup.com/api/DayAheadPrices"
    dateParam = date.today()
    params = {
                "currency": "EUR",
                "market": "DayAhead",
                "deliveryArea": "NL",
                "date": dateParam                
            }

    reponse = requests.get(url, params=params)
    reponse.raise_for_status()
    data = reponse.json()
    return data
    
print(get_nordpool_prices())