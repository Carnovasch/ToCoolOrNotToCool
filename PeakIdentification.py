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


def identifyPeaks(prices:list[float], avg_price:float, max_Peaks: int, max_Peak_len: int, qrt_Off: int) -> list[bool]:
    left: int = max_Peak_len // 2
    right: int = max_Peak_len - left - 1

    check_prices: list = prices.copy()    # Be sure not to override anything for possible future use

    peak_list: list = [False] * len(prices)
    check_list: list = [True] * len(prices)

    identified_peaks: int = 0
    iteration: int = 0
    MAX_ITERATIONS: int = len(prices) // 2

    # Clean up all prices below average price
    for i, price in enumerate(prices, start=0):
        if price < avg_price:
            check_prices[i] = 0

    while identified_peaks < max_Peaks:
        # Identify maximum value in prices, and set pointer to peak
        max_price_ptr: int = check_prices.index(max(check_prices))

        # Check if peak is valid and set pointer to middle of peak
        valid_peak: bool = True
        if check_list[max_price_ptr] == True:

            # Align pointer for edge cases (never start or end a day with the relay on, based on '15 minutes' off before and after peak
            if max_price_ptr < left + qrt_Off:
                max_price_ptr = left + qrt_Off
            elif max_price_ptr > len(prices) - right - 1 - qrt_Off:
                max_price_ptr = len(prices) - right - 1 - qrt_Off

            # Check if total width of peak is valid
            for j in range(max_price_ptr - left, max_price_ptr + right + 1):
                if check_list[j] == False:
                    valid_peak = False
                    break
        else:
            valid_peak = False
      
        # When we have identified a valid total peak, set peak
        if valid_peak == True:
            identified_peaks += 1
            # Set peak
            for i in range(max_price_ptr - left, max_price_ptr + right + 1):
                peak_list[i] = True
            # Set check_list and check_prices, so they wont be checked again for a new peak
            for i in range(max_price_ptr - left - qrt_Off, max_price_ptr + right + 1 + qrt_Off):
                check_list[i] = False
                check_prices[i] = 0

        iteration += 1
        
        if iteration >= MAX_ITERATIONS: # Break when in infinite loop
            break
    
    return peak_list
