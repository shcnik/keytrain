import csv
import datetime
import os


class InvalidLayoutException(Exception):
    def __init__(self, msg, *args):
        super().__init__(*args)
        self.msg = msg


class Statistics:
    def __init__(self):
        self.__length = 0
        self.__time = -1
        self.__errors = 0
        self.__keyerrs = {}
        self.__starttime = 0
        self.__progress = False
        self.__press = 0

    def start(self, length):
        self.clear()
        self.__length = length
        self.__starttime = datetime.datetime.now().timestamp()
        self.__progress = True

    def fix_error(self, corrkey):
        self.__errors += 1
        self.__keyerrs.setdefault(corrkey, 0)
        self.__keyerrs[corrkey] += 1

    def stop(self):
        self.__time = datetime.datetime.now().timestamp() - self.__starttime
        self.__progress = False

    def fix_input(self):
        self.__press += 1

    def get_stats(self):
        if self.__progress:
            self.__time = datetime.datetime.now().timestamp() - self.__starttime
        return {'time': int(self.__time), 'length' : self.__length, 'length': self.__length,
                'speed': (self.__length / self.__time * 60.0) if self.__time != 0 else 0,
                'errate': (self.__errors / self.__press) if self.__press != 0 else 0,
                'errors': self.__errors, 'press': self.__press}

    def get_heatmap(self, layout):
        keymap = {}
        try:
            with open('layout/%s.layout' % layout, 'r') as f:
                for row in [13, 13, 11, 10, 13, 13, 11, 10]:
                    line = f.readline()
                    keymap.update(zip(list(line[:row]), list(line[:row].upper())))
        except FileNotFoundError:
            raise InvalidLayoutException('Layout %s not found' % layout)
        except IndexError:
            raise InvalidLayoutException('Not all keys defined for layout %s' % layout)
        heatmap = {}
        for key in keymap:
            heatmap.setdefault(keymap[key], 0)
            heatmap[keymap[key]] += (self.__keyerrs.setdefault(key, 0) / self.__errors) if self.__errors != 0 else 0
        return heatmap

    def save_to(self, filename):
        fields = ['time', 'speed', 'errate']
        if filename not in os.listdir('.'):
            with open(filename, 'w', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=fields)
                writer.writeheader()
        with open(filename, 'a', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fields)
            writer.writerow({'time': datetime.datetime.now().isoformat(sep=' ', timespec='minutes'),
                             'speed': self.__length / self.__time * 60.0,
                             'errate': self.__errors / self.__length})

    def clear(self):
        self.__length = 0
        self.__time = -1
        self.__errors = 0
        self.__keyerrs = {}
        self.__progress = False
