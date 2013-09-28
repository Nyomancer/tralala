#!/bin/python2

from twisted.words.protocols import irc
from twisted.internet import protocol
from datetime import datetime
import os

class LoggerClass:

    def __init__(self):
        #open logfiles here...
        self.logfile = open("tralala.log", 'w')
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


class TralalaBot(irc.IRCClient):
    
    #CTCP VERSION request details
    versionName = "TralalaBot"
    versionNum = "0.1.0"
    
    #gets nick from factory
    def _get_nickname(self):
        return self.factory.nickname
    
    #set _ALL_ the names
    nickname = property(_get_nickname)
    realname = nickname
    username = nickname

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

        #TODO: build a backlog feature

        #grants channelop to owner after sending the right "password" via query
        if (user.split('!')[0] == "chke") and (channel == self.nickname) and (msg == "opmefaggot"):
            logMsg = "%s %s requested OP: granted" % ((user.split('!')[0]), channel,)
            logger.logStd(logMsg)
            self.mode(self.factory.channel, True, "o", None, "chke")


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



import sys
from twisted.internet import reactor

if __name__ == "__main__":
        chan = sys.argv[1]
        logger = LoggerClass() #ffffuuuuuuu
        reactor.connectTCP('irc.freenode.net', 6667, TralalaBotFactory('#' + chan))
        reactor.run()
