from jinja2 import Environment, PackageLoader, FileSystemLoader, select_autoescape
from collections import namedtuple
import sqlite3
from modules.database import db_name

def generate_report():
    Comliances = namedtuple('Compliances', 'ID, desc, info, status')
    print(db_name)