from shared import run
from gpiozero import Button, LED

def main():
    button = Button(26, bounce_time=0.1)
    led0=LED(22)
    led1=LED(27)
    led2=LED(17)
    leds=[led0,led1,led2]

    def led_update(led,status):
        if status=='off':
            led.off()
        elif status=='on':
            led.on()
        elif status=='blink':
            led.blink(on_time=0.5, off_time=0.5)
    
    def is_pressed():
        return button.is_pressed

    def wait_for_press():
        button.wait_for_press()

    run(is_pressed, wait_for_press, leds, led_update)


if __name__ == "__main__":
    main()
