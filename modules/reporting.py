import os
import sqlite3
import sys
from collections import namedtuple

from jinja2 import Environment, FileSystemLoader, select_autoescape
from weasyprint import HTML

from modules.database import DB_NAME
from modules.transports import get_config
from modules.time import get_start_time, get_finish_time, get_duration


TEMPLATE_HTML = os.path.join('templates', 'index.html')
TEMPLATE_CSS = os.path.join('templates', 'style.css')
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
        total_controls = len(curr.execute('select * from control').fetchall())
        Compliance = namedtuple('Compliance',
                                'ID, title, description, status')
        # Это кошмар, я понимаю, но понятия не имею, как сделать качественнее
        # Вложенные запросы?
        compliances = [Compliance(ID, *curr.execute('select * from control where id={}'
                .format(control_id)).fetchone()[1:], status) for ID, control_id, status
                in curr.execute('select * from scandata').fetchall()]
    context.update({'total_controls': total_controls})
    context.update({'compliances': compliances})
    return context


def generate_report(report_name):
    rendered = render(TEMPLATE_HTML, get_context())
    document = HTML(string=rendered).render()
    document.write_pdf(report_name)
