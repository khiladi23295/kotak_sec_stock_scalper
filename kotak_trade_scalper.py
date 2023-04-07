from ks_api_client import ks_api
from datetime import datetime
import requests
import pandas as pd
import math
import time

access_token = '' # Your Access Token Here
consumer_key = ''  # Your Consumer Key Here
consumer_secret = '' # Your Consumer Secret

userid = '' # Your Username Here
password = '' # Your Password Here

#-----------------Login----------------------------

# Defining the host is optional and defaults to https://sbx.kotaksecurities.com/apim
#Replace app-id with the name of the app you created in the kotak api portal
client = ks_api.KSTradeApi(access_token = access_token, userid = userid, consumer_key = consumer_key,ip = "127.0.0.1", app_id = "DefaultApplication", \
host = "https://tradeapi.kotaksecurities.com/apim", consumer_secret = consumer_secret)
login1=client.login(password = password)
login2=client.session_2fa()

#----------------Getting Stocks  for the day--------------------
df = pd.read_csv("C:/abcd/Some_Path/StockNames.txt", sep=",",header=None,names=["First_Stock","First_Threshold","Second_Stock","Second_Threshold"])
symbol_name = [df.iloc[0,0].upper(),df.iloc[0,2].upper()]
threshold_price = [df.iloc[0,1],df.iloc[0,3]]
print("Symbol Name: ",symbol_name,"Threshold Price: ",threshold_price)

#--------------Fetching all stocks list---------------------------
url = 'https://tradeapi.kotaksecurities.com/apim/scripmaster/1.1/filename'
headers = { 'accept' : 'application/json', 'consumerKey' : f"{consumer_key}", 'Authorization' : f"Bearer  {access_token}"}
res = requests.get(url, headers=headers).json()
cash = res['Success']['cash']
symbol_list = pd.read_csv(cash, sep='|')

#--------------Getting instrument token and current price-------------------
instrument_token_list = []
current_price_list = []
for i in symbol_name:
    print(i)
    try:
        instrumentToken = symbol_list[(symbol_list['instrumentName'] == i) & (symbol_list['exchange'] == 'NSE') & (symbol_list['instrumentType'] == 'EQ')].iloc[0,0]
        instrument_token_list.append(int(instrumentToken))
            
        symbol_price = float(client.quote(instrument_token = int(instrumentToken))['success'][0]['ltp'])
        current_price_list.append(symbol_price)  
    except Exception as e:
        with open('log.txt', 'a') as file:
            file.write("\n"+"Exception occurred while selecting stocks : "+str(e))
         
print(instrument_token_list, current_price_list)

#--------------Getting Required Margin-----------------------------
order_info = []                                  # This section will be used in future to calculate the quantity of the stocks 
for i in range(len(instrument_token_list)):      # based on the leverage provided in the stock
    order_info.append( 
        {"instrument_token": instrument_token_list[i], "quantity": 1, "price": current_price_list[i], "amount": 0, "trigger_price": 0}
        )
    
margin_required_list = []
margin_required = client.margin_required(transaction_type = "BUY",order_info = order_info)
for i in range(len(instrument_token_list)):
    margin_required_list.append(margin_required['Success'][i]['normal'])

#----------------Calculating quantity------------------------------
# cash_balance = 5000  # Has kept the account balance fixed for now but in future will get it through a api call
# quantity_list = [math.floor((cash_balance/margin_required_list[0])),math.floor((cash_balance/margin_required_list[1]))]
# quantity_list     # Calculating the quantity that can be bought using the cash balance in the account

#-------------------Placing the orders---------------------------
counter=len(instrument_token_list)
flag = 1
while(flag ==1):
    now = datetime.now()
    my_time_string = "09:15:00"   # Trades will execute at exactly 9:15 AM when the Stock Market opens
    my_datetime = datetime.strptime(my_time_string, "%H:%M:%S")
    print("Date Time: ",my_datetime)
    my_datetime = now.replace(hour=my_datetime.time().hour, minute=my_datetime.time().minute, second=my_datetime.time().second, microsecond=0)
    if (now >= my_datetime):
        with open('log.txt', 'a') as file:
            file.write("\n"+"Time of Execution: "+str(now))
        for i in instrument_token_list:   # Loop that places the buy orders for both the stocks
            try:
                placed_order_details = client.place_order(order_type = "MIS", instrument_token = i, transaction_type = "BUY",\
                               quantity = 1, price = 0, disclosed_quantity = 0,\
                               validity = "GFD", variety = "REGULAR") # REGULAR
                time.sleep(1)
                with open('log.txt', 'a') as file:
                    file.write("\n"+"Placed Order Details: "+str(placed_order_details))
            except Exception as e:
                counter-=1
                with open('log.txt', 'a') as file:
                    file.write("\n"+"Exception occurred in placing order and the exception is :"+str(e))
        
        #----------------Placing the TP/SL orders-----------------------------
        order_details = client.positions(position_type = "TODAYS")
        time.sleep(1)
        for i in range(counter):    
            exec_price = round(order_details['Success'][i]['averageStockPrice'],2)
            instrumentToken = order_details['Success'][i]['instrumentToken']
            quantity = order_details['Success'][i]['buyTradedQtyLot']
            
            number = round(exec_price + (exec_price * .0075),2) # Setting Take Profit at 0.75%
            decimal = (round((number - math.floor(number)),2)*100)/10
            decimal2 = round(((decimal - math.floor(decimal))/10),2)
            take_profit = round((number - decimal2),2)
            with open('log.txt', 'a') as file:
                file.write("\n"+"Take Profit: "+str(take_profit))
            
            number = round(exec_price - (exec_price * .0025),2) # Setting Stop Loss at 0.25%
            decimal = (round((number - math.floor(number)),2)*100)/10
            decimal2 = round(((decimal - math.floor(decimal))/10),2)
            stop_loss = round((number - decimal2),2)
            with open('log.txt', 'a') as file:
                file.write("\n"+"Stop Loss: "+str(stop_loss))
                
            try:
                take_profit_order = client.place_order(order_type = "MIS", instrument_token = instrumentToken, transaction_type = "SELL",\
                           quantity = quantity, price = take_profit, trigger_price = 0, disclosed_quantity = 0,\
                           validity = "GFD", variety = "REGULAR") # Placing the Take profit Order
                
            except Exception as e:
                client.place_order(order_type = "MIS", instrument_token = instrumentToken, transaction_type = "SELL",\
                           quantity = quantity, price = 0,  disclosed_quantity = 0,\
                           validity = "GFD", variety = "REGULAR") # In case Take profit order fails, we will exit the stock immediately
#                 
                with open('log.txt', 'a') as file:
                    file.write("\n"+"Exception occured while placing Take Profit order and the exception is "+str(e))
                    
            time.sleep(1)
            
            try:
                stop_loss_order = client.place_order(order_type = "MIS", instrument_token = instrumentToken, transaction_type = "SELL",\
                           quantity = quantity, price = 0, trigger_price = stop_loss, disclosed_quantity = 0,\
                           validity = "GFD", variety = "REGULAR") # Placing the Stop Loss Order
                
            except Exception as e:
                client.place_order(order_type = "MIS", instrument_token = instrumentToken, transaction_type = "SELL",\
                           quantity = quantity, price = 0, disclosed_quantity = 0,\
                           validity = "GFD", variety = "REGULAR")  # In case Stop Loss order fails, we will exit the stock immediately
                
                with open('log.txt', 'a') as file:
                    file.write("\n"+"Exception occured while placing Stop Loss order and the exception is "+str(e))
                    
            time.sleep(1)
    if (now >= my_datetime):
        flag =0 #will break because of time check when time is less
    time.sleep(1)
client.logout() # Logout the session created through  Kotak API
