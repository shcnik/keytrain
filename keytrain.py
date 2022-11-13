from kivy.app import App
import kivy
import events
from screens import MenuScreen, TrainScreen, SettingsScreen, StatScreen, ResultScreen
from kivy.uix.screenmanager import ScreenManager, NoTransition
from kivy.core.window import Window
import syslog
from functools import partial
import logger


class KeyTrainApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.locale = {}

    def loadloc(self, locale):
        try:
            with open('locale/%s.loc' % locale, 'r') as locfile:
                locfile.readline()
                while True:
                    line = locfile.readline()
                    if line == '':
                        break
                    string, locstring = tuple(line.split('\n')[0].split('#'))
                    self.locale[string] = locstring
        except FileNotFoundError:
            logger.log('Localization %s not found. Default localization will be used.' % locale, 'warn')
            self.locale = {}

    def build_config(self, config):
        config.setdefaults('locale', {
            'lang': 'ru-ru'
        })
        config.setdefaults('tasks', {
            'lang': 'ru-ru',
            'layout': 'ЙЦУКЕН'
        })

    def localize(self, widget):
        if hasattr(widget, 'text'):
            widget.text = self.locale.setdefault(widget.text, widget.text)
        for child in widget.children:
            self.localize(child)

    def build(self):
        config = self.config
        self.loadloc(config.get('locale', 'lang'))
        self.title = 'KeyTrain'
        sm = ScreenManager(transition=NoTransition())
        sm.add_widget(MenuScreen(config, name='Menu'))
        sm.add_widget(TrainScreen(config, name='Train'))
        sm.add_widget(ResultScreen(config, name='Result'))
        sm.add_widget(StatScreen(config, name='Stat'))
        sm.add_widget(SettingsScreen(config, name='Settings'))
        sm.get_screen('Settings').children[0].interface.menu.close_button.on_press = partial(events.exit_settings, sm)
        for scr in sm.screens:
            self.localize(scr)
        Window.borderless = '0'
        sm.current = 'Menu'
        return sm

    def on_config_change(self, instance, config, section, key, value):
        for scr in self.root.screens:
            scr.update(config)


kivy.require('2.1.0')
if __name__ == '__main__':
    KeyTrainApp().run()
 
