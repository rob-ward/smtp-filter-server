#! /usr/bin/env python

# Copyright (c) 2013, Rob Ward
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without 
# modification, are permitted provided that the following conditions are met:
#
#    Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#
#      Redistributions in binary form must reproduce the above copyright 
#    notice, this list of conditions and the following disclaimer in
#      the documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE 
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF
# THE POSSIBILITY OF SUCH DAMAGE.


# smtp-filter-server -- Is a small simple smtp server that can filter messages
# based on a set of rules prior to sending.
#
# This tool is not designed to be a large scale smtp server, it is designed to 
# be used as a local smtp server for other tools where filtering there output
# is required.
#
# 
# Please report any bugs to or feature requests to;
#             https://github.com/rob-ward/smtp-filter-server
#



import smtpd
import asyncore
import smtplib
import ConfigParser
import os.path
import email.utils
from email.mime.text import MIMEText
import random
import logging 

class FilterSMTPServer(smtpd.SMTPServer):

    serveruri = ""
    port = ""
    forcessl = False
    auth = False
    username = ""
    password = ""
    

    def printinfo(self):
        print self.serveruri
        print self.port
        print self.forcessl
        print self.auth
        print self.username
        print self.password
        
        
    def process_message(self, peer, mailfrom, rcpttos, data):
        logging.info( 'Message addressed from:' + mailfrom)
        logging.info( 'Message length        :' + str(len(data)))
        logging.info("Message:\n" + data)        
        
        
        if self.forcessl == "True":
            logging.info("Forcessl is on")
            server = smtplib.SMTP_SSL(self.serveruri, self.port)
        else:
            logging.info("Forcessl is not on")
            server = smtplib.SMTP(self.serveruri, self.port)
        
        try:
            server.set_debuglevel(True)

            # identify ourselves, prompting server for supported features
            server.ehlo()
            if self.forcessl != "True":

                if server.has_extn('STARTTLS'):
                    logging.info("Said Hello over STARTTLS");
                    server.starttls()
                    server.ehlo()
            
            if self.auth == "True":
                server.login(self.username, self.password )
                logging.info("Logged in")
            
            logging.info("Sending....");
            server.sendmail(mailfrom, rcpttos, data)
        except:
           logging.info("FAIL????:");
            
        return


####################


def main():
    logging.info("entering")
    logging.info("os.getcwd() = " + os.getcwd())
	
    config_path = os.path.expanduser('~/.smtp-filter-config')

    config = ConfigParser.RawConfigParser()
    config.read(config_path)

    server = FilterSMTPServer(('127.0.0.1', 1025), None)

    try:
        server.serveruri = config.get("SERVER", 'uri')
        server.port = config.get("SERVER", 'port')
        server.forcessl = config.get("SERVER", 'forcessl')
        server.auth = config.get("SERVER", 'auth')
        server.username = config.get("SERVER", 'username')
        server.password = config.get("SERVER", 'password')
    except ConfigParser.NoSectionError:
        print "It appears that there is no server section defined in the config file, please create" + \
              "\na config file  ~/.smtp-filter-config see docs for more info"
    except ConfigParser.NoOptionError:
        print "It appears that you config file is missing some fields, please RTFM!"
    
    server.printinfo()

    asyncore.loop()

#################


if __name__ == "__main__":
	rnum = random.randint(100000, 999999)
	logging.basicConfig(format="%(asctime)s: - " + str(rnum) + " - %(filename)s: -  %(funcName)s() - %(lineno)d : %(message)s", level=logging.DEBUG, filename='/tmp/smtp-filter-server.log')
	main()
