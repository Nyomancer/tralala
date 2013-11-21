#!/bin/python2

from twisted.words.protocols import irc
from twisted.internet import protocol
from datetime import datetime
import time
import os
import random
import sys
from twisted.internet import reactor

#for backlog
import collections

#central configuration class
class ConfigClass:
    
    def __init__(self):
        #modify as needed
        self.nick = "TralalaBot"
        self.owner = "owner"
        self.adminpw = "supersecretpassword"
        self.server = "irc.freenode.net"
        self.port = 6666
        self.channel = "#tralalabot"
    
    #no getter-methods here. lets see how that works out...
    #TODO: properties... how do they work?

#simple logging class
class LoggerClass:

    def __init__(self):
        #open logfiles here...
        self.logfile = open("tralala.log", 'a')
        self.logfile.write("[STD]: " + datetime.strftime(datetime.now(), "%d.%m.%y - %H:%M:%S:%f: ") + "start logging\n")
        self.logfile.flush()
        os.fsync(self.logfile.fileno())
    
    def logStd(self, message):
        #pipe standard-type message to logfile
        self.logfile.write("[STD]: " + datetime.strftime(datetime.now(), "%d.%m.%y - %H:%M:%S:%f: ") + message + "\n")
        #yeah... i know...
        self.logfile.flush()
        os.fsync(self.logfile.fileno())
   
    def logErr(self, message):
        #pipe error-type message to logfile
        self.logfile.write("[ERR]: " +  datetime.strftime(datetime.now(), "%d.%m.%y - %H:%M:%S:%f: ") + message + "\n")
        self.logfile.flush()
        os.fsync(self.logfile.fileno())


#revolver class used in russian roulette
class Revolver:
    def __init__(self):
        self.reload()

    def reload(self):
        self.bullet = random.randint(1,6)
        self.chamber = 1
        return "Can't you see I'm reloading?"

    def shoot(self, user):
        #empty chamber
        if (self.chamber >= 5) and (self.chamber != self.bullet):
            textOut = "%s: Chamber %s of 6: *click*\nReloading" % (user, self.chamber)
            self.reload()
            
        #you "found" the bullet
        elif (self.chamber == self.bullet):
            textOut = "%s: Chamber %s of 6: BOOM\nReloading" % (user, self.chamber)
            self.reload()

        #bullet in last chamber, restart game
        else:
            textOut = "%s: Chamber %s of 6: *click*" % (user, self.chamber)
            self.chamber += 1

        return textOut


class TralalaBot(irc.IRCClient):
    
    #CTCP VERSION request details
    versionName = "TralalaBot"
    versionNum = "0.2.5"
    
    #gets nick from factory
    def _get_nickname(self):
        return self.factory.nickname
    
    #set _ALL_ the names
    nickname = property(_get_nickname)
    realname = nickname
    username = nickname

    #set backlog options
    backlogLength = 30
    backlog = collections.deque([], backlogLength)

    #processes triggers
    def processTrigger(self, user, channel, message):
        if message == "!version":
            self.msg(channel, "%s %s" % (self.versionName, self.versionNum,))


        elif message == "!info":
            self.msg(channel, "%s %s\nGet your copy at: github.com/nyomancer/tralala\nWritten by nyo@nyo-node.net" % (self.versionName, self.versionNum,))

        elif message == "!last":
            for x in self.backlog:
                self.msg(user.split('!')[0], x)
                time.sleep(0.5)

        elif message == "!reload":
            self.msg(channel, "%s" % (revolver.reload()))

        elif message == "!shoot":
            self.msg(channel, "%s" % (revolver.shoot(user.split('!')[0])))

    #append to backlog - legacy
    #TODO: make this work and make this pretty
    def appendBacklog(self, message):
        self.backlog.append(message)

    
    #called after sucessfully signing on to the server.
    def signedOn(self):
        self.join(self.factory.channel)
        logMsg = "Signed on as %s" % (self.nickname,)
        logger.logStd(logMsg)

    #called when I finish joining a channel
    def joined(self, channel):
        logMsg = "Joined %s" % (channel,)
        logger.logStd(logMsg)
         
    #called when I have a message from a user to me or a channel
    def privmsg(self, user, channel, msg):

        #append "user: message" to backlog
        if channel == conf.channel:
            self.backlog.append("%s: %s" % (user.split('!')[0], msg))


        #grants channelop to owner after sending the right "password" via query
        if (user.split('!')[0] == conf.owner) and (channel == self.nickname) and (msg == conf.adminpw):
            logMsg = "%s %s requested OP: granted" % ((user.split('!')[0]), channel,)
            logger.logStd(logMsg)
            self.mode(self.factory.channel, True, "o", None, conf.owner)
        
        #trigger hook
        elif (msg[0] == "!"):
            self.processTrigger(user, channel, msg)

class TralalaBotFactory(protocol.ClientFactory):
    protocol = TralalaBot

    def __init__(self, channel, nickname='TralalaTest'):
        self.channel = channel
        self.nickname = nickname


    def clientConnectionLost(self, connector, reason):
        logMsg = "Lost connection (%s), reconnecting." % (reason,)
        logger.logErr(logMsg)
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        logMsg = "Could not connect: %s" % (reason,)
        logger.logErr(logMsg)




if __name__ == "__main__":
        conf = ConfigClass()
        logger = LoggerClass()
        revolver = Revolver()
        reactor.connectTCP(conf.server, conf.port, TralalaBotFactory(conf.channel, conf.nick))
        reactor.run()
