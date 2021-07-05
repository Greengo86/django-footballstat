import logging
import time
from stats_parser.celery_tasks import app


@app.task
def send_print(arg):
    logging.warning("Send Down")
    print(arg)
    with open('helloworld.txt', 'a+') as filehandle:
        filehandle.write('\n' + 'Hello, world!' + time.strftime("%c", time.localtime()) + '\n')
