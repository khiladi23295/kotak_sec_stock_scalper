# A stock scalper built on Kotak Securities platform through python API.

The need to build this scalper:
	Since scalping is a very fast process. it is not possible to do it when placing orders manually. Hence this code is used to put buy and
	sell orders automatically.
	   
Limitations in the code as of now:

	1- Only LONG trades can be placed for now but functionality for SHORT orders will be added in later versions.
	
	2- A threshold level for the stock is added but is not being used currently. Threshold level is the price of the
	   stock which is set by the user. It acts as a trigger price for a trade to be executed in either direction (LONG/SHORT).
	   
	3- Currently only 2 stocks can be traded but in the future limit will be increased.
	
	4- Currently the code is cluttered, repetitive code will be replaced with functions. (Fixed)
	
	5- Since this is a test code, the quantity has been fixed to 1. In the future, there will be 2 options available, either you can fix the trade amount per trade or 
	   it will be calculated dynamically based on your account cash balance. (Fixed)
	   
Current Features:

	1- All the exceptions in the program are written to a text file for debugging.
	
	2- TakeProfit is set at 0.75% and StopLoss is set at 0.25%. They are kept small as this is an Intraday Scalping strategy.

 	3 - StopLoss/TakeProfit are now canceled automatically if the price hits either of them. If either of the order is not canceled, the broker platform treats
	   it as a new order and opens a new position.

    	4 - The quantity is now calculated by the fixed trade amount per stock set by the user.

Some Broker Limitations:

 	1 - While trading with Kotak Securities, there is a latency of about 50 seconds on average between the orders getting sent and being executed on the exchange. Orders are getting sent to the broker exactly at 09:15:00 but it takes time for the orders to get executed. This could be a limitation set by the broker.

  	2 - As compared to other brokers, Kotak Securities does not offer intraday leverage on the majority of the stocks. For any given stock, Zerodha might offer a 5x leverage but Kotak will give zero leverage. This reduces the quantity of the stocks you can buy, which is key to being profitable in scalping. 
