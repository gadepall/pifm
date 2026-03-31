import RPi.GPIO as GPIO
import time

RX_PIN = 23

GPIO.setmode(GPIO.BCM)
# Using PUD_UP just in case you removed your physical pull-up resistor
GPIO.setup(RX_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

print("--- Receiver Monitor Test ---")
print("Reading the raw pin state...")

try:
    while True:
        state = GPIO.input(RX_PIN)
        if state == 1:
            print("Pin State: 1 (HIGH)")
        else:
            print("Pin State: 0 (LOW)")
            
        time.sleep(0.1) # Read it 10 times a second
        
except KeyboardInterrupt:
    print("\nStopping.")
finally:
    GPIO.cleanup()
