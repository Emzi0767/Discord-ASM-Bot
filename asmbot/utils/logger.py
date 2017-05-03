import datetime
import traceback
import os


def log(*messages, **kwargs):
    ts = datetime.datetime.now(datetime.timezone.utc)
    ts = ts.strftime("%Y-%m-%d %H:%M:%S %z")

    tg = kwargs.get("tag", "STDOUT    ")
    if len(tg) > 10:
        tg = tg[0:10]
    elif len(tg) < 10:
        tg += " " * (10 - len(tg))

    pid = os.getpid()

    prefix = "[{}] [PID {:05}] [{}] ".format(ts, pid, tg)

    msgs = [s for s in "\n".join(messages).split("\n") if len(s.strip()) > 0]

    for msg in msgs:
        print("{}{}".format(prefix, msg))


def logex(exception: Exception, **kwargs):
    extype = type(exception)
    value = exception
    tback = exception.__traceback__
    exinfo = (extype, value, tback)

    exfmts = [s.replace("\\n", "") for s in traceback.format_exception(*exinfo)]

    log(*exfmts, **kwargs)
