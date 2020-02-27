# ipwatch
Reports when your system's public IP address changes.

Intended to reveal when your VPN is up or down, so you can have some confidence that it's atually working.

Tested only on Linux Mint 19.

https://github.com/BillDietrich/ipwatch

---

## Ways it can report IP address changes

You can choose one or more of the following:

### Desktop notifications
(This is the default setting; no edit needed unless you change things later.)

Edit ipwatch.py to set gsUIChoice to "notification".

### To stdout
Edit ipwatch.py to set gsUIChoice to "stdout".

### To system log (Linux journal)
Edit ipwatch.py to set gsUIChoice to "syslog".

---

## Ways to run it

### From command-line
(Easiest way to start out; try this first.)

./ipwatch.py

### From a systemd service started at system boot time
sudo cp ipwatch.py /usr/local/bin

sudo cp ipwatch.service /etc/systemd/system

---

## Additional connection to signal when network goes up/down
(This gives faster reporting of changes.  And it works no matter how you have run ipwatch.py, from command-line or service.)

sudo cp ipwatch.netdown /etc/network/if-post-down.d

sudo cp ipwatch.netup /etc/network/if-up.d

---

## Additional configuration

### IPsec
If you are using a VPN with IPsec (such as strongSwan and IKEv2), sometimes the VPN connection does not get re-established if the network connection goes down and then comes back up.

To fix this, un-comment the three-line "if" statement near the end of ipwatch.netup, which will restart IPsec each time the network comes up.  I recommend you do this.

### DNS accesses
You could edit ipwatch.py to make the IP address be retrieved using DNS accesses instead of HTTP accesses.

To use DNS accesses, you must:
* pip3 install dnspython
* Edit ipwatch.py to un-comment the line "import dns.resolver"
* Edit ipwatch.py to set gsAccessType to "DNS"

If you want to use DNS accesses AND run as a service, you must also:
* sudo -H pip3 install dnspython

### Sites to fetch IP address from
Edit ipwatch.py, function GetIPAddressViaHTTP, array arrsSites to see and change the web site the IP address is fetched from.

---

## Limitations
* Does polling, and can't do that too frequently, or else it would slow down the system and maybe violate TOS on the web site that it fetches the IP address from.  So it's possible to miss brief, transient changes.  And a change may be reported as much as 60 or 120 seconds after it actually happens.
* Tested only on Linux Mint 19.3 Cinnamon.
* Requires Python 3.3 or greater.
* Only the first site in arrsSites is used to fetch IP address.

---

## Privacy Policy
This code doesn't collect, store or transmit your identity or personal information in any way.
