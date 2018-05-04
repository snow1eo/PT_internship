import os
import sqlite3
from collections import namedtuple, Counter
from typing import NamedTuple

from jinja2 import Environment, FileSystemLoader, select_autoescape
from weasyprint import HTML, CSS

from modules.database import DB_NAME
from modules.statuses import Status
from modules.transports import get_transport_config

TEMPLATE_HTML = os.path.join('templates', 'index.html')
CSS_FILE = os.path.join('templates', 'style.css')
TIME_FORMAT = "%Y.%m.%d %H:%M:%S"


def render(tpl_path, context):
    path, filename = os.path.split(tpl_path)
    return Environment(
        loader=FileSystemLoader(path or './'),
        autoescape=select_autoescape(['html', 'xml'])
    ).get_template(filename).render(context)


def get_context(start_time, finish_time):
    env = get_transport_config()
    duration = finish_time - start_time

    class Control(NamedTuple):
        ID = None
        title = None
        description = None
        requirement = None
        status = None
    Transport = namedtuple('Transport', 'name, password, login, port')
    transports = [Transport(name, param['password'], param['login'], param['port'])
                            for name, param in env['transports'].items()]

    with sqlite3.connect(DB_NAME) as db:
        curr = db.cursor()
        controls = [Control(ID, title, desc, requir, Status(code).name) for
                    ID, title, desc, requir, code in
                    curr.execute("""SELECT scandata.id, control.title,
                        control.description, control.requirement,
                        scandata.status FROM scandata INNER JOIN control
                        ON scandata.ctrl_id = control.id""").fetchall()]
    statuses_count = {Status(code).name: 0 for code in range(1, 6)}
    statuses_count.update(dict(Counter([control.status for control in controls])))

    context = dict(
        host=env['host'],
        transports=transports,
        start_time=start_time.strftime(TIME_FORMAT),
        finish_time=finish_time.strftime(TIME_FORMAT),
        duration=duration,
        total_controls=len(controls),
        controls=controls,
        statuses=statuses_count)
    return context


def generate_report(report_name, start_time, finish_time):
    rendered = render(TEMPLATE_HTML, get_context(start_time, finish_time))
    doc = HTML(string=rendered)
    wcss = CSS(filename=CSS_FILE)
    doc.write_pdf(report_name, stylesheets=[wcss])
