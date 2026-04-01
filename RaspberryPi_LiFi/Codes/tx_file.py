#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time
import argparse
import os

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

def send_file(filepath):
    if not os.path.exists(filepath):
        print(f"[TX] Error: '{filepath}' not found.")
        return

    # Read the text file
    with open(filepath, 'r', encoding='utf-8') as f:
        text_data = f.read()

    print(f"[TX] Transmitting '{filepath}' ({len(text_data)} characters)...")
    
    # Preamble (Wake up receiver)
    GPIO.output(TX_PIN, GPIO.HIGH)
    time.sleep(1.0)
    GPIO.output(TX_PIN, GPIO.LOW)
    time.sleep(0.5)
    
    # Send Characters one by one
    for i, char in enumerate(text_data):
        # We use ord() to convert the character to its ASCII number
        # If it's a weird unicode character, we replace it with a standard space to avoid crashing
        try:
            val = ord(char)
            if val > 255: val = 32
        except:
            val = 32
            
        send_byte(val)
        time.sleep(BIT_TIME * 2)  # Tiny pause between letters
        
        # Print progress every 10 characters
        if i > 0 and i % 10 == 0:
            print(f"[TX] Sent {i}/{len(text_data)} characters...")
            
    send_byte(0x00) # End of file marker
    GPIO.output(TX_PIN, GPIO.LOW)
    print(f"[TX] Sent {len(text_data)}/{len(text_data)} characters. Done!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", default="message.txt", help="Text file to send")
    args = parser.parse_args()
    
    setup()
    try:
        send_file(args.file)
    finally:
        GPIO.cleanup()
