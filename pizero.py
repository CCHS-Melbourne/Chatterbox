from shared import run
from gpiozero import Button


def main():
    button = Button(26, bounce_time=0.1)

    def is_pressed():
        return button.is_pressed

    def wait_for_press():
        button.wait_for_press()

    run(is_pressed, wait_for_press)


if __name__ == "main":
    main()
