#!/bin/python2

from twisted.words.protocols import irc
from twisted.internet import protocol




class TralalaBot(irc.IRCClient):
    def _get_nickname(self):
        return self.factory.nickname
    
    nickname = property(_get_nickname)
    
    def signedOn(self):
        self.join(self.factory.channel)
        print "Signed on as %s." % (self.nickname,)

    def joined(self, channel):
        print "Joined %s." % (channel,)

    def privmsg(self, user, channel, msg):
        print "%s: %s" % (user, msg,)
        if msg == "teststring123":
             self.msg(channel, "teststring456")


class TralalaBotFactory(protocol.ClientFactory):
    protocol = TralalaBot

    def __init__(self, channel, nickname='TralalaTest'):
        self.channel = channel
        self.nickname = nickname


    def clientConnectionLost(self, connector, reason):
        print "Lost connection (%s), reconnecting." % (reason,)
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print "Could not connect: %s" % (reason,)



###main loop

import sys
from twisted.internet import reactor

if __name__ == "__main__":
        chan = sys.argv[1]
        reactor.connectTCP('irc.freenode.net', 6667, TralalaBotFactory('#' + chan))
        reactor.run()
