import discord
import threading
import asyncio
import time
import datetime

import redditdownload
import serverinterface

stopFlag = False

commands = {
    'clear x' : 'x mesajı sil',
    'server status': 'sunucunun durumunu yazdır',
    'oylama (zaman saniye) (konu) (seçenek 1) (seçenek 2)....' : 'oylama başlat',
    'reddit top (subreddit) (zaman [all, day, hour, month, week, year])' : 'subreddit ve zaman aralığından en iyi postu göster',
    'reddit random (subreddit)': 'subredditten rastege bir post göster',
    'trade add (al_sayı) (al_isim) (ver_sayı) (ver_isim)': 'yeni bir trade ekle',
    'trade list': 'tradeleri listele',
    'trade remove (numara)': 'belirtilen numaralı tradeyi sil'
}

class Trade:
    al_amnt:int
    ver_amnt:int
    al_name:str
    ver_name:str
    author:str

tradeList = []

emojiNumMap = ["0️⃣", "1️⃣","2️⃣","3️⃣","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣","🔟"]

async def oylamaEnd(message : discord.Message, tovote, subject):
    reactions = {}
    for reaction in message.reactions:
        reactions[reaction.emoji] = reaction.count
    print(reactions)

    answer = f"Oylama bitti.\n`Konu: {subject}`\n"
    index = 0
    for key, value in reactions.items():
        answer += f"`{tovote[index]}: {value - 1}`\n"
        index += 1
    await message.channel.send(answer)

async def classifyCommand(bot: discord.Client, message : discord.message):
    content = str(message.content)[1:].strip()

    args = content.split(' ')
    args[0] = args[0].lower()
    
    if args[0] == 'help':
        response = ''
        for key, value in commands.items():
            response += "**`!" + key + "`**: " + value + '\n'
        await message.channel.send(response)

    if args[0] == 'clear':
        if(len(args) == 1):
            messagesToDelete = []
            async for x in message.channel.history():
                messagesToDelete.append(x)
            await message.channel.delete_messages(messagesToDelete)
            await message.channel.send("Deleted `" + str(len(messagesToDelete)) + "` messages")
        if args[1] != None:
            toClear = int(args[1]) + 1
            messagesToDelete = []
            async for x in message.channel.history(limit=toClear):
                messagesToDelete.append(x)
            await message.channel.delete_messages(messagesToDelete)
            await message.channel.send("Deleted `" + str(len(messagesToDelete)) + "` messages")
    
    if args[0] == 'reddit':
        post = redditdownload.RedditPost()
        try:
            if args[1] == "top":
                sub = args[2]
                time = args[3]
                post: redditdownload.RedditPost = redditdownload.RedditDownload.getTop(sub, time)
            elif args[1] == "random":
                sub = args[2]
                post: redditdownload.RedditPost = redditdownload.RedditDownload.getRandom(sub)
            if(post.submission.is_self):
                await message.channel.send(f"**`{post.submission.title}`**\n`{post.submission.score} Upvotes`\n{post.submission.url}")
            else:
                await message.channel.send(f"**`{post.submission.title}`**\n`{post.submission.score} Upvotes`\nhttps://www.reddit.com{post.submission.permalink}\n{post.submission.url}")
        except:
            await message.channel.send(f"`({message.content})` komudunda bir hata oluştu. **!help**")
        
    if args[0] == 'oylama':
        subject = args[2]
        tovote = []
        tovotestr = ""
        for i in range(3, len(args)):
            tovote.append(args[i])
        for i in range(len(tovote)):
            tovotestr += emojiNumMap[i] + ": " + tovote[i] + "\n"
        message = await message.channel.send("Oylama **`" + subject + "`**:\n" + tovotestr)
        msg = discord.utils.get(bot.cached_messages, id=message.id)
        for i in range(len(tovote)):
            print(emojiNumMap[i])
            await msg.add_reaction(emojiNumMap[i])
        await asyncio.sleep(int(args[1]))
        await oylamaEnd(discord.utils.get(bot.cached_messages, id=message.id), tovote, subject)
    if args[0] == 'server':
        if args[1] == 'status':
            status = serverinterface.Server.serverStatus()

            if serverinterface.Server.serverIcon() == "":
                await message.channel.send(status)
            else:
                image = discord.File(serverinterface.Server.serverIcon())
                await message.channel.send(status, file=image)
    
    if args[0] == 'trade':
        if args[1] == "add":
            al_amnt = args[2]
            al_name = args[3]
            ver_amnt = args[4]
            ver_name = args[5]

            trade = Trade()
            trade.al_amnt = al_amnt
            trade.ver_amnt = ver_amnt
            trade.al_name = al_name
            trade.ver_name = ver_name
            trade.author = message.author.name

            tradeList.append(trade)
        if args[1] == "list":
            ret = ""

            i = 0
            for trade in tradeList:
                ret += f"`{i}` {trade.author}: {trade.al_amnt} {trade.al_name} - {trade.ver_amnt} {trade.ver_name}\n"
                i += 1
            await message.channel.send(ret)
        if args[1] == "remove":
            index = int(args[2])
            tradeList.remove(tradeList[index])
            await message.channel.send("Trade removed")

    print("Command ", content + " from " , message.author)

class MinecraftBot(discord.Client):
    async def botMsgChannel(self):
        for guild in self.guilds:
            return discord.utils.get(guild.channels, name="minecraft-bot-msg")

    async def mc_online_checker(self):
        global stopFlag
        online_players_old = []
        online_players = []
        while (True) :
            try:
                online_players_old = serverinterface.Server.onlinePlayers()
                online_players = online_players_old
                break
            except:
                print("mc_online_checker onlinePlayers() error")
                time.sleep(2)
        botch = await self.botMsgChannel()
        await botch.send("Online oyuncular: " + online_players.__str__())
        while (True):
            while (True) :
                try:
                    online_players_old = online_players
                    online_players = serverinterface.Server.onlinePlayers()
                    break
                except:
                    print("mc_online_checker onlinePlayers() error")
                    time.sleep(2)
            joined = []
            left = []
            for i in online_players:
                if i not in online_players_old:
                    joined.append(i)
            for i in online_players_old:
                if i not in online_players:
                    left.append(i)

            for guild in self.guilds:
                channel = discord.utils.get(guild.channels, name="minecraft-bot-msg")
                for i in joined:
                    await channel.send(datetime.datetime.now().strftime("%H:%M:%S") + " - " + i + " katıldı")
                for i in left:
                    await channel.send(datetime.datetime.now().strftime("%H:%M:%S") + " - " + i + " ayrıldı")
            await asyncio.sleep(0.5)
            if stopFlag:
                break

    def print_logged_in(self):
        global stopFlag
        while(True):
            for guild in self.guilds:
                for user in guild.members:
                    if user.status != discord.Status.offline and user.bot == False:
                        print(user.name + " is online")
            print("-----------------")
            time.sleep(10)

            if stopFlag:
                break

    async def on_ready(self):
        print(f'Logged on as {self.user}!')
        botch = await self.botMsgChannel()
        await botch.send(datetime.datetime.now().strftime("%H:%M:%S") + " - " + "Bot started")

        asyncio.create_task(self.mc_online_checker())

    async def on_reaction_add(self, reaction, user):
        print(reaction.message.content)
        if str(reaction.message.content).startswith("Oylama"):
            if user.name != "MinecraftBot":
                await reaction.message.channel.send(user.name + " " + reaction.emoji + " ile oyladı")

    async def on_message(self, message):
        print(f'Message from {message.author}: {message.content}')
        if str(message.content).strip().startswith('!') and message.author != self.user:
            await classifyCommand(self, message)

    async def close(self):
        botch = await self.botMsgChannel()
        await botch.send(datetime.datetime.now().strftime("%H:%M:%S") + " - Bot closing")
        await discord.Client.close(self)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True

with open('trades.txt', 'r') as file:
    string = file.read()
    file.close()
    for line in string.split(';'):
        trade = Trade()
        line_spl = line.split(',')
        if(len(line_spl) < 5):
            continue
        trade.author = line_spl[0]
        trade.al_amnt = int(line_spl[1])
        trade.al_name = line_spl[2]
        trade.ver_amnt = int(line_spl[3])
        trade.ver_name = line_spl[4]
        tradeList.append(trade)

client = MinecraftBot(intents=intents)
loggedintimer = threading.Thread(target=client.print_logged_in)
loggedintimer.start()
client.run('MTA3MjkxMjg3MjQ0MDYwNjg2MQ.GsJJWi.b47jHKnlf9ST1WfoSM9Rl7-cqi0xij-V-BsegU')

print("Stopflag set")
stopFlag = True

file_str = ""
for trade in tradeList:
    file_str += f"{trade.author},{trade.al_amnt},{trade.al_name},{trade.ver_amnt},{trade.ver_name};"
with open("trades.txt", "w") as file:
    file.write(file_str)
    file.close()
