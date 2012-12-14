#!/usr/bin/python

"""
Asynchrone Python IRC Bot

Author: Timo Schrappe
CC BY-NC-SA 
http://creativecommons.org/licenses/by-nc-sa/3.0/
"""

"""
TODO:

* "Check" message in Webinterface -> print "check" to IRC and starts counting in Webinterface
* Each Question can be marked with timestamp. It should disappear after it is marked as "answered" 
* Pseudo BNF Message parse http://tools.ietf.org/html/rfc1459.html#section-2.3.1

"""
import sys,asyncore,socket,re,time

import cProfile

class PyBot(asyncore.dispatcher):    
        
    def __init__(self, host, nickname, channel, password='', port=6667):
        self.host = host
        self.port = port
        self.nickname = nickname
        self.channel = channel
        self.password = password

        # Creates an asynchronous socket
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect((self.host,self.port))
        print 'Processing...'
        print 
        
    def handle_connect(self):
        # http://tools.ietf.org/html/rfc2812#section-3.1.1
        # Command: PASS
        # Parameters: <password>
        if self.password:
            print 'Password sent'
            self.send('PASS %s\r\n' % self.password)

        # http://tools.ietf.org/html/rfc2812#section-3.1.2
        # Command: NICK
        # Parameters: <nickname>
        self.send('NICK %s\r\n' % self.nickname)

        # http://tools.ietf.org/html/rfc2812#section-3.1.3
        # Command: USER
        # Parameters: <user> <mode> <unused> <realname>
        # Bit 3 = +i
        # Bit 2 = +w
        self.send('USER %s 12 * :IRC %s\r\n'% (self.nickname, 'pyree.de by Timo Schrappe'))


    def convertIRCMessage(self, s):
        prefix = ''
        trailing = []
        if not s:
            pass
        if s[0] == ':' and ' ' in s:
                prefix, s = s[1:].split(' ', 1)
        if s.find(' :') != -1:
            s, trailing = s.split(' :', 1)
            args = s.split()
            args.append(trailing)
        else:
            args = s.split()
        if len(args) > 0:
            command = args.pop(0)
        else:
            command = ''
        return prefix, command, args


    def parseIRCCommand(self, cmd, prefix, args):
        if cmd == '001':
            print 'pyree is now connected to %s ' % self.host
            print 'he is now listening on questions'
            print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
            print
            self.send('JOIN %s\r\n' % self.channel)
        elif cmd == 'PRIVMSG' and args[0] == self.channel and (args[1].startswith('Q:') or args[1].startswith('q:')):
            question = args[1][2:].strip()
            nick = prefix.split('@')[0].split('!')[0]
            print "%s: %s" % (nick, question)
            # Here code for your printer ;-)
            # http://pyserial.sourceforge.net/pyserial_api.html
        elif cmd == '221':
            print prefix, args


    def handle_read(self):
        s = self.recv(512)
        if '\r\n' in s:
            lines = s.splitlines()
            if len(lines) is 1:
                prefix, command, args = self.convertIRCMessage(lines[0])
                if command == 'PING':
                    self.send('PONG %s\r\n' % args[0])
                else:
                    self.parseIRCCommand(command, prefix, args)
            else:
                for line in lines:
                    prefix, command, args = self.convertIRCMessage(line)
                    if command == 'PING':
                        self.send('PONG %s\r\n' % args[0])
                    else:
                        self.parseIRCCommand(command, prefix, args)


    def handle_error(self):
        print 'Error handled'
        self.close()

    def handle_close(self):
        self.close()
        print 'Socket closed'
try:
    # PyBot(server, username, channel, password)
    pyBot = PyBot('c.ustream.tv', '', '#eevblog', '')
    asyncore.loop()
except KeyboardInterrupt, e:
    pyBot.close()
    print e

