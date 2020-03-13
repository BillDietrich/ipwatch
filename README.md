# ipwatch
Reports when your system's public IP address changes.

Intended to reveal when your VPN is up or down, so you can have some confidence that it's actually working.

Tested only on Linux Mint 19 and Windows 10 Home.

https://github.com/BillDietrich/ipwatch

There are many other similar projects in GitHub.  This one is a little different in that it works on both Linux and Win10, and also supports reporting via system log and stdout and desktop notifications.  Some others are Linux-only, or only report to specific email or messaging systems.  Also, on Linux this supports automatically restarting IPsec when the network goes down and then comes back up.

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

# After python is installed:
pip3 install plyer
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

With Python installed:

1. pip install requests
2. pip install pywin32
3. pip install plyer

### Edit ipwatch.py
#### On Linux
No edits needed in ipwatch.py

#### On Windows 10
Edit ipwatch.py to:
* Change the line "gbOSLinux = True" to "gbOSLinux = False".

---

## Quick-start to try ipwatch: run it manually

### On Linux command-line
```bash
ipwatch.py
```

See desktop notifications.

### On Windows 10
Double-click on ipwatch.cmd file.

See notifications in "action center" at right end of system tray.

---

## Ways ipwatch can report IP address changes

You can choose one or more of the following:

### Desktop notifications
(This is the default setting; no edit needed unless you change things later.)

Edit ipwatch.py to set gsUIChoice to "notification".

You will see notifications on the desktop or in the "action center".

### To stdout
Edit ipwatch.py to set gsUIChoice to "stdout".

You will see reports in the command-line window where you ran ipwatch.py.

### To system log
Edit ipwatch.py to set gsUIChoice to "syslog".

You will see reports in the system log:

For Linux, to see output, on command-line do
```bash
sudo journalctl | grep ipwatch
```

For Win10, to see output, run Event Viewer application.  Look in administrative events from Applications, and look for events with Origin "ipwatch".

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

### Run the program automatically

#### From a Linux systemd service started at system boot time
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

#### From a Windows 10 task started when you log in

1. Go to Control Panel / Administrative Tools / Program Tasks.
2. In Actions (rightmost pane), click on Local Tasks / Create Basic Task.
3. Set Name of Task to "ipwatch" (not mandatory, just for clarity).
4. Set various fields.
5. For "When do you want to run the task ?" select "At start of session".
6. For "What action do you want to take for this task ?" select "Run a program".
7. For "Program or Script" select the ipwatch.cmd file.
8. Save the task.
9. The task will appear in the list of Active Tasks (bottom of middle pane).
10. Log out and back in.
11. ipwatch should report an IP address change, in whatever way it's configured to report.

---

## Additional configuration

### IPsec (Linux only)
If you are using a VPN with IPsec (such as strongSwan and IKEv2), sometimes the VPN connection does not get re-established if the network connection goes down and then comes back up.

To fix this, install ipwatchnetup and ipwatchnetdown and un-comment the three-line "if" statement near the end of ipwatchnetup, which will restart IPsec each time the network comes up.  I recommend you do this.
```bash
sudo cp ipwatchnetdown /etc/network/if-post-down.d
sudo cp ipwatchnetup /etc/network/if-up.d
sudo edit /etc/network/if-up.d/ipwatchnetup
```

### No-VPN address prefix
To give a minor tweak to the polling frequency, you could edit ipwatch.py to change the value of gsIPAddressStartNoVPN to contain the first part of your IP address from your ISP (when the VPN is not active).  Probably not worth doing.

### DNS accesses
You could edit ipwatch.py to make the IP address be retrieved using DNS accesses instead of HTTP accesses.  I don't recommend you do this.

#### On Linux

To use DNS accesses (not recommended), you must:
* pip3 install dnspython
* Edit ipwatch.py to un-comment the line "import dns.resolver"
* Edit ipwatch.py to set gsAccessType to "DNS"

If you want to use DNS accesses AND run as a service, you must also:
* sudo -H pip3 install dnspython

#### On Windows 10

???

### Sites to fetch IP address from
Edit ipwatch.py, function GetIPAddressViaHTTP, array arrsSites to see and change the web sites the IP address is fetched from.  This should be necessary only if some site stops working for some reason.

---

## Testing
1. After ipwatch.py starts (either via command-line or service), look for a report that system's public IP address has changed from "start" to some valid value such as "1.2.3.4".  Check to see if the valid value is from your ISP or your VPN.
2. Disconnect from the network, and look for a report that system's public IP address has changed from some valid value such as "1.2.3.4" to "no network connection".
3. Re-connect to the network, and look for a report that system's public IP address has changed from "no network connection" to some valid value such as "1.2.3.4".  Check to see if the valid value is from your ISP or your VPN.

[Would be nice to have a VPN test server that went up and down regularly, so we could test that situation.]

---

## Limitations
* Does polling on Windows.  Can't poll too frequently, or else it would slow down the system and maybe violate TOS on the web site that it fetches the IP address from.  So it's possible to miss brief, transient changes.  And a change of address may be reported as much as 60 or 120 seconds after it actually happens.
* Tested only on Linux Mint 19.3 Cinnamon with 5.3 kernel, and Windows 10 Home.
* Tested only with IPv4, not IPv6.
* On Linux, tested only with strongSwan/IPsec to Windscribe VPN.
* On Win10, tested only without VPN.
* Not tested on a LAN with no internet access.
* Requires Python 3.3 or greater.
* Can't really guarantee that at boot time this service will report the public IP address before any other service does any internet access.  So it really can't give 100% assurance that there is no IP leak before the VPN starts up.
* Can't guarantee that quick, transient changes in the public IP address will be detected.  So it really can't give 100% assurance that there is no IP leak caused by brief faults in the VPN.

## To-Do
* Automatically detect OS type.
* Any way to stop polling on Win10 ?
* Spin off threads so we don't miss any changes ?
* In Linux with VPN, when you unplug the Ethernet cable, the socket notifies right away.  But then trying to fetch the IP address takes a long time (8-10 seconds) to time out, even with a short timeout specified in the app.  Not sure if the delay is in the VPN or somewhere else.  So the app feels very slow.  Not sure if it happens in other configurations too.

---

## Privacy Policy
This code doesn't collect, store, process, or transmit anyone's identity or personal information in any way.  It does not modify or transmit your system's data outside your system in any way.
