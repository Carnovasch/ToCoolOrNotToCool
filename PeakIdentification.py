def identifyPeaks(prices, avg_price, peakW):
    left = peakW // 2
    right = peakW - left - 1

    check_prices = prices.copy()

    for i, price in enumerate(check_prices, start=0):
        if price < avg_price:
            price[i] = 0

    print("Hello", check_prices)    

    # Identify maximum value in prices, and set peak
    max_price_i = prices.index(max(prices))
    if max_price_i == 0:
        max_price_i = left
    elif max_price_i == len(prices - 1):
        max_price_i = len(prices) - right

           

    
    #return is_peak
