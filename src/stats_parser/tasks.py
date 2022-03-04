from . import parser
from stats_parser.celery_tasks import app


@app.task
def go_parse(arg: str):
    parser.main(arg)
    return True
