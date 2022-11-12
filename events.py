import csv
from kivy.core.window import Window
from stats import Statistics
from kivy.clock import Clock
from functools import partial


def quit_menu():
    Window.close()


def start(scr):
    scr.manager.current = 'Train'


def settings(scr):
    scr.manager.current = 'Settings'


def stats(scr):
    scr.manager.current = 'Stat'


def quit_train(scr):
    train_finish(scr)
    scr.manager.current = 'Menu'


def start_train(scr):
    scr.ids['task_label'].text = scr.trainer.get_task()
    update(scr)
    Statistics.length = len(scr.trainer.curtask)
    scr.ids['task_input'].disabled = False
    scr.training = True
    Clock.schedule_interval(partial(update, scr), 1.0)
    scr.keyboard = Window.request_keyboard(None, scr, 'text')
    scr.keyboard.bind(on_key_up=partial(key_up, scr))
    scr.ids['start_btn'].disabled = True
    scr.ids['task_input'].focus = True


def text_check(scr):
    if scr.trainer.is_finish() and scr.ids['task_input'].text != '':
        train_finish(scr)


def input_check(to_add, undo):
    if undo:
        return ''
    if len(to_add) != 1:
        return ''
    train = Window.children[0].get_screen('Train').trainer
    res = train.check_sym(to_add)
    if not res:
        return ''
    return to_add


def train_finish(scr, *args):
    scr.training = False
    scr.ids['start_btn'].disabled = False
    scr.keyboard.unbind(on_key_up=partial(key_up, scr))
    scr.ids['task_input'].disabled = True
    scr.ids['task_input'].text = ''
    scr.trainer.stat.save_to('stats.csv')
    scr.manager.current = 'Result'


def exit_settings(sm, *args):
    sm.current = 'Menu'


def update(scr, *args):
    stats = scr.trainer.stat.get_stats()
    scr.ids['speed_lbl'].text = '{:.1f}'.format(
        (scr.trainer.curpos / stats['time'] * 60) if stats['time'] != 0 else 0)
    scr.ids['error_lbl'].text = '{:.1%}'.format(
        (stats['errors'] / stats['press']) if stats['press'] != 0 else 0)
    scr.ids['time_lbl'].text = '{:1d}:{:02d}'.format(stats['time'] // 60, stats['time'] % 60)


def key_up(scr, keycode, key):
    if key[1] == 'backspace':
        scr.trainer.back()
    update(scr)


def repeat(scr):
    scr.manager.current = 'Train'


def menu(scr):
    scr.manager.current = 'Menu'

def clear_stat(scr):
    with open('stats.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['time', 'speed', 'errate'])
        writer.writeheader()
    scr.ids['table'].clear_widgets()