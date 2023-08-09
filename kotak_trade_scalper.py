from ks_api_client import ks_api
from datetime import datetime
import credentials as cr
import requests
import pandas as pd
import math
import time

access_token = cr.user_details["access_token"]
consumer_key = cr.user_details["consumer_key"]
consumer_secret = cr.user_details["consumer_secret"]

userid = cr.user_details["username"]
password = cr.user_details["password"]


def exception_logs(msg, e):
    with open('log.txt', 'a') as file:
        file.write("\n" + msg + str(e))

def cancel_order(instrumentToken, quantity):
    client.place_order(order_type="MIS", instrument_token=instrumentToken, transaction_type="SELL",
                       quantity=quantity, price=0, disclosed_quantity=0, validity="GFD", variety="REGULAR")
# -----------------Login----------------------------

# Replace app-id with the name of the app you created in the kotak api portal


client = ks_api.KSTradeApi(access_token=access_token, userid=userid, consumer_key=consumer_key,
                           ip="127.0.0.1", app_id="DefaultApplication",
                           host="https://tradeapi.kotaksecurities.com/apim", consumer_secret=consumer_secret)
login1 = client.login(password=password)
login2 = client.session_2fa()

# ----------------Getting Stocks  for the day--------------------
df = pd.read_csv("C:/Users/Documents/GitHub/kotak_sec_stock_scalper/StockNames.txt", sep=",", header=None,
                 names=["First_Stock", "First_Threshold", "Second_Stock", "Second_Threshold"])
symbol_name = [df.iloc[0, 0].upper(), df.iloc[0, 2].upper()]
threshold_price = [df.iloc[0, 1], df.iloc[0, 3]]
print("Symbol Name: ", symbol_name, "Threshold Price: ", threshold_price)

# --------------Fetching all stocks list---------------------------
url = 'https://tradeapi.kotaksecurities.com/apim/scripmaster/1.1/filename'
headers = {'accept': 'application/json', 'consumerKey': f"{consumer_key}", 'Authorization': f"Bearer  {access_token}"}
res = requests.get(url, headers=headers).json()
cash = res['Success']['cash']
symbol_list = pd.read_csv(cash, sep='|')

# --------------Getting instrument token and current price-------------------
instrument_token_list = []
current_price_list = []
for i in symbol_name:
    print(i)
    try:
        instrumentToken = symbol_list[(symbol_list['instrumentName'] == i) & (symbol_list['exchange'] == 'NSE') &
                                      (symbol_list['instrumentType'] == 'EQ')].iloc[0, 0]
        instrument_token_list.append(int(instrumentToken))
            
        symbol_price = float(client.quote(instrument_token=int(instrumentToken))['success'][0]['ltp'])
        current_price_list.append(symbol_price)  
    except Exception as e:
        msg = "Exception occurred while selecting stocks : "
        exception_logs(msg, e)


# --------------Getting Required Margin-----------------------------
order_info = []          # This section will be used in future to calculate the quantity of the stocks
for i in range(len(instrument_token_list)):    # based on the leverage provided in the stock
    order_info.append( 
        {"instrument_token": instrument_token_list[i], "quantity": 1, "price": current_price_list[i], "amount": 0,
         "trigger_price": 0}
        )
    
margin_required_list = []
margin_required = client.margin_required(transaction_type="BUY", order_info=order_info)
for i in range(len(instrument_token_list)):
    margin_required_list.append(margin_required['Success'][i]['normal'])

# ----------------Calculating quantity------------------------------
cash_balance = cr.user_details["cash_used_per_stock"]
quantity_list = [math.floor(cash_balance/margin_required_list[i]) for i in range(len(margin_required_list))]
print(quantity_list)
# -------------------Placing the orders---------------------------
counter = len(instrument_token_list)
flag = 1
while flag == 1:
    now = datetime.now()
    my_time_string = "09:15:00"   # Trades will execute at exactly 9:15 AM when the Stock Market opens
    my_datetime = datetime.strptime(my_time_string, "%H:%M:%S")
    print("Date Time: ", my_datetime)
    my_datetime = now.replace(hour=my_datetime.time().hour, minute=my_datetime.time().minute,
                              second=my_datetime.time().second, microsecond=0)
    if now >= my_datetime:
        msg = "Time of Execution: "
        exception_logs(msg, now)
        for i in range(len(instrument_token_list)):# Loop that places the buy orders for both the stocks
            inst_tok = instrument_token_list[i]
            try:
                placed_order_details = client.place_order(order_type="MIS", instrument_token=inst_tok, transaction_type="BUY",
                               quantity=quantity_list[i], price=0, disclosed_quantity=0, validity="GFD", variety="REGULAR")  # REGULAR
                time.sleep(1)
                msg = "Placed Order Details: "
                exception_logs(msg, placed_order_details)
            except Exception as e:
                counter -= 1
                msg = "Exception occurred in placing order and the exception is :"
                exception_logs(msg, e)
        
        # ----------------Placing the TP/SL orders-----------------------------
        time.sleep(2)
        order_details = client.positions(position_type="TODAYS")
        exception_logs("Positions Details--->> ", order_details)
        for i in range(counter):    
            exec_price = round(order_details['Success'][i]['buyTrdAvg'], 2)
            instrumentToken = order_details['Success'][i]['instrumentToken']
            index_instrumentToken = instrument_token_list.index(instrumentToken)
            quantity = quantity_list[index_instrumentToken] #order_details['Success'][i]['buyTradedQtyLot']
            stock_name = symbol_name[index_instrumentToken]
            msg = "Stock Nanme, Execution Price, InsToken, Index of the insToken, Quantity -> "
            p = stock_name + " " + str(exec_price)+" "+str(instrumentToken)+" "+str(index_instrumentToken)+" "+str(quantity)
            exception_logs(msg, p)
            
            number = round(exec_price + (exec_price * .0075), 2)  # Setting Take Profit at 0.75%
            decimal = (round((number - math.floor(number)), 2)*100)/10
            decimal2 = round(((decimal - math.floor(decimal))/10), 2)
            take_profit = round((number - decimal2), 2)
            
            number = round(exec_price - (exec_price * .0025), 2)  # Setting Stop Loss at 0.25%
            decimal = (round((number - math.floor(number)), 2)*100)/10
            decimal2 = round(((decimal - math.floor(decimal))/10), 2)
            stop_loss = round((number - decimal2), 2)

            msg = "Take Profit and Stop Loss for "+symbol_name[index_instrumentToken] + " : "
            p = str(take_profit)+" "+str(stop_loss)
            exception_logs(msg, p)
                
            try:
                take_profit_order = client.place_order(order_type="MIS", instrument_token=instrumentToken, transaction_type="SELL",
                           quantity=quantity, price=take_profit, trigger_price=0, disclosed_quantity=0,
                           validity="GFD", variety="REGULAR")  # Placing the Take profit Order
                
            except Exception as e:
                cancel_order(instrumentToken, quantity)
                # In case Take profit order fails, we will exit the stock immediately
#
                msg = "Exception occurred while placing Take Profit order and the exception is "
                exception_logs(msg, e)
                    
            time.sleep(1)
            
            try:
                stop_loss_order = client.place_order(order_type="MIS", instrument_token=instrumentToken, transaction_type="SELL",
                           quantity=quantity, price=0, trigger_price=stop_loss, disclosed_quantity=0,
                           validity="GFD", variety="REGULAR")  # Placing the Stop Loss Order
                
            except Exception as e:
                cancel_order(instrumentToken, quantity)
                # In case Stop Loss order fails, we will exit the stock immediately

                msg = "Exception occurred while placing Stop Loss order and the exception is "
                exception_logs(msg, e)
                    
            time.sleep(1)
    if now >= my_datetime:
        flag = 0  # will break because of time check when time is less
    time.sleep(1)
while len(symbol_name) > 0:
    order_report = client.order_report()
    time.sleep(1)
    orders_df = pd.DataFrame()
    for key, values in order_report["success"][0].items():
        orders_df[key] = [order_report["success"][i][key] for i in range(len(order_report["success"]))]
    remove_list = []
    # orders_df.to_csv("C:/Users/Documents/GitHub/kotak_sec_stock_scalper/orders_df.csv", mode='a')
    for i in range(len(symbol_name)):
        temp_df = orders_df[orders_df["instrumentName"] == symbol_name[i]]
        # temp_df.to_csv("C:/Users/Documents/GitHub/kotak_sec_stock_scalper/temp_df.csv", mode='a')
        quant = quantity_list[i]
        print(symbol_name[i],"Selected Quantity from list->", quant,temp_df["filledQuantity"])
        if list(temp_df["filledQuantity"]) in [[quant, quant, 0], [quant, 0, quant],[0, quant, quant]]:
            a = int(temp_df["orderId"].where(temp_df["filledQuantity"] == 0).dropna().iloc[0])
            print(a)
            client.cancel_order(order_id=a)
            orders_df.drop(orders_df[orders_df["instrumentName"] == symbol_name[i]].index, inplace=True)
            remove_list.append(symbol_name[i])
            msg = "Extra Order Cancelled for "+ symbol_name[i]+" with orderid "
            exception_logs(msg, a)

        else:
            print("TP/SL is not filled")
    if len(remove_list) > 0:
        for i in remove_list:
            index = symbol_name.index(i)
            symbol_name.remove(i)
            quantity_list.pop(index)
    print("Remove_list --> ", remove_list)
    time.sleep(1)
print(client.logout())  # Logout the session created through  Kotak API
