import syslog


levels = {'error': 'ERROR', 'warn': 'WARNING', 'note': 'INFO'}


def log(msg, level):
    global levels
    msgline = '[%s] %s' % (levels[level], msg)
    print(msgline)
    syslog.syslog(msgline)
