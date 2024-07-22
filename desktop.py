from shared import run
import keyboard  # Added for keyboard input


def main():
    def is_pressed():
        return keyboard.is_pressed("space")

    def wait_for_press():
        keyboard.wait("space")

    run(is_pressed, wait_for_press)


if __name__ == "__main__":
    main()
