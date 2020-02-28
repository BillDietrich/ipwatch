# ipwatch
Reports when your system's public IP address changes.

Intended to reveal when your VPN is up or down, so you can have some confidence that it's actually working.

Tested only on Linux Mint 19 and Windows 10 Home.

https://github.com/BillDietrich/ipwatch

There are many other similar projects in GitHub.  This one is a little different in that it should be fairly portable, and also supports reporting via system log and stdout and desktop notifications.  Some others maybe aren't so portable, or only report to specific email or messaging systems.  Also, this one supports automatically restarting IPsec when the network goes down and then comes back up.

---

## Basic installation

### Copy the minimal files to disk
In the GitHub repo, click the "Clone or download" button, then click the "Download ZIP" button.  Save the ZIP file to disk.
#### On Linux
Copy file ipwatch.py from the ZIP file to /usr/local/bin

#### On Windows 10
Copy files ipwatch.cmd and ipwatch.py from the ZIP file to some folder.

### Requires Python 3.3+
#### On Linux
```bash
# See what is installed
python3 --version

# If it's not installed:
# On Debian-type Linux:
sudo apt-get update
sudo apt-get install python3
```

#### On Windows 10
Open windows command prompt: Win+X and then choose "Command Shell (as Administrator)".

Type "python -V"

If Python is not installed:

1. Go to https://www.python.org/downloads/windows/
2. Download installer (EXE).
3. Run the installer.
4. In the installer, check the checkboxes "Installer launcher for all users" and "Add Python 3 to PATH" before you click on the Install button.
5. Near end of installation, click on "Disable limit on PATH length".
6. After installer finishes, open windows command prompt (Win+X and then choose "Command Shell (as Administrator)") and type "python -V" to verify the installation.
7. pip install requests
8. pip install pywin32

### Edit ipwatch.py
#### On Linux
No edits needed in ipwatch.py

Default is to use HTTP requests, and report via desktop notifications.

#### On Windows 10
Edit ipwatch.py to:
* Change the line "gbOSLinux = True" to "gbOSLinux = False".
* Change the line "gsUIChoice = 'notification'" to "gsUIChoice = 'stdout'".

---

## Quick-start to try ipwatch: run it manually

### On Linux command-line
```bash
ipwatch.py
```

See desktop notifications.

### On Windows 10
Double-click on ipwatch.cmd file.

See output in the text window.

---

## Ways ipwatch can report IP address changes

You can choose one or more of the following:

### Desktop notifications
(This is the default setting; no edit needed unless you change things later.)

Edit ipwatch.py to set gsUIChoice to "notification".

You will see notifications on the desktop.  Notifications are non-modal on Linux (ipwatch keeps going without waiting for user to do anything), but modal on Windows 10 (a modal dialog is displayed and ipwatch waits until user closes the dialog).

To use on Linux, Zenity must be installed (it's installed by default on Mint 19).  To see if it is installed, on command-line run "zenity --version".

To use on Win10, download https://github.com/maravento/winzenity/raw/master/zenity.zip and copy the EXE file inside it to the same folder where ipwatch.py is located.

### To stdout
Edit ipwatch.py to set gsUIChoice to "stdout".

You will see reports in the command-line window where you ran ipwatch.py.

### To system log
Edit ipwatch.py to set gsUIChoice to "syslog".

To use on Win10, do "pip install pywin32".

You will see reports in the system log:

For Linux, on command-line do
```bash
sudo journalctl | grep ipwatch
```

For Win10, run Event Viewer application.  Look in administrative events from Applications, and look for events with Origin "ipwatch".

---

## Ways to run ipwatch

### Run the program manually
(Easiest way to start out; try this first.)

#### On Linux command-line
```bash
ipwatch.py
```

Then try steps in the "Testing" section, below.

#### On Windows 10
Double-click on ipwatch.cmd file.

Then try steps in the "Testing" section, below.


### From a Linux systemd service started at system boot time
```bash
sudo cp ipwatch.py /usr/local/bin		# you may have done this already
sudo edit /usr/local/bin/ipwatch.py		# to set gsUIChoice to "syslog".
sudo cp ipwatch.service /etc/systemd/system
```

After rebooting, on command-line do
```bash
sudo journalctl | grep ipwatch
```
Then try steps in the "Testing" section, below, and check the journal again.

---

## Additional connection to signal when network goes up/down (Linux only)
(This gives faster reporting of changes.  And it works no matter how you have run ipwatch.py, from command-line or service.)

```bash
sudo cp ipwatchnetdown /etc/network/if-post-down.d
sudo cp ipwatchnetup /etc/network/if-up.d

# If you want to restart IPsec when network comes up (see IPsec section):
sudo edit /etc/network/if-up.d/ipwatchnetup
# Un-comment the three-line "if" statement near the end
```

---

## Additional configuration

### IPsec (Linux only)
If you are using a VPN with IPsec (such as strongSwan and IKEv2), sometimes the VPN connection does not get re-established if the network connection goes down and then comes back up.

To fix this, un-comment the three-line "if" statement near the end of ipwatchnetup, which will restart IPsec each time the network comes up.  I recommend you do this.
```bash
sudo edit /etc/network/if-up.d/ipwatchnetup
```

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
1. After ipwatch.py starts (either via command-line or service), look for a report that system's public IP address has changed from "start" to some valid value such as "1.2.3.4".  Check to see if the valid value is from your ISP or your VPN.
2. Disconnect from the network, and look for a report that system's public IP address has changed from some valid value such as "1.2.3.4" to "no network connection".
3. Re-connect to the network, and look for a report that system's public IP address has changed from "no network connection" to some valid value such as "1.2.3.4".  Check to see if the valid value is from your ISP or your VPN.

[Would be nice to have a VPN test server that went up and down regularly, so we could test that situation.]

---

## Limitations
* Does polling.  Can't poll too frequently, or else it would slow down the system and maybe violate TOS on the web site that it fetches the IP address from.  So it's possible to miss brief, transient changes.  And a change of address may be reported as much as 60 or 120 seconds after it actually happens.
* Tested only on Linux Mint 19.3 Cinnamon with 5.3 kernel, and Windows 10 Home.
* Tested only with IPv4, not IPv6.
* Tested only with strongSwan/IPsec to Windscribe VPN.
* Not tested on a LAN with no internet access.
* Requires Python 3.3 or greater.
* Only the first site in arrsSites is used to fetch IP address.
* Can't really guarantee that at boot time this service will report the public IP address before any other service does any internet access.  So it really can't give 100% assurance that there is no IP leak before the VPN starts up.
* Can't guarantee that quick, transient changes in the public IP address will be detected.  So it really can't give 100% assurance that there is no IP leak caused by brief faults in the VPN.

## To-Do
* Any way to run as service on Win10 ?
* Any way to get a signal about network going down/up on Win10 ?

---

## Privacy Policy
This code doesn't collect, store, process, or transmit anyone's identity or personal information in any way.  It does not modify or transmit your system's data outside your system in any way.
