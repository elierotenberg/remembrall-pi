#!/bin/sh
GPIOZERO_PIN_FACTORY=pigpio PIGPIO_ADDR=$(dig +short remembrall.local) poetry run python -m app.check_device
