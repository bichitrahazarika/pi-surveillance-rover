from gpiozero import DigitalOutputDevice, PWMOutputDevice
from config import *

# Direction pins
IN1_PIN = DigitalOutputDevice(IN1)
IN2_PIN = DigitalOutputDevice(IN2)
IN3_PIN = DigitalOutputDevice(IN3)
IN4_PIN = DigitalOutputDevice(IN4)

# PWM pins
ENA_PIN = PWMOutputDevice(ENA)
ENB_PIN = PWMOutputDevice(ENB)

speed = DEFAULT_SPEED


def set_speed(value):
    global speed
    speed = max(0.0, min(1.0, value))


def get_speed():
    return speed


def stop():
    ENA_PIN.value = 0
    ENB_PIN.value = 0

    IN1_PIN.off()
    IN2_PIN.off()
    IN3_PIN.off()
    IN4_PIN.off()


# ==========================
# CORRECTED DIRECTIONS
# ==========================

def forward():
    # Physically moves rover forward
    IN1_PIN.on()
    IN2_PIN.off()

    IN3_PIN.on()
    IN4_PIN.off()

    ENA_PIN.value = speed
    ENB_PIN.value = speed


def backward():
    # Physically moves rover backward
    IN1_PIN.off()
    IN2_PIN.on()

    IN3_PIN.off()
    IN4_PIN.on()

    ENA_PIN.value = speed
    ENB_PIN.value = speed


def left():
    # Turn left
    IN1_PIN.on()
    IN2_PIN.off()

    IN3_PIN.off()
    IN4_PIN.on()

    ENA_PIN.value = speed
    ENB_PIN.value = speed

def right():
    # Turn right
    IN1_PIN.off()
    IN2_PIN.on()

    IN3_PIN.on()
    IN4_PIN.off()

    ENA_PIN.value = speed
    ENB_PIN.value = speed
