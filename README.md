# naplps-server
A basic NAPLPS server for interacting with compatible hardware terminals.

## Requirements

You will need a terminal thst supports NAPLPS (obviously) This was designed for and tested with the AT&T Sceptre but other terminals such as the AlexTel or Telidon-compatible terminals will likely work (but we would love testers). This does not support Minitel/TELETEL, Prestel, or Bildschirmtext terminals.

The server is written in python, so it should be fairly portable, but it has only been tested on a Ubuntu machine. it likely would not take much to get it running on another POSIX system like MacOS.

The server will need a standard Hayes-compatible dial-up modem. This has been tested with an inexpensive USB modem with a Conexant chipset, commonly branded for Dell or Lenovo. Other modems should work just fine.

Between the terminal and the modem, there needs to be something acting as a telephone network. Decades ago this would have been the PSTN, but it should work just fine with a more modern colution. Testing was done eith a Viking line simulator but more testing will be done with SIP devices.

## Software Setup

Before running the server you will need to know the device that corresponds with the modem connected to the host. In my case it is `/dev/ttyACM0`. If you have a serial modem connected to a USB/serial adapter it will likely be `/dev/ttyUSB0`. On a Mac this might be `/dev/cu.usbserial-xxxxxxxx`.

To avoid using `sudo` your user needs to be added to the `dialout` group:

```
sudo usernod -aG dialout yourUsername
```

After this you will need to log out and back in or otherwise find a away to refresh your groups:

```
exec su - yourUsername
```

The only software dependency is `python3`:

```
sudo apt-get install python3
```

## Running the Server

The server takes an optional argument for the device, and if not supplied it will default to `/dev/ttyUSB0`

```
python3 naplps-server.py /dev/tryACM0
```

Basic logging to the console will let you know how the server is operating. The server can be terminated with `ctrl-c` as needed.

## Adding/Removing Images

Images added to the `images` directory will be randomly sent to the terminal. Current logic does not allow the same image to be sent twice in a row, so you should get a different image eith every push. Images added to the directory will not enter the rotation until after the server is restarted. It is not recommended to remove images from the directory while the server is running.

Only images ending in the `.nap` (case insensitive) extension will be displayed. Note thet not all NAPLPS images seem to be created equally and some will not render properly.

The images in this directory currently are sample images that should work out-of-the-box.

Attribution for the images can be found in the [images/README.md](images/README.md).
