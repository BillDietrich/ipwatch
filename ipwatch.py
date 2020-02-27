#!/usr/bin/env python3

#--------------------------------------------------------------------------------------------------
# ipwatch.py        Reports when your system's public IP address changes
#                   https://github.com/BillDietrich/ipwatch

# If this is going to run at boot-time, put this file in the root filesystem
# (maybe in /usr/local/bin) instead of under /home, because /home may not
# be mounted or decrypted when the service starts.

# on Linux, to see if app is running in background:
#   sudo ps -ax | grep ipwatch

# Copyright Bill Dietrich 2020


#--------------------------------------------------------------------------------------------------

import subprocess
import sys
import signal       # https://docs.python.org/3/library/signal.html
import time         # https://www.cyberciti.biz/faq/howto-get-current-date-time-in-python/
import requests
import syslog       # https://docs.python.org/2/library/syslog.html

#import dns.resolver    # un-comment this if you want gsAccessType = 'DNS'
# and do "apt install python-dnspython" or "pip3 install dnspython"
#
# And to run this script with DNS and as a service, you must do "sudo -H pip3 install dnspython"
# so this package gets installed for root user too.


#--------------------------------------------------------------------------------------------------

# edit these to change the behavior of the app

gsAccessType = 'HTTP'         # HTTP or DNS

gsUIChoice = 'notification'         # one or more of: notification syslog stdout

# If VPN is down and we're leaking, IP address will start with this.
# In that case, poll a little faster.
# Put nonsense value such as 'zzz.' to disable this.
gsIPAddressStartNoVPN = 'zzz.' 


#--------------------------------------------------------------------------------------------------

# state variables

gsConnectionState = 'none'    # none or 'rejected by site' or connected

gsOldIPAddress = 'start'    # start or 'internal error' or 'no network connection' or connected'

gnSleep = 0


# getting extremely precise timestamps:
# https://stackoverflow.com/questions/38319606/how-to-get-millisecond-and-microsecond-resolution-timestamps-in-python
# time.time()  is microseconds but not necessarily accurate ?
# https://stackoverflow.com/questions/5998245/get-current-time-in-milliseconds-in-python


#--------------------------------------------------------------------------------------------------

# command using DNS: dig +short myip.opendns.com @resolver1.opendns.com
# https://stackoverflow.com/questions/2805231/how-can-i-do-dns-lookups-in-python-including-referring-to-etc-hosts
# https://stackoverflow.com/questions/3898363/set-specific-dns-server-using-dns-resolver-pythondns
# http://www.dnspython.org/
# http://www.dnspython.org/examples.html
# https://0xbharath.github.io/python-network-programming/protocols/dns/index.html

def GetIPAddressViaDNS():

    global gsConnectionState
    global gnSleep

    objResolver = dns.resolver.Resolver(configure=False)

    # resolver1.opendns.com == 208.67.222.222
    objResolver.nameservers = [ '208.67.222.222' ]

    sIPAddress = 'internal error'
    gnSleep = 1
    try:
        objResolverAnswer = objResolver.query('myip.opendns.com', 'A')
        #print(objResolverAnswer)
        #for i in objResolverAnswer.response.answer:
        #    for j in i.items:
        #        print(j.to_text())
        if len(objResolverAnswer.response.answer) < 1:
            print('Nameserver gave no answer')
            sIPAddress = 'connected'
            gsConnectionState = 'rejected by site'
            gnSleep = 60
        else:
            sIPAddress = str(objResolverAnswer.response.answer[0].items[0])
            gsConnectionState = 'connected'
            if sIPAddress.startswith(gsIPAddressStartNoVPN):
                gnSleep = 60
            else
                gnSleep = 120
    except exception as objE:
        print('exception "'+str(objE)+'"')
        sIPAddress = 'no network connection'
        gsConnectionState = 'none'
        gnSleep = 1
    finally:
        #print('sIPAddress "'+sIPAddress+'"')
        return sIPAddress


#--------------------------------------------------------------------------------------------------

def GetIPAddressViaHTTP():

    global gsConnectionState
    global gnSleep

    arrsSites = [                   # first item index == 0
        'http://ifconfig.me/ip',    # asks that you rate-limit to 1/minute
        'http://ifconfig.co/ip',    # asks that you rate-limit to 1/minute
        'http://ifconfig.io/ip',    # asks that you rate-limit to 1/minute
        'http://ipecho.net/plain',
        'http://icanhazip.com',
        'http://bot.whatismyipaddress.com',
        'https://diagnostic.opendns.com/myip',
        'http://checkip.amazonaws.com/',
        'http://whatismyip.akamai.com',
        'https://api.ipify.org',
        'https://ip.42.pl/short',
        'http://ipinfo.io/ip',
        #'http://ipaddr.pub/ip',     # rejects with 406
        'http://ident.me'
    ]

    sIPAddress = 'internal error'
    gnSleep = 1
    try:
        # some services (ifconfig) ask that you rate-limit to 1/minute
        sSite = arrsSites[0]
        # objRequest = requests.get(sSite, { 'User-Agent': 'Mozilla/5.0' })
        objRequest = requests.get(sSite)
        # print('headers "%s"' % objRequest.headers)
        if objRequest.status_code > 200:
            print('Site '+sSite+' gave HTTP status'+str(objRequest.status_code)+' content "'+objRequest.content.decode('ascii')+'"')
            sIPAddress = 'connected'
            gsConnectionState = 'rejected by site'
            gnSleep = 60
        else:
            sIPAddress = objRequest.content.decode('ascii').strip()
            gsConnectionState = 'connected'
            if sIPAddress.startswith(gsIPAddressStartNoVPN):
                gnSleep = 60
            else
                gnSleep = 120
    except requests.exceptions.RequestException as objE:
        # print('request exception "'+str(objE)+'"')
        sIPAddress = 'no network connection'
        gsConnectionState = 'none'
        gnSleep = 1
    except exception as objE:
        print('exception "'+str(objE)+'"')
        gnSleep = 60
    finally:
        # print('sIPAddress "'+sIPAddress+'"')
        return sIPAddress


#--------------------------------------------------------------------------------------------------

def GetAddress():

    global gsConnectionState
    global gsUIChoice
    global gsOldIPAddress

    if gsAccessType == 'HTTP':
        sNewIPAddress = GetIPAddressViaHTTP()
    else:
        sNewIPAddress = GetIPAddressViaDNS()

    if gsOldIPAddress == sNewIPAddress:
        return

    sMsg = ('Public IP address changed from "'+gsOldIPAddress+'" to "'+sNewIPAddress+'"')
    gsOldIPAddress = sNewIPAddress

    if 'stdout' in gsUIChoice:
        print(time.strftime("%H:%M:%S")+': '+sMsg)
    if 'notification' in gsUIChoice:
        # open a modal dialog, so no more checking until user sees the dialog and closes it
        #    subprocess.call(['zenity','--info','--text',sMsg])
        # add a (non-modal) notification in the system tray, so no wait for user action
        subprocess.call(['zenity','--notification','--text',sMsg])
        # on Linux, see output as notifications in system tray
    if 'syslog' in gsUIChoice:
        syslog.syslog(sMsg)
        # on Linux, see output:
        #   sudo journalctl --pager-end
        # or
        #   sudo journalctl | grep ipwatch


#--------------------------------------------------------------------------------------------------
# Not sure why this is needed, but it is, otherwise signal will make process exit.
# And sometimes this is not called, even though the signal came in to the main loop.

def handler(signum, frame):
    #print('Signal handler called with signal', signum)
    return


#--------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    #if argv is None:
    #    argv = sys.argv
    #if len(argv) < 2:
    #    monitor_frequency = 3600
    #else:
    #    monitor_frequency = argv[1]

    # Not sure why this is needed, but it is, otherwise signal will make process exit.
    signal.signal(signal.SIGUSR1, handler)

    while True:

        GetAddress()

        try:
            #print('sleep for '+str(gnSleep))
            # SIGUSR1 == 10 in major archs
            # pkill --signal SIGUSR1 -f ipwatch.py
            objSignal = signal.sigtimedwait({signal.SIGUSR1}, gnSleep)
            #if objSignal == None:
                #print('sleep timed out')
            #else:
                #print('received signal '+str(objSignal.si_signo))
        except KeyboardInterrupt:
            sys.exit()
        #except InterruptedError as objE:
            #print('sigtimedwait exception "'+str(objE)+'"')


#--------------------------------------------------------------------------------------------------