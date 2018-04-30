#from jinja2 import Environment, PackageLoader, FileSystemLoader, select_autoescape
from collections import namedtuple
import time
#import sqlite3
from modules.database import DB_NAME


def generate_report():

    Comliances = namedtuple('Compliances', 'ID, desc, info, status')
    print(DB_NAME)
