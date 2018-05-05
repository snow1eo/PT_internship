import os
import sqlite3
from collections import namedtuple, Counter
from datetime import datetime

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


def get_context():
    env = get_transport_config()

    Control = namedtuple('Control', 'ID, title, description, requirement, status')
    Transport = namedtuple('Transport', 'name, password, login, port')
    transports = [Transport(name, param['password'], param['login'], param['port'])
                  for name, param in env['transports'].items()]

    with sqlite3.connect(DB_NAME) as db:
        curr = db.cursor()
        scan_id = curr.execute("SELECT seq FROM sqlite_sequence WHERE name='scanning'").fetchone()[0]
        controls = [Control(ID, title, desc, requir, Status(code).name) for
                    ID, title, desc, requir, code in
                    curr.execute("""SELECT scandata.id, control.title,
                        control.description, control.requirement,
                        scandata.status FROM scandata INNER JOIN control
                        ON scandata.ctrl_id = control.id AND
                        scandata.scan_id = ?""", (scan_id,)).fetchall()]
        start_time, finish_time = map(
                lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M:%S.%f"),
                curr.execute("""SELECT start, finish FROM
                    scanning WHERE id = ?""", (scan_id,)).fetchone())

    statuses_count = {Status(code).name: 0 for code in range(1, 6)}
    statuses_count.update(dict(Counter([control.status for control in controls])))

    context = dict(
        host=env['host'],
        transports=transports,
        start_time=start_time.strftime(TIME_FORMAT),
        finish_time=finish_time.strftime(TIME_FORMAT),
        duration=finish_time-start_time,
        total_controls=len(controls),
        controls=controls,
        statuses=statuses_count)
    return context


def generate_report(report_name):
    rendered = render(TEMPLATE_HTML, get_context())
    doc = HTML(string=rendered)
    wcss = CSS(filename=CSS_FILE)
    doc.write_pdf(report_name, stylesheets=[wcss])
