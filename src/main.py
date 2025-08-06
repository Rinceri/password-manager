from textual.app import App

from controller.screen_controller import ScreenController


class MainApp(App):

    def on_mount(self):
        ScreenController(self).push_login()


if __name__ == "__main__":
    app = MainApp()
    app.run()
