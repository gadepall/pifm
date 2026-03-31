#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time
import argparse

TX_PIN   = 18
BIT_TIME = 0.05  # 50ms per bit = 20 bps

def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(TX_PIN, GPIO.OUT)
    GPIO.output(TX_PIN, GPIO.LOW)

def send_byte(val):
    t = time.time()
    
    # Start bit (1 - Light ON)
    GPIO.output(TX_PIN, GPIO.HIGH)
    gap = (t + BIT_TIME) - time.time()
    if gap > 0: time.sleep(gap)

    # 8 Data bits
    for i in range(8):
        bit = (val >> i) & 1
        GPIO.output(TX_PIN, GPIO.HIGH if bit else GPIO.LOW)
        target = t + BIT_TIME * (i + 2)
        gap = target - time.time()
        if gap > 0: time.sleep(gap)

    # Stop bit (0 - Light OFF)
    GPIO.output(TX_PIN, GPIO.LOW)
    target = t + BIT_TIME * 10
    gap = target - time.time()
    if gap > 0: time.sleep(gap)

def send_message(msg):
    print(f"[TX] Sending: '{msg}'")
    
    # Preamble (Wake up receiver)
    GPIO.output(TX_PIN, GPIO.HIGH)
    time.sleep(1.0)
    GPIO.output(TX_PIN, GPIO.LOW)
    time.sleep(0.5)
    
    # Send Characters
    for char in msg:
        send_byte(ord(char))
        time.sleep(BIT_TIME * 2)  # Tiny pause between letters
        
    send_byte(0x00) # End message
    GPIO.output(TX_PIN, GPIO.LOW)
    print("[TX] Done.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--message", default="HELLO WORLD FROM LIFI")
    args = parser.parse_args()
    
    setup()
    try:
        send_message(args.message)
    finally:
        GPIO.cleanup()
