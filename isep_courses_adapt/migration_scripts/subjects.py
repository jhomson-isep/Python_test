# -*- coding: utf-8 -*-
from sqlachemy_conn import *
import logging

session_pg = get_pg_session()
session_server = get_session_server_isep()

subjects = session_server.query(IsepAsignaturas).all()

logger = logging.getLogger(__name__)

logger.warning("Start up script subjects import")
for subject in subjects:
    op_subject = session_pg.query(OpSubject).\
                filter(OpSubject.code == subject.CodAsignatura).first()
    if op_subject is None:
        op_subject = OpSubject()
        op_subject.name = subject.NomAsignatura
        op_subject.code = subject.CodAsignatura
        op_subject.type = 'theory'
        op_subject.subject_type = 'compulsory'
        op_subject.uvic_code = subject.CodUvic
        op_subject.moodle_course_id = subject.Moodle
        op_subject.active = True
        session_pg.add(op_subject)
        session_pg.commit()
        logger.warning("Subject register code: %s" %  subject.CodAsignatura)
    else:
        logger.warning("Subject Already exist code: %s" %  subject.CodAsignatura)

logger.warning("End of script subjects import")