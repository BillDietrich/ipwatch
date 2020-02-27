# ipwatch
Reports when your system's public IP address changes.

Intended to reveal when your VPN is up or down, so you can have some confidence that it's actually working.

Tested only on Linux Mint 19.

https://github.com/BillDietrich/ipwatch

There are many other similar projects in GitHub.  This one is a little different in that it should be fairly portable, and also supports reporting via system log and stdout and desktop notifications.  Some others maybe aren't so portable, or only report to specific email or messaging systems.  Also, this one supports automatically restarting IPsec when the network goes down and then comes back up.

---

## Ways it can report IP address changes

You can choose one or more of the following:

### Desktop notifications
(This is the default setting; no edit needed unless you change things later.)

Edit ipwatch.py to set gsUIChoice to "notification".

You will see notifications in the Linux system tray, or wherever your desktop displays notifications.

### To stdout
Edit ipwatch.py to set gsUIChoice to "stdout".

You will see reports in the command-line Terminal where you ran ipwatch.py.

### To system log
Edit ipwatch.py to set gsUIChoice to "syslog".

You will see reports in the system log.  For Linux, on command-line do "sudo journalctl | grep ipwatch".

---

## Ways to run ipwatch

### From command-line
(Easiest way to start out; try this first.)

./ipwatch.py

Then try steps in the "Testing" section, below.

### From a Linux systemd service started at system boot time
sudo cp ipwatch.py /usr/local/bin

sudo edit /usr/local/bin/ipwatch.py to set gsUIChoice to "syslog".

sudo cp ipwatch.service /etc/systemd/system

After rebooting, on command-line do "sudo journalctl | grep ipwatch". Then try steps in the "Testing" section, below, and check the journal again.

---

## Additional connection to signal when network goes up/down
(This gives faster reporting of changes.  And it works no matter how you have run ipwatch.py, from command-line or service.)

sudo cp ipwatch.netdown /etc/network/if-post-down.d

sudo cp ipwatch.netup /etc/network/if-up.d

sudo edit /etc/network/if-up.d/ipwatch.netup if you want to restart IPsec when network comes up (see IPsec section).

---

## Additional configuration

### IPsec
If you are using a VPN with IPsec (such as strongSwan and IKEv2), sometimes the VPN connection does not get re-established if the network connection goes down and then comes back up.

To fix this, un-comment the three-line "if" statement near the end of ipwatch.netup, which will restart IPsec each time the network comes up.  I recommend you do this.  sudo edit /etc/network/if-up.d/ipwatch.netup

### No-VPN address prefix
To give a minor tweak to the polling frequency, you could edit ipwatch.py to change the value of gsIPAddressStartNoVPN to contain the first part of your IP address from your ISP (when the VPN is not active).  Probably not worth doing.

### DNS accesses
You could edit ipwatch.py to make the IP address be retrieved using DNS accesses instead of HTTP accesses.  I don't recommend you do this.

To use DNS accesses, you must:
* pip3 install dnspython
* Edit ipwatch.py to un-comment the line "import dns.resolver"
* Edit ipwatch.py to set gsAccessType to "DNS"

If you want to use DNS accesses AND run as a service, you must also:
* sudo -H pip3 install dnspython

### Sites to fetch IP address from
Edit ipwatch.py, function GetIPAddressViaHTTP, array arrsSites to see and change the web site the IP address is fetched from.  This should be necessary only if the default site stops working for some reason.

---

## Testing
* After ipwatch.py starts (either via command-line or service), look for a report that system's public IP address has changed from "start" to some valid value such as "1.2.3.4".  Check to see if the valid value is from your ISP or your VPN.
* Disconnect from the network, and look for a report that system's public IP address has changed from some valid value such as "1.2.3.4" to "no network connection".
* Re-connect to the network, and look for a report that system's public IP address has changed from "no network connection" to some valid value such as "1.2.3.4".  Check to see if the valid value is from your ISP or your VPN.

---

## Limitations
* Does polling.  Can't poll too frequently, or else it would slow down the system and maybe violate TOS on the web site that it fetches the IP address from.  So it's possible to miss brief, transient changes.  And a change of address may be reported as much as 60 or 120 seconds after it actually happens.
* Tested only on Linux Mint 19.3 Cinnamon with 5.3 kernel.
* Tested only with IPv4, not IPv6.
* Tested only with strongSwan/IPsec to Windscribe VPN.
* Not tested on a LAN with no internet access.
* Requires Python 3.3 or greater.
* Only the first site in arrsSites is used to fetch IP address.
* Can't really guarantee that at boot time this service will report the public IP address before any other service does any internet access.  So it really can't give 100% assurance that there is no IP leak before the VPN starts up.
* Can't guarantee that quick, transient changes in the public IP address will be detected.  So it really can't give 100% assurance that there is no IP leak caused by brief faults in the VPN.

---

## Privacy Policy
This code doesn't collect, store or transmit anyone's identity or personal information in any way.  It does not modify or transmit your system's data outside your system in any way.
