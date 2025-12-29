# naplps-server

A basic NAPLPS server for interacting with compatible hardware terminals.

After connection, this server will send NAPLPS graphics to the terminal in a loop with a 10 second delay between each push.

[Awesome, I want to run my own!](#software-setup)  
[I have a phone line, how can i connect to the demo?](#live-demo-experimental)

This is a quick project I built in about 6 hours because I bought an AT&T Sceptre and wanted to get it working. Proper writeup forthcoming!

## Requirements

You will need a terminal thst supports NAPLPS (obviously) This was designed for and tested with the AT&T Sceptre but other terminals such as the AlexTel or Telidon-compatible terminals will likely work (but we would love testers). This does not support Minitel/TELETEL, Prestel, or Bildschirmtext terminals.

The server is written in python, so it should be fairly portable, but it has only been tested on a Ubuntu machine. it likely would not take much to get it running on another POSIX system like MacOS.

The server will need a standard Hayes-compatible dial-up modem. This has been tested with an inexpensive USB modem with a Conexant chipset, commonly branded for Dell or Lenovo. Other modems should work just fine.

Between the terminal and the modem, there needs to be something acting as a telephone network. Decades ago this would have been the PSTN, but it should work just fine with a more modern colution. Testing was done with a Viking line simulator but more testing will be done with SIP devices.

## Software Setup

Before running the server you will need to know the device that corresponds with the modem connected to the host. In my case it is `/dev/ttyACM0`. If you have a serial modem connected to a USB/serial adapter it will likely be `/dev/ttyUSB0`. On a Mac this might be `/dev/cu.usbserial-xxxxxxxx`.

To avoid using `sudo` your user needs to be added to the `dialout` group:

```
sudo usermod -aG dialout $USER
```

After this you will need to log out and back in or otherwise find a away to refresh your groups:

```
exec su - $USER
```

The only software dependency is `python3`, though we do need the `pyserial` package:

```
sudo apt-get install python3 python3-serial
```

## Running the Server

The server takes an optional argument for the device, and if not supplied it will default to `/dev/ttyUSB0`

```
python3 naplps-server.py /dev/ttyACM0
```

Basic logging to the console will let you know how the server is operating. The server can be terminated with `ctrl-c` as needed.

## Terminal Settings

How to configure your terminal to connect to the server.

### AT&T Sceptre

At the landing screen (Data Base Access) press `MODE` for the Mode Select screen and then `2` for Directory. Then press a number 1-5 to create an entry:

| Setting    | Value |
| -------- | ------- |
| Name             | *any*      |
| Contents         | `SHIFT+PHONE`*number*`SHIFT+DATA` |
| Setup Parameters | yes        |
| Parity           | None       |
| Duplex           | Full       |
| All Caps         | Off        |
| Protocol         | NAPLPS 8   |
| Sync/Async       | Async-1200 |
| Flow Ctrl        | On/On      |
| EOL Char         | CR         |

Then press `RETURN` to save. Press `MODE` to return to the Mode Select screen and `1` to go back to the Data Base Access screen. From here you can press the digit of the entry you made to start the call.

## Running as a Service

The server can be impleneted as a `systemd` service.

Clone the project into `/opt` and copy `conf/naplps-server@.service` into `/etc/systemd/system/`.

```
cd /opt
git clone https://github.com/dialup-world/naplps-server.git
sudo cp naplps-server/conf/naplps-server@.service /etc/systemd/system/naplps-server@.service
```

Ensure our log file exists (might not be needed):

```
sudo touch /var/log/naplps-server.log
```

Reload `systemd` units:

```
sudo systemctl daemon-reload
```

Start and enable the service while specifying your device. I am using `ttyACM0`:

```
sudo systemctl start naplps-server@ttyACM0.service
sudo systemctl enable naplps-server@ttyACM0.service
```

Check status and logs:

```
sudo systemctl status naplps-server@ttyACM0.service
sudo tail -f /var/log/naplps-server.log
```

## Live Demo (Experimental)

We currently have a live demo up you can connect to with your videotex terminal via a variety of methods. It is *flakey* and can break easily. More work will be done to see about how (if) we can improve this.

* PSTN (US/Canada only) - `267-921-1337`
* PhreakNet - `263-0502`
* Direct SIP
  - Server: `sip.dialup.world`
  - Port: `16556`
  - User: `naplps`
  - Password: `naplps`
  - Codecs: `G.711/ulaw` ONLY
  - Number: any

## Adding/Removing Images

Images added to the `images` directory will be randomly sent to the terminal. Current logic does not allow the same image to be sent twice in a row, so you should get a different image with every push. Images added to the directory will not enter the rotation until after the server is restarted. It is not recommended to remove images from the directory while the server is running.

Only images ending in the `.nap` (case insensitive) extension will be displayed. Note thet not all NAPLPS images seem to be created equally and some will not render properly.

The images in this directory currently are sample images that should work out-of-the-box.

Attribution for the images can be found in the [images/README.md](images/README.md).

## TO-DO

* Play around with parity/error-correcting. It seems the terminal was aware of errora if set to use a parity bit, but I didnt see it attempt a retry.

## Further Reading

A lot of other people have been working on interesting things in this space and I'd like to highlight a few

* [Remember Tomorrow: A Telidon Story](https://www.remembertomorrow.ca/en-ca) - John Durno has been working on preserving/reviving NAPLPS/Telidon work for the last decade and this project showcases some fantastic artwork and artists from this forgotten medium.
* [Interactive NAPLPS (Telidon 709) Graphics on a Modern Computer: Technical Note](https://dspace.library.uvic.ca/items/599ee778-0bac-452e-9624-b5c04832a0d7) - This technical note and accompanying demo describes a method for [re] creating interactive presentations of NAPLPS graphics on modern (as of 2017) computing hardware. (John Durno)
* [NAPLPS: Videotex/Teletext Presentation Level Protocol Syntax](https://archive.org/details/naplps-CSA-T500-1983) - The NAPLPS specification. 
* [The glorious futility of generating NAPLPS in 2023](https://scruss.com/blog/2023/09/18/the-glorious-futility-of-generating-naplps-in-2023/) - Some "recent" research done in working with NAPLPS graphics in 2023.
* [Vintage Bell Alextel computer terminal can display graphics!](https://www.youtube.com/watch?v=0BKRfM5HHSM) - Video from vintagecomputer.ca that helped me determine at a high level how to send data to a NAPLPS terminal.
