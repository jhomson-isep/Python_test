# -*- coding: utf-8 -*-
from sqlachemy_conn import *
from dotenv import load_dotenv, find_dotenv
from sqlalchemy import and_
from connect_postgresql import PSQL
import logging
import pandas as pd

session_pg = get_pg_session()
faculties = None
logger = logging.getLogger(__name__)
logger.warning("Start up script import relation faculties subjects")
with open('All_faculties.csv', 'r') as csv_file:
    faculties = pd.read_csv(csv_file, names=['DNI', 'EMAIL', 'Codigo_Asignatura'])

for o, row in faculties.iterrows():
    try:
        DNI = row.DNI.split("/")
        op_faculty = None
        res_partner = None
        for op_dni in DNI:
            op_faculty = session_pg.query(OpFaculty).\
                            filter(OpFaculty.nifp == op_dni).first()
        if op_faculty is None:
            res_partner = session_pg.query(ResPartner).\
                            filter(ResPartner.email == row.EMAIL).first()
        if res_partner is None:
            logger.warning("Faculty with DNI's %s not exist!!" % DNI)
            continue
        else:
            op_faculty = session_pg.query(OpFaculty).\
                            filter(OpFaculty.partner_id == res_partner.id).first()
        op_subject = session_pg.query(OpSubject).\
                        filter(OpSubject.code == row.Codigo_Asignatura).first()
        if op_subject is None:
            logger.warning("Subject code %s not exist!!" % row.Codigo_Asignatura)
            continue
        pg_sql = PSQL()
        op_faculty_op_subject_rel = pg_sql.get_subject_faculty_id_rel(op_faculty.id, op_subject.id)
        if op_faculty_op_subject_rel is None:
            pg_sql.create_subject_faculty_rel([op_faculty.id, op_subject.id])
            logger.warning("Faculty relation created nifp %s" % op_faculty.nifp)
        else:
            logger.warning("Faculty relation exist nifp %s" % op_faculty.nifp)
    except Exception as e:
        logger.warning(e)
logger.warning("End of script import relation faculties subjects")


