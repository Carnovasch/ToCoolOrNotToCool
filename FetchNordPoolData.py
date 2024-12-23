#   *********************************************************************
#   *                                                                   *
#   *   Function:       get_nordpool_prices                             *
#   *   Description:    Get 'DayAhead' data from NordPool for today     *
#   *                   in Euro's for Netherlands                       *
#   *   Author:         Danny Oldenhave                                 *
#   *   Used within:    ToCoolOrNotToCool                               *
#   *   Dependancies:   requests, json, datetime                        *
#   *                                                                   *
#   *********************************************************************


import requests, json
from datetime import date

BACKUPDATA = json.dumps(
        {"backup": True, "deliveryDateCET": "2024-12-10", "version": 2, "updatedAt": "2024-12-09T11:55:38.4137827Z", "deliveryAreas": ["NL"], "market": "DayAhead", "multiAreaEntries": [{"deliveryStart": "2024-12-09T23:00:00Z", "deliveryEnd": "2024-12-10T00:00:00Z", "entryPerArea": {"NL": 77.27}}, {"deliveryStart": "2024-12-10T00:00:00Z", "deliveryEnd": "2024-12-10T01:00:00Z", "entryPerArea": {"NL": 85.0}}, {"deliveryStart": "2024-12-10T01:00:00Z", "deliveryEnd": "2024-12-10T02:00:00Z", "entryPerArea": {"NL": 84.93}}, {"deliveryStart": "2024-12-10T02:00:00Z", "deliveryEnd": "2024-12-10T03:00:00Z", "entryPerArea": {"NL": 83.7}}, {"deliveryStart": "2024-12-10T03:00:00Z", "deliveryEnd": "2024-12-10T04:00:00Z", "entryPerArea": {"NL": 87.21}}, {"deliveryStart": "2024-12-10T04:00:00Z", "deliveryEnd": "2024-12-10T05:00:00Z", "entryPerArea": {"NL": 87.69}}, {"deliveryStart": "2024-12-10T05:00:00Z", "deliveryEnd": "2024-12-10T06:00:00Z", "entryPerArea": {"NL": 100.0}}, {"deliveryStart": "2024-12-10T06:00:00Z", "deliveryEnd": "2024-12-10T07:00:00Z", "entryPerArea": {"NL": 112.79}}, {"deliveryStart": "2024-12-10T07:00:00Z", "deliveryEnd": "2024-12-10T08:00:00Z", "entryPerArea": {"NL": 134.23}}, {"deliveryStart": "2024-12-10T08:00:00Z", "deliveryEnd": "2024-12-10T09:00:00Z", "entryPerArea": {"NL": 157.73}}, {"deliveryStart": "2024-12-10T09:00:00Z", "deliveryEnd": "2024-12-10T10:00:00Z", "entryPerArea": {"NL": 153.13}}, {"deliveryStart": "2024-12-10T10:00:00Z", "deliveryEnd": "2024-12-10T11:00:00Z", "entryPerArea": {"NL": 163.0}}, {"deliveryStart": "2024-12-10T11:00:00Z", "deliveryEnd": "2024-12-10T12:00:00Z", "entryPerArea": {"NL": 135.22}}, {"deliveryStart": "2024-12-10T12:00:00Z", "deliveryEnd": "2024-12-10T13:00:00Z", "entryPerArea": {"NL": 169.15}}, {"deliveryStart": "2024-12-10T13:00:00Z", "deliveryEnd": "2024-12-10T14:00:00Z", "entryPerArea": {"NL": 169.48}}, {"deliveryStart": "2024-12-10T14:00:00Z", "deliveryEnd": "2024-12-10T15:00:00Z", "entryPerArea": {"NL": 176.6}}, {"deliveryStart": "2024-12-10T15:00:00Z", "deliveryEnd": "2024-12-10T16:00:00Z", "entryPerArea": {"NL": 179.97}}, {"deliveryStart": "2024-12-10T16:00:00Z", "deliveryEnd": "2024-12-10T17:00:00Z", "entryPerArea": {"NL": 159.9}}, {"deliveryStart": "2024-12-10T17:00:00Z", "deliveryEnd": "2024-12-10T18:00:00Z", "entryPerArea": {"NL": 181.0}}, {"deliveryStart": "2024-12-10T18:00:00Z", "deliveryEnd": "2024-12-10T19:00:00Z", "entryPerArea": {"NL": 176.65}}, {"deliveryStart": "2024-12-10T19:00:00Z", "deliveryEnd": "2024-12-10T20:00:00Z", "entryPerArea": {"NL": 151.98}}, {"deliveryStart": "2024-12-10T20:00:00Z", "deliveryEnd": "2024-12-10T21:00:00Z", "entryPerArea": {"NL": 120.0}}, {"deliveryStart": "2024-12-10T21:00:00Z", "deliveryEnd": "2024-12-10T22:00:00Z", "entryPerArea": {"NL": 107.2}}, {"deliveryStart": "2024-12-10T22:00:00Z", "deliveryEnd": "2024-12-10T23:00:00Z", "entryPerArea": {"NL": 121.37}}], "blockPriceAggregates": [{"blockName": "Off-peak 1", "deliveryStart": "2024-12-09T23:00:00Z", "deliveryEnd": "2024-12-10T07:00:00Z", "averagePricePerArea": {"NL": {"average": 89.82, "min": 77.27, "max": 112.79}}}, {"blockName": "Peak", "deliveryStart": "2024-12-10T07:00:00Z", "deliveryEnd": "2024-12-10T19:00:00Z", "averagePricePerArea": {"NL": {"average": 163.01, "min": 134.23, "max": 181.0}}}, {"blockName": "Off-peak 2", "deliveryStart": "2024-12-10T19:00:00Z", "deliveryEnd": "2024-12-10T23:00:00Z", "averagePricePerArea": {"NL": {"average": 125.14, "min": 107.2, "max": 151.98}}}], "currency": "EUR", "exchangeRate": 1, "areaStates": [{"state": "Final", "areas": ["NL"]}], "areaAverages": [{"areaCode": "NL", "price": 132.3}]}
    )

def get_nordpool_prices(debug=False) -> dict:
    if  not debug:
        url = "https://dataportal-api.nordpoolgroup.com/api/DayAheadPrices"
        dateParam = date.today()
        params = {
                    "currency": "EUR",
                    "market": "DayAhead",
                    "deliveryArea": "NL",
                    "date": dateParam                
                }

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
        except requests.exceptions.RequestException as e: # Nordpool Data unavailable, return BACKUPDATA dataset
            BACKUPDATA["e"] = e
            return json.loads(BACKUPDATA)

        data = response.json()
        data["backup"] = False
    else:
       return json.loads(BACKUPDATA)

    # Basic check if data is valid, otherwise return BACKUPDATA dataset
    if "areaAverages" not in data or "multiAreaEntries" not in data:
        BACKUPDATA["e"] = "Data from Nordpool was incomplete"
        return json.loads(BACKUPDATA)
    
    return data