#!/usr/bin/env python3
"""\
This script serves as a simple NAPLPS server

Usage: naplps-server.py <serial-device>
Example: naplps-server.py /dev/ttyACM0
"""
import serial
import time
import logging
import os
import signal
import sys
import random

DEFAULT_SERIAL_PORT = '/dev/ttyUSB0'
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
NAPLPS_DIR = os.path.join(SCRIPT_DIR, 'images')
LOOP_DELAY = 10  # seconds

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')

running = True
last_file = None

def handle_shutdown(signum, frame):
    global running
    if running:
        running = False
        logging.info("Shutting down...")
    else:
        sys.exit(1)

signal.signal(signal.SIGINT, handle_shutdown)
signal.signal(signal.SIGTERM, handle_shutdown)

def interruptible_sleep_with_monitor(ser, seconds):
    """Sleep and monitor remote input, logging per-character during wait."""
    buffer = ""
    elapsed = 0.0
    step = 0.1
    while running and elapsed < seconds:
        time.sleep(step)
        elapsed += step

        if ser.in_waiting:
            try:
                char = ser.read().decode(errors='ignore')
                buffer += char

                # Display to console
                sys.stdout.write(char)
                sys.stdout.flush()

                # Log each visible char separately
                if char.strip():
                    logging.info(f"[REMOTE CHAR] {repr(char)}")

                # Check for disconnects
                if "NO CARRIER" in buffer or "BUSY" in buffer:
                    logging.info("Modem disconnected.")
                    return False

            except Exception as e:
                logging.warning(f"Error reading serial: {e}")
                return False
    return True

def open_serial(port):
    return serial.Serial(
        port=port,
        baudrate=1200,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,  # no parity
        stopbits=serial.STOPBITS_ONE,
        xonxoff=False,
        rtscts=False,
        dsrdtr=False,
        timeout=0,
        write_timeout=600
    )

def wait_for_ring(ser):
    logging.info("Waiting for RING...")
    buffer = ""
    while running:
        if ser.in_waiting:
            char = ser.read().decode(errors='ignore')
            buffer += char
            if "RING" in buffer:
                logging.info("RING detected.")
                return
        time.sleep(0.1)

def wait_for_connect(ser):
    logging.info("Sending ATA...")
    ser.write(b'ATA\r')
    buffer = ""
    while running:
        if ser.in_waiting:
            char = ser.read().decode(errors='ignore')
            buffer += char
            if "CONNECT" in buffer:
                logging.info("Connection established.")
                return True
            elif "NO CARRIER" in buffer:
                logging.info("Call dropped.")
                return False
        time.sleep(0.1)
    return False

def get_random_nap_file():
    global last_file

    if not os.path.isdir(NAPLPS_DIR):
        logging.error(f"NAPLPS directory does not exist: {NAPLPS_DIR}")
        return None

    files = [f for f in os.listdir(NAPLPS_DIR)
             if os.path.isfile(os.path.join(NAPLPS_DIR, f)) and f.lower().endswith('.nap')]

    if not files:
        logging.error(f"No .nap files found in directory: {NAPLPS_DIR}")
        return None

    if last_file and len(files) > 1:
        files = [f for f in files if f != last_file]

    chosen = random.choice(files)
    last_file = chosen
    return os.path.join(NAPLPS_DIR, chosen)

def send_naplps_loop(ser):
    logging.info("Starting NAPLPS send loop with 10ms/char delay.")
    while running:
        nap_file = get_random_nap_file()
        if not nap_file:
            logging.error("No NAPLPS file to send.")
            return

        logging.info(f"Sending file: {nap_file}")
        try:
            with open(nap_file, 'rb') as f:
                data = f.read()

            for byte in data:
                if not running:
                    return
                ser.write(bytes([byte]))
                time.sleep(0.01)  # 10ms per byte

            logging.info(f"NAPLPS file sent. Sleeping for {LOOP_DELAY} seconds and monitoring for input...")

            if not interruptible_sleep_with_monitor(ser, LOOP_DELAY):
                break

        except (serial.SerialException, OSError) as e:
            logging.warning(f"Connection lost during send: {e}")
            break

def main():
    port = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_SERIAL_PORT
    logging.info(f"Using serial port: {port}")
    logging.info(f"Loading images from: {NAPLPS_DIR}")

    while running:
        try:
            with open_serial(port) as ser:
                ser.write(b'ATZ\r')
                time.sleep(1)
                ser.write(b'ATS0=0\r')
                time.sleep(1)

                wait_for_ring(ser)
                if wait_for_connect(ser):
                    send_naplps_loop(ser)
                    logging.info("Connection ended. Returning to idle...")
                else:
                    logging.info("No connection made. Returning to idle...")
        except serial.SerialException as e:
            logging.error(f"Serial error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
