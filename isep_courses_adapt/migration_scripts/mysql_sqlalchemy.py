from dotenv import load_dotenv, find_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import Table, MetaData
from sqlalchemy.ext.declarative import declarative_base
import os

# MYSQL Connection
Base_mysql = declarative_base()
dbname = os.environ['MYSQL_DATABASE']
user = os.environ['MYSQL_USER']
password = os.environ['MYSQL_PASSWORD']
host = os.environ['MYSQL_HOST']
port = os.environ['MYSQL_PORT']

mysql = create_engine('mysql+mysqlconnector://{0}:{1}@{2}:{3}/{4}'.format(
    user, password, host, port, dbname))

metadata_mysql = MetaData(bind=mysql)


# MYSQL Tables
class MdlAttendanceSession(Base_mysql):
    __table__ = Table('mdl_attendance_sessions', metadata_mysql, autoload=True)


class MdlAttendance(Base_mysql):
    __table__ = Table('mdl_attendance', metadata_mysql, autoload=True)


class MdlGroups(Base_mysql):
    __table__ = Table('mdl_groups', metadata_mysql, autoload=True)


class MdlUser(Base_mysql):
    __table__ = Table('mdl_user', metadata_mysql, autoload=True)


class MdlAttendanceLog(Base_mysql):
    __table__ = Table('mdl_attendance_log', metadata_mysql, autoload=True)


class MdlAttendanceStatuses(Base_mysql):
    __table__ = Table('mdl_attendance_statuses', metadata_mysql, autoload=True)


def get_mysql_session():
    Session_mysql = sessionmaker()
    Session_mysql.configure(bind=mysql)
    return Session_mysql()
