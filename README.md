# A stock scalper built on Kotak Securities platform through python API.

Need to built this scalper:
	Since scalping is a very fast process. it is not possible to do it by manually placing orders. Hence
	this code is used to put buy ans sell orders automatically.
	   
Limitations in the code as of now:

	1- Only LONG trades can be placed for now but functionality for SHORT orders will be added in later versions.
	
	2- A threshold level for the stock is added but nor being used currently. Threshold level is the price of the
	   stock which is set by the user. User can decide if the trade should be executed in case the stocks' current
	   price id above or below the threshold depending on the type(LONG/SHORT) of trade.