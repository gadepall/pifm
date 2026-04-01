#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time

RX_PIN   = 23
# SPEED UPGRADE: Must exactly match the transmitter
BIT_TIME = 0.005  

def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(RX_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def read():
    return 0 if GPIO.input(RX_PIN) else 1

def wait_pin(state, timeout=60.0):
    deadline = time.time() + timeout
    while time.time() < deadline:
        if GPIO.input(RX_PIN) == state: return True
        time.sleep(0.0001) # Increased polling resolution for higher speeds
    return False

def receive_byte():
    if not wait_pin(GPIO.LOW, timeout=86400): return -2 
    t = time.time()
    
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
    print("--- High-Speed LiFi Receiver (200 bps) ---")
    print("Waiting for incoming transmission...")
    
    try:
        if not wait_pin(GPIO.LOW, timeout=86400): exit("Timeout.")
        print("Signal detected! Downloading file...")
        if not wait_pin(GPIO.HIGH, timeout=2.0): exit("Preamble failed.")
            
        chars_received = 0
        output_filename = "received_document.txt"
        
        with open(output_filename, "w", encoding='utf-8') as f:
            while True:
                b = receive_byte()
                
                if b == -2 or b == 0x00: break
                if b == -1: continue
                
                if 32 <= b <= 126 or b in [9, 10, 13]:
                    char = chr(b)
                    f.write(char)
                    
                    # Only flush to disk occasionally to prevent SD card lag
                    if chars_received % 20 == 0:
                        f.flush() 
                    
                    chars_received += 1
                    
                    # Only print to terminal every 50 characters so Python doesn't miss bits
                    if chars_received % 50 == 0:
                        print(f"\r[RX] Downloaded: {chars_received} characters...", end="", flush=True)
                
        # (The bug was right here. Removed f.flush() so it doesn't crash after closing!)
        print(f"\n\n✅ SUCCESS! Saved {chars_received} characters to '{output_filename}'.")
        
    finally:
        GPIO.cleanup()
