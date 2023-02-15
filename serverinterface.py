from mcstatus import JavaServer
import base64

ip = "45.87.173.241:25565"
server = JavaServer.lookup(ip)

class Server:
    def serverStatus():
        status = server.status()

        onlineplayers = ""
        if status.players.sample != None:
            for i in status.players.sample:
                onlineplayers += i.name + "\n"
                print(i.name)
        return (f"**{ip}**\n{status.description}\nOyuncu sayısı: {status.players.online}\nGecikme: {status.latency.__trunc__()} ms\nVersiyon: {status.version.name}\n\nOnline oyuncular:\n{onlineplayers}")
    
    def onlinePlayers():
        status = server.status()
        onlineplayers = []
        if status.players.sample != None:
            for i in status.players.sample:
                onlineplayers.append(i.name)
        return onlineplayers

    def serverIcon():
        status = server.status()
        if status.favicon == None:
            return ""
        icon = base64.b64decode(status.favicon.split(',')[1])
        #print(icon)

        if icon != "":
            img_file = open('image.png', 'wb')
            img_file.write(icon)
            img_file.close()

        return "image.png"

if __name__ == "__main__":
    print(Server.serverStatus())
