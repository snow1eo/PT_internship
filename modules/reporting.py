import os
import sqlite3
from collections import namedtuple, Counter

# import pdfkit
from weasyprint import HTML, CSS
from jinja2 import Environment, FileSystemLoader, select_autoescape

from modules.database import DB_NAME
from modules.statuses import get_status_name
from modules.time import get_start_time, get_finish_time, get_duration
from modules.transports import get_config

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
                             'ID, title, description, requirement, status')
        controls = [Control(ID, title, desc, requir, get_status_name(code)) for
                    ID, title, desc, requir, code in
                    curr.execute("""SELECT scandata.id, control.title,
                        control.description, control.requirement,
                        scandata.status FROM scandata INNER JOIN control
                        ON scandata.ctrl_id = control.id""").fetchall()]
    context.update({'total_controls': len(controls)})
    context.update({'controls': controls})
    context.update({'statuses': {get_status_name(code): 0 for code in range(1,6)}})
    context['statuses'].update(dict(Counter([control.status for control in controls])))
    return context


def generate_report(report_name):
    rendered = render(TEMPLATE_HTML, get_context())
    doc = HTML(string=rendered)
    wcss = CSS(filename=CSS_FILE)
    doc.write_pdf(report_name, stylesheets=[wcss])

    # pdfkit.from_string(rendered, report_name, css=CSS_FILE)
