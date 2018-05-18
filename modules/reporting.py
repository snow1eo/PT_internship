import os
import sqlite3
from base64 import b64decode
from collections import namedtuple, Counter
from datetime import datetime

from jinja2 import Environment, FileSystemLoader, select_autoescape
from weasyprint import HTML, CSS

from modules.database import DB_NAME, get_scan_id
from modules.statuses import Status
from modules.transports import get_host_name, get_transport_names

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
    Control = namedtuple('Control',
                         'ID, title, description, requirement, prescription, status, error')
    Transport = namedtuple('Transport', 'name, user, port')
    Audit = namedtuple('Audit', 'attribute, value')
    with sqlite3.connect(DB_NAME) as db:
        curr = db.cursor()
        scan_id = get_scan_id()
        audit = {prot: [Audit(attribute, b64decode(value).decode()) for attribute, value in
                        curr.execute("""SELECT attribute, value FROM audit
                                 WHERE scan_id = ? and protocol = ?""", (scan_id, prot))]
                 for prot in get_transport_names()}
        transports = [Transport(name, user, port) for name, user, port in
                      curr.execute("SELECT name, user, port FROM transport WHERE scan_id = ?", (scan_id,))]
        controls = [Control(ID, title, desc, requir, presc, Status(code).name, error) for
                    ID, title, desc, requir, presc, code, error in
                    curr.execute("""SELECT scandata.id, control.title,
                        control.description, control.requirement, control.prescription,
                        scandata.status, scandata.error FROM scandata INNER JOIN
                        control ON scandata.ctrl_id = control.id AND
                        scandata.scan_id = ?""", (scan_id,)).fetchall()]
        start_time, finish_time = map(
            lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M:%S.%f"),
            curr.execute("""SELECT start, finish FROM
                    scanning WHERE id = ?""", (scan_id,)).fetchone())
    statuses_count = {Status(code).name: 0 for code in range(1, 6)}
    statuses_count.update(dict(Counter([control.status for control in controls])))
    return dict(
        host=get_host_name(),
        audit=audit,
        transports=transports,
        start_time=start_time.strftime(TIME_FORMAT),
        finish_time=finish_time.strftime(TIME_FORMAT),
        duration=finish_time - start_time,
        total_controls=len(controls),
        controls=controls,
        statuses=statuses_count)


def generate_report(report_name):
    rendered = render(TEMPLATE_HTML, get_context())
    doc = HTML(string=rendered)
    wcss = CSS(filename=CSS_FILE)
    doc.write_pdf(report_name, stylesheets=[wcss])
