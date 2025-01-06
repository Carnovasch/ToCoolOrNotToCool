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


def identifyPeaks(prices:list[float], avg_price:float, peakW: int) -> list[bool]:
    left: int = peakW // 2
    right: int = peakW - left - 1

    check_prices: list = prices.copy()    # Be sure not to override anything for possible future use

    peak_list: list = [False] * len(prices)

    # Clean up all prices below average price
    for i, price in enumerate(prices, start=0):
        if price < avg_price:
            check_prices[i] = 0

    MAX_ITERATIONS: int = len(prices)
    iteration: int = 0

    while (max(check_prices) >= avg_price):
        # Identify maximum value in prices, and set pointer to peak
        max_price_ptr: int = check_prices.index(max(check_prices))
        if max_price_ptr < left:
            max_price_ptr = left
        elif max_price_ptr > len(prices) - right - 1:
            max_price_ptr = len(prices) - right - 1

        # Set peak
        for i in range(max_price_ptr - left, max_price_ptr + right + 1):
            if check_prices[i] > 0:  # Set as peak only when can be checked
                peak_list[i] = True

        # Set peak + edges to 0 in check_prices (when applicable)
        for i in range(max_price_ptr - left - 2, max_price_ptr + right + 2):
            if 0 <= i < len(prices):
                check_prices[i] = 0  # Set to 0, so it wont be checked or identified as peak anymore

        iteration += 1

        if (iteration >= MAX_ITERATIONS): # Break when in infinite loop
            break
    
    return peak_list
