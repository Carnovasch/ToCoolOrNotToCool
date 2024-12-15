#   **********************************************************************
#   *                                                                    *
#   *   Function:       identifyPeaks                                    *
#   *   Description:    Return a boolean peak list with identified peaks *
#   *                   with a maximum width                             *
#   *   Author:         Danny Oldenhave                                  *
#   *   Used within:    ToCoolOrNotToCool                                *
#   *   Dependancies:   none                                             *
#   *                                                                    *
#   **********************************************************************


def identifyPeaks(prices, avg_price, peakW):
    left = peakW // 2
    right = peakW - left - 1

    check_prices = prices.copy()

    peak_list = [False] * len(prices)

    # Clean up all prices below average price
    for i, price in enumerate(prices, start=0):
        if price < avg_price:
            check_prices[i] = 0

    MAX_ITERATIONS = len(prices)
    iteration = 0

    while (max(check_prices) > 0):
        # Identify maximum value in prices, and set peak
        max_price_i = prices.index(max(check_prices))
        if max_price_i == 0:
            max_price_i = left
        elif max_price_i == len(prices) - 1:
            max_price_i = len(prices) - right

        # Set peak
        for i in range(max_price_i - left, max_price_i + right + 1):
            peak_list[i] = True

        # Set peak + edges to 0 in check_prices (when applicable)
        for i in range(max_price_i - left - 2, max_price_i + right + 2):
            if (i >= 0 or i < len(prices)):
                check_prices[i] = 0  

        iteration += 1

        if (iteration >= MAX_ITERATIONS): # Break when in infinite loop
            break

    
    return peak_list
