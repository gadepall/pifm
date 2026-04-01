#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time

RX_PIN   = 23
BIT_TIME = 0.05  # 20 bps

def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(RX_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def read():
    # In this circuit, Light ON pulls the pin LOW (0V). 
    # We return 1 to represent the light is ON.
    return 0 if GPIO.input(RX_PIN) else 1

def wait_pin(state, timeout=60.0):
    deadline = time.time() + timeout
    while time.time() < deadline:
        if GPIO.input(RX_PIN) == state: return True
        time.sleep(0.001)
    return False

def receive_byte():
    # Wait for light to turn ON (Pin goes LOW)
    if not wait_pin(GPIO.LOW, timeout=10.0): return -2
    t = time.time()
    
    # Confirm it wasn't a random flicker
    time.sleep(BIT_TIME * 0.5)
    if read() != 1: return -1
        
    byte_val = 0
    for i in range(8):
        target = t + BIT_TIME * (i + 1.5)
        gap = target - time.time()
        if gap > 0: time.sleep(gap)
        bit = read()
        byte_val |= (bit << i)
        
    target = t + BIT_TIME * 10.5
    gap = target - time.time()
    if gap > 0: time.sleep(gap)
        
    return byte_val

if __name__ == "__main__":
    setup()
    print("--- LiFi Text Receiver ---")
    print("Waiting for signal...")
    
    try:
        if not wait_pin(GPIO.LOW, timeout=60.0): exit("Timeout.")
        print("Signal detected! Downloading...")
        if not wait_pin(GPIO.HIGH, timeout=5.0): exit("Preamble failed.")
            
        message = ""
        while True:
            b = receive_byte()
            if b == -2 or b == 0x00: break
            if b == -1: continue
            
            if 32 <= b <= 126:
                print(f"Got: '{chr(b)}'")
                message += chr(b)
                
        print(f"\nFINAL MESSAGE: {message}")
        
    finally:
        GPIO.cleanup()
