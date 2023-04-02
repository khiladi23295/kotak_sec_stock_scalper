# A stock scalper built on Kotak Securities platform through python API.

The need to built this scalper:
	Since scalping is a very fast process. it is not possible to do it when placing orders manually. Hence this code is used to put buy and
	sell orders automatically.
	   
Limitations in the code as of now:

	1- Only LONG trades can be placed for now but functionality for SHORT orders will be added in later versions.
	
	2- A threshold level for the stock is added but not being used currently. Threshold level is the price of the
	   stock which is set by the user. It acts as a trigger price for a trade to be executed in either directions(LONG/SHORT).
	   
	3- StopLoss/TakeProfit are not cancelled automatically if price hits either of them. If either of the order is not cancelled, broker platform treats
	   it as a new order and opens a new position. This will also be fixed in later versions.
	   
	4- Currently only 2 stocks can be traded but in future limit will be increased.
	
	5- Currently the code is cluttered, repetitive code will replaced with functions.
	
	6- Since this is a test code, quantity has been fixed to 1. In future there will be 2 options available, either you can fix the trade amount per trade or 
	   it will be calculated dynamically based on your account cash balance.
	   
Current Features:

	1- All the exceptions in the program are written to a text file for debugging..
	
	2- TakeProfit is set at 0.75% and StopLoss is set at 0.25%. They are kept small as this is a Intraday Scalping startegy.
