import random
from stats import Statistics


class Trainer:
    def __init__(self, taskfile):
        self.__gen = random.Random()
        self.tasks = []
        self.curtask = ''
        self.curpos = -1
        self.stat = Statistics()
        with open("tasks/%s.task" % taskfile, 'r') as task:
            while True:
                line = task.readline()
                if line == '':
                    break
                self.tasks.append(line)

    def get_task(self):
        self.curtask = self.tasks[self.__gen.randint(0, len(self.tasks) - 1)]
        self.curpos = 0
        self.stat.start(len(self.curtask))
        return self.curtask

    def back(self):
        self.curpos -= 1
        self.stat.fix_input()
        self.stat.fix_error(chr(8))

    def check_sym(self, sym):
        self.stat.fix_input()
        if self.curpos >= len(self.curtask):
            return False
        if self.curtask[self.curpos] == sym:
            self.curpos += 1
            return True
        self.stat.fix_error(self.curtask[self.curpos])
        return False

    def is_finish(self):
        if self.curpos >= len(self.curtask):
            self.stat.stop()
            return True
        return False
