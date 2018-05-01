import os
import sqlite3
import sys
from collections import namedtuple, Counter

from jinja2 import Environment, FileSystemLoader, select_autoescape
import pdfkit

from modules.database import DB_NAME
from modules.transports import get_config
from modules.time import get_start_time, get_finish_time, get_duration
from modules.statuses import get_status_name


TEMPLATE_HTML = os.path.join('templates', 'index.html')
CSS_FILE = os.path.join('templates', 'style.css')
ENV = get_config()


def render(tpl_path, context):
    path, filename = os.path.split(tpl_path)
    return Environment(
        loader=FileSystemLoader(path or './'),
        autoescape=select_autoescape(['html', 'xml'])
    ).get_template(filename).render(context)


def get_context():
    context = dict()
    Transport = namedtuple('Transport', 'name, password, login, port')
    transports = [Transport(name, param['password'], param['login'], param['port'])
                            for name, param in ENV['transports'].items()]
    context.update({'host': ENV['host']})
    context.update({'transports': transports})

    context.update({'start_time': get_start_time()})
    context.update({'finish_time': get_finish_time()})
    context.update({'duration': get_duration()})

    with sqlite3.connect(DB_NAME) as db:
        curr = db.cursor()
        Control = namedtuple('Control',
                            'ID, title, description,\
                            requirement, system, status')
        # Это кошмар, я понимаю, но понятия не имею, как сделать качественнее
        # Или имеет смысл заполнять последовательно, а не за 1 проход в 1 строку?
        raw_controls = curr.execute("""SELECT * FROM scandata INNER JOIN
                control ON scandata.ctrl_id = control.id""").fetchall()
        raw_controls = [(c[1],)+c[4:7]+(c[5+c[2]], get_status_name(c[2])) for c in raw_controls]
        controls = [Control(ID, title, description, requirement, system, status) for
                ID, title, description, requirement, system, status in raw_controls]

    context.update({'total_controls': len(controls)})
    context.update({'controls': controls})
    context.update({'statuses': {get_status_name(code): 0 for code in range(1,6)}})
    context['statuses'].update(dict(Counter([control.status
                for control in controls])))
    return context


def generate_report(report_name):
    rendered = render(TEMPLATE_HTML, get_context())
    pdfkit.from_string(rendered, report_name, css=CSS_FILE)
