from telethon import TelegramClient, events
import asyncio
async def login():
    api_id = 28134961
    api_hash = '81bb5d269eab1d7604e469d1a5bf5a03'

    # Use your own API_ID and API_HASH from https://my.telegram.org/apps
    client = TelegramClient('WealthSaga', api_id, api_hash)

    # Connect to Telegram
    await client.start()

    # Get the entity of the group you want to save messages from
    group_entity = await client.get_entity("testchannel_162")
    # -1001238734576


    # Handle new messages in the group
    # "(?i)" makes it case-insensitive, and | separates "options"
    @client.on(events.NewMessage(chats=group_entity))
    async def my_event_handler(event):
        # Save the message text to a file
        msg = event.raw_text
        splitted = msg.split(sep=",")
        first_stock_name = splitted[0]
        first_threshold = splitted[1]
        second_stock_name = splitted[2]
        second_threshold = splitted[3]

        with open('StockNames.txt', 'w') as file:
            file.write(first_stock_name + "," + first_threshold + "," + second_stock_name + "," + second_threshold)

    # Start listening for new messages
    # client.add_event_handler(my_event_handler)
    try:
        print('(Press Ctrl+C to stop this)')
        await client.run_until_disconnected()
    finally:
        client.disconnect()

loop = asyncio.get_event_loop()
loop.run_until_complete(login())
