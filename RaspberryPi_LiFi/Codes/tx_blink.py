import RPi.GPIO as GPIO
import time

TX_PIN = 18

GPIO.setmode(GPIO.BCM)
GPIO.setup(TX_PIN, GPIO.OUT)

print("--- Transmitter Blink Test ---")
print("Flashing IR LED every 2 seconds...")

try:
    while True:
        print("[TX] Turning LED: ON")
        GPIO.output(TX_PIN, GPIO.HIGH)
        time.sleep(2)
        
        print("[TX] Turning LED: OFF")
        GPIO.output(TX_PIN, GPIO.LOW)
        time.sleep(2)
        
except KeyboardInterrupt:
    print("\nStopping.")
finally:
    GPIO.output(TX_PIN, GPIO.LOW)
    GPIO.cleanup()
