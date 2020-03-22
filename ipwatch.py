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

# edit these to change the behavior of the app

gsAccessType = 'HTTP'         # HTTP or DNS

gsUIChoice = 'notification'   # one or more of: notification syslog stdout

# If VPN is down and we're leaking, IP address will start with this.
# In that case, poll a little faster.
# Put nonsense value such as 'zzz.' to disable this.
gsIPAddressStartNoVPN = 'zzz.' 


#--------------------------------------------------------------------------------------------------

#import subprocess
import sys
import platform
import time         # https://www.cyberciti.biz/faq/howto-get-current-date-time-in-python/
import requests
import ipaddress
import os           # https://docs.python.org/3/library/os.html
import socket

gbOSLinux = (platform.system() == "Linux")
gbOSWindows = (platform.system() == "Windows")

# for Linux:
if gbOSLinux:
    import syslog       # https://docs.python.org/2/library/syslog.html
    from plyer import notification      # https://plyer.readthedocs.io/en/latest/#
    # and do "pip3 install plyer"

# for Windows 10:
if gbOSWindows:
    import win32evtlogutil
    import win32evtlog
    # and do "pip install pywin32"
    from plyer import notification      # https://plyer.readthedocs.io/en/latest/#
    # and do "pip install plyer"

if gsAccessType == 'DNS':
    import dns.resolver
    # and do "apt install python-dnspython" or "pip3 install dnspython"
    #
    # And to run this script with DNS and as a service, you must do "sudo -H pip3 install dnspython"
    # so this package gets installed for root user too.


#--------------------------------------------------------------------------------------------------

# state variables

gsConnectionState = 'none'    # none or 'rejected by site' or connected

gsOldIPAddress = 'start'    # start or 'internal error' or 'no network connection' or connected'

gnSleep = 0

gnNextSiteIndex = 0


#--------------------------------------------------------------------------------------------------

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
            gnSleep = 120
        else:
            sIPAddress = str(objResolverAnswer.response.answer[0].items[0])
            gsConnectionState = 'connected'
            if sIPAddress.startswith(gsIPAddressStartNoVPN):
                gnSleep = 30
            else:
                gnSleep = 120
    except exception as objE:
        print('exception "'+str(objE)+'"')
        sIPAddress = 'no network connection'
        gsConnectionState = 'none'
        gnSleep = 1     # while accesses are not getting out at all, try frequently
    finally:
        #print('sIPAddress "'+sIPAddress+'"')
        return sIPAddress


#--------------------------------------------------------------------------------------------------

def GetIPAddressViaHTTP():

    global gsConnectionState
    global gnSleep
    global gnNextSiteIndex

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
        sSite = arrsSites[gnNextSiteIndex]
        gnNextSiteIndex = gnNextSiteIndex + 1
        if gnNextSiteIndex >= len(arrsSites):
            gnNextSiteIndex = 0
        # https://realpython.com/python-requests/
        # objRequest = requests.get(sSite, { 'User-Agent': 'Mozilla/5.0' })
        #print('do requests.get("'+sSite+'")')
        objRequest = requests.get(sSite, timeout=(1,1))     # 1 second to connect, 1 second to get data
        # print('headers "%s"' % objRequest.headers)
        if objRequest.status_code > 200:
            print('Site '+sSite+' gave HTTP status'+str(objRequest.status_code)+' content "'+objRequest.content.decode('ascii')+'"')
            sIPAddress = 'connected'
            gsConnectionState = 'rejected by site'
            gnSleep = 2
        else:
            sIPAddress = objRequest.content.decode('ascii').strip()
            gsConnectionState = 'connected'
            if sIPAddress.startswith(gsIPAddressStartNoVPN):
                gnSleep = 10
            else:
                gnSleep = 120
    except requests.exceptions.RequestException as objE:
        # print('request exception "'+str(objE)+'"')
        sIPAddress = 'no network connection'
        gsConnectionState = 'none'
        gnSleep = 1     # while accesses are not getting out at all, try frequently
    except exception as objE:
        print('exception "'+str(objE)+'"')
        gnSleep = 60
    finally:
        # print('sIPAddress "'+sIPAddress+'"')
        return sIPAddress


#--------------------------------------------------------------------------------------------------

def GetAddress():

    global gsAccessType

    if gsAccessType == 'HTTP':
        sNewIPAddress = GetIPAddressViaHTTP()
    else:
        sNewIPAddress = GetIPAddressViaDNS()

    return sNewIPAddress


#--------------------------------------------------------------------------------------------------

def ReportChange(sNewIPAddress):

    global gsConnectionState
    global gsUIChoice
    global gsOldIPAddress

    sMsg = ('Public IP address changed from "'+gsOldIPAddress+'" to "'+sNewIPAddress+'"')

    if 'stdout' in gsUIChoice:

        print(time.strftime("%H:%M:%S")+': '+sMsg)

    if 'notification' in gsUIChoice:

        # https://plyer.readthedocs.io/en/latest/#
        # https://github.com/kivy/plyer
        # no way to have notification remain permanently

        if gbOSLinux:
            # notifications appear both on desktop (briefly) and in tray
            notification.notify(title='IP address changed', message=sMsg, app_name='ipwatch', timeout=8*60*60)

        if gbOSWindows:
            notification.notify(title='IP address changed', message=sMsg, app_name='ipwatch', timeout=8*60*60)

    if 'syslog' in gsUIChoice:

        if gbOSLinux:
            syslog.syslog(sMsg)
            # on Linux, to see output:
            #   sudo journalctl --pager-end
            # or
            #   sudo journalctl | grep ipwatch

        if gbOSWindows:
            # https://stackoverflow.com/questions/51385195/writing-to-windows-event-log-using-win32evtlog-from-pywin32-library
            # https://www.programcreek.com/python/example/96660/win32evtlogutil.ReportEvent
            # https://docs.microsoft.com/en-us/windows/win32/eventlog/event-logging-elements
            win32evtlogutil.ReportEvent(
                                        "ipwatch",
                                        #7040,       # event ID  # https://www.rapidtables.com/convert/number/decimal-to-binary.html
                                        1610612737,  # event ID  # https://www.rapidtables.com/convert/number/decimal-to-binary.html
                                        eventCategory=1,
                                        eventType=win32evtlog.EVENTLOG_INFORMATION_TYPE,
                                        strings=[sMsg],
                                        data=b"")
            # https://rosettacode.org/wiki/Write_to_Windows_event_log#Python
            # on Win10, to see output:
            # run Event Viewer application.


#--------------------------------------------------------------------------------------------------


#def iptoint(ip):
#    return int(socket.inet_aton(ip).encode('hex'),16)


#--------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    
    # unfortunately AF_NETLINK is not available on Windows
    #print('getattr(AF_NETLINK) == '+str(getattr(socket, 'AF_NETLINK', None)))

    if gbOSLinux:

        objSocket = socket.socket(socket.AF_NETLINK, socket.SOCK_RAW, socket.NETLINK_ROUTE)
        #print('os.getpid '+str(os.getpid()))
        #print('os.getaddrinfo '+str(socket.getaddrinfo(None,1)))
        objSocket.bind((os.getpid(), 1))       # works but slow
        #objSocket.bind((0, 1))       # works but slow
        #objSocket.bind((0, 0))          # doesn't work, no msgs
        #objSocket.bind((0, 31))       # works but slow
        #objSocket.bind((os.getpid(), 31))       # works but slow
        #objSocket.bind((int(ipaddress.IPv4Address("192.168.0.1")), 1))       # works but slow
        #objSocket.bind((int(ipaddress.IPv4Address("192.168.0.159")), 1))       # works but slow

    while True:

        sNewIPAddress = GetAddress()

        if gsOldIPAddress != sNewIPAddress:
            ReportChange(sNewIPAddress)
            gsOldIPAddress = sNewIPAddress

        try:

            if gbOSLinux:

                # http://man7.org/linux/man-pages/man7/netlink.7.html
                # https://docs.python.org/3/library/socket.html
                # https://gist.github.com/Lukasa/6209575d588f1584c374
                try:
                    objSocket.settimeout(gnSleep)
                    #print('about to socket.recv with timeout of '+str(gnSleep))
                    objData = objSocket.recv(10)    # rest of data will be discarded
                    #print('data "'+str(objData)+'"')
                except OSError as objE:
                    #print('exception "'+str(objE)+'"')
                    i = 1       # placeholder

            if gbOSWindows:
                time.sleep(gnSleep)

        except KeyboardInterrupt:
            if gbOSLinux:
                objSocket.close()
            sys.exit()
        #except InterruptedError as objE:
            #print('sigtimedwait exception "'+str(objE)+'"')


#--------------------------------------------------------------------------------------------------
