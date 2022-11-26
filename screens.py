import syslog

from kivy.uix.screenmanager import Screen
from kivy.core.window import Window

import events
from trainer import Trainer
from kivy.config import ConfigParser
from kivy.uix.settings import Settings
from kivy.app import App
from kivy.graphics import Rectangle, Line, Color
from kivy.uix.label import Label
from functools import partial
from stats import InvalidLayoutException
import os
import csv
import logger


class MenuScreen(Screen):
    def __init__(self, config, **kwargs):
        super().__init__(**kwargs)
        self.__animate = False

    def enter(self):
        Window.size = (400, 300)
        Window.set_title('KeyTrain')

    def update(self, config):
        pass


class TrainScreen(Screen):
    def __init__(self, config, **kwargs):
        super().__init__(**kwargs)
        self.trainer = Trainer(config.get('tasks', 'lang'))
        self.training = False

    def update(self, config):
        self.trainer = Trainer(config.get('tasks', 'lang'))

    def enter(self):
        Window.size = (800, 500)
        self.ids['time_lbl'].text = '0:00'
        self.ids['speed_lbl'].text = '0.0'
        self.ids['error_lbl'].text = '0.0%'


class StatScreen(Screen):
    def __init__(self, config, **kwargs):
        super().__init__(**kwargs)

    def update(self, config):
        pass

    def enter(self):
        Window.size = (800, 800)
        self.ids['table'].clear_widgets()
        try:
            with open('stats.csv', 'r', newline='') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        self.ids['table'].add_widget(
                            Label(text=row['time'], font_size='20pt', size_hint_x=None, width=800, halign='left'))
                        self.ids['table'].add_widget(
                            Label(text="%.1f" % float(row['speed']), font_size='20pt', size_hint_x=None, width=400,
                                  halign='center'))
                        self.ids['table'].add_widget(
                            Label(text="{:.2%}".format(float(row['errate'])), font_size='20pt', size_hint_x=None,
                                  width=400, halign='center'))
                    except KeyError:
                        continue
        except FileNotFoundError:
            with open('stats.csv', 'w', newline='') as f:
                logger.log('Statistics file not found. Empty one was created.', 'warn')
                writer = csv.DictWriter(f, fieldnames=['time', 'speed', 'errate'])
                writer.writeheader()


class SettingsScreen(Screen):
    def __generate_json(self):
        return ('''
[
  {
    "type": "title",
    "title": "Localization"
  },
  {
    "type": "options",
    "title": "App language",
    "desc": "Set the language used by KeyTrain",
    "section": "locale",
    "key": "lang",
    "options": %s
  },
  {
    "type": "title",
    "title": "Tasks"
  },
  {
    "type": "options",
    "title": "Task language",
    "desc": "Set the language used in tasks",
    "section": "tasks",
    "key": "lang",
    "options": %s
  },
  {
    "type": "options",
    "title": "Keyboard layout",
    "desc": "Set the layout you are using",
    "section": "tasks",
    "key": "layout",
    "options": %s
  }
]
        ''' % (str(list(map(lambda locale: locale[:-4], os.listdir('locale')))),
               str(list(map(lambda task: task[:-5], os.listdir('tasks')))),
               str(list(map(lambda layout: layout[:-7], os.listdir('layout')))))).replace("'", '"')

    def __init__(self, config, **kwargs):
        super().__init__(**kwargs)
        config = ConfigParser()
        config.read('keytrain.ini')
        self.set = Settings()
        self.set.add_json_panel('Settings', config, data=self.__generate_json())
        self.set.bind(on_config_change=App.get_running_app().on_config_change)
        self.on_enter = self.enter
        self.add_widget(self.set)
        for setting in self.set.children[0].children[0].children[0].children[0].children:
            if len(setting.children) == 0:
                continue
            lines = setting.children[0].children[1].text.split('\n')
            lines[1] = lines[1][25:-15]
            setting.children[0].children[1].text = "{0}\n[size=13sp][color=999999]{1}[/color][/size]".format(
                App.get_running_app().locale.setdefault(lines[0], lines[0]),
                App.get_running_app().locale.setdefault(lines[1], lines[1]))

    def enter(self):
        self.set.bind(on_close=partial(events.exit_settings, self.manager))
        Window.size = (800, 800)

    def update(self, config):
        pass


class ResultScreen(Screen):
    def __init__(self, config, **kwargs):
        super().__init__(**kwargs)
        self.normkeys = [''] * 4
        self.shiftkeys = [''] * 4
        self.keylayout = config.get('tasks', 'layout')
        try:
            with open('layout/%s.layout' % self.keylayout, 'r') as f:
                for i in range(0, 4):
                    self.normkeys[i] = f.readline()
                for i in range(0, 4):
                    self.shiftkeys[i] = f.readline()
        except FileNotFoundError:
            logger.log('Layout %s not found.' % self.keylayout, 'error')

    def update(self, config):
        self.keylayout = config.get('tasks', 'layout')
        try:
            with open('layout/%s.layout' % self.keylayout, 'r') as f:
                for i in range(0, 4):
                    self.normkeys[i] = f.readline()
                for i in range(0, 4):
                    self.shiftkeys[i] = f.readline()
        except FileNotFoundError:
            logger.log('Layout %s not found.' % self.keylayout, 'error')

    def __draw_key(self, x, y, w, h, lchar, hchar, heat=-1):
        with self.canvas:
            if heat >= 0:
                Color(120 / 360 * (1.0 - heat), 1.0, 0.7, mode='hsv')
                Rectangle(size=(w, h), pos=(x, y))
            Color(0.0, 0.0, 1.0, mode='hsv')
            Line(points=[x, y, x + w, y, x + w, y + h, x, y + h, x, y], width=5)
        keychars = Label(size=(w - 5, h - 5), pos=(x - 2.5 - 755, y - 2.5 - 355),
                         halign='center', valign='center')
        if (lchar.upper() == hchar) or (lchar == hchar):
            keychars.text = hchar
            keychars.font_size = '%dpx' % (h // 2)
        else:
            keychars.text = '{0}\n{1}'.format(hchar, lchar)
            keychars.font_size = '%dpx' % (h // 3)
        self.add_widget(keychars)

    def __draw_keyboard(self, heatmap):
        for i in range(0, 13):
            self.__draw_key(200 + 80 * i, 450, 80, 80,
                            self.normkeys[0][i], self.shiftkeys[0][i],
                            heatmap.setdefault(self.normkeys[0][i], 0) + heatmap.setdefault(self.shiftkeys[0][i], 0))
        self.__draw_key(1240, 450, 160, 80, 'back︎', '')
        self.__draw_key(200, 370, 120, 80, 'tab', '')
        for i in range(0, 12):
            self.__draw_key(320 + 80 * i, 370, 80, 80, self.normkeys[1][i], self.shiftkeys[1][i],
                            heatmap.setdefault(self.normkeys[1][i], 0) + heatmap.setdefault(self.shiftkeys[1][i], 0))
        self.__draw_key(1280, 370, 120, 80, self.normkeys[1][12], self.shiftkeys[1][12],
                        heatmap.setdefault(self.normkeys[1][i], 0) + heatmap.setdefault(self.shiftkeys[1][i], 0))
        self.__draw_key(200, 290, 160, 80, 'caps', '')
        for i in range(0, 11):
            self.__draw_key(360 + 80 * i, 290, 80, 80, self.normkeys[2][i], self.shiftkeys[2][i],
                            heatmap.setdefault(self.normkeys[2][i], 0) + heatmap.setdefault(self.shiftkeys[2][i], 0))
        self.__draw_key(1240, 290, 160, 80, 'enter', '')
        self.__draw_key(200, 210, 200, 80, 'shift', '')
        for i in range(0, 10):
            self.__draw_key(400 + 80 * i, 210, 80, 80, self.normkeys[3][i], self.shiftkeys[3][i],
                            heatmap.setdefault(self.normkeys[3][i], 0) + heatmap.setdefault(self.shiftkeys[3][i], 0))
        self.__draw_key(1200, 210, 200, 80, 'shift', '')
        self.__draw_key(570, 130, 400, 80, ' ', ' ',
                        heatmap.setdefault(self.normkeys[0][i], 0) + heatmap.setdefault(self.shiftkeys[0][i], 0))

    def enter(self):
        Window.size = (800, 400)
        stats = self.manager.get_screen('Train').trainer.stat.get_stats()
        self.ids['time_lbl'].text = '{:1d}:{:02d}'.format(stats['time'] // 60, stats['time'] % 60)
        self.ids['speed_lbl'].text = '{:.1f}'.format(stats['speed'])
        self.ids['error_lbl'].text = '{:.1%}'.format(stats['errate'])
        heatmap = {}
        try:
            heatmap = self.manager.get_screen('Train').trainer.stat.get_heatmap(self.keylayout)
        except InvalidLayoutException as ex:
            logger.log('%s. Layout not loaded.' % ex.msg, 'error')
        self.__draw_keyboard(heatmap)
