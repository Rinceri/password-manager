from textual.app import App
import argparse

from texpass.controller.screen_controller import ScreenController


class MainApp(App):

    def on_mount(self):
        ScreenController(self).push_login()


def main():
    """
    Creates the App and runs it
    """
    from texpass import setup_app
    from texpass import setup_cloud

    setup_app.setup_database()

    parser = argparse.ArgumentParser(description="TUI Password manager")

    parser.add_argument('-c', '--cloud', action="store_true")
    args = parser.parse_args()

    if args.cloud:
        setup_cloud.main()
    else:
        app = MainApp()
        app.run()

if __name__ == "__main__":
    main()
