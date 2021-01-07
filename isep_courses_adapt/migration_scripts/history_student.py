# -*- coding: utf-8 -*-
from sqlachemy_conn import MailMessage, OpStudent, Historico, get_session_server_isep, get_pg_session
from sqlalchemy import and_
import logging

session_server = get_session_server_isep()
session_pg = get_pg_session()

historys = session_server.query(Historico).all()
logger = logging.getLogger(__name__)
for history in historys:
    logger.warning("**************************************")
    logger.warning("On import students history")
    logger.warning("**************************************")
    if history.Observaciones != '':
        body = """<p>%s - %s</p>
         <p>%s</p>""" % (history.Fecha, history.Usuario, history.Observaciones)
        student = session_pg.query(OpStudent).\
                    filter(OpStudent.gr_no == history.N_Id).first()
        if student is not None:
            message = session_pg.query(MailMessage).\
                        filter(and_(MailMessage.body == body, MailMessage.model == 'op.student',
                                    MailMessage.res_id == student.id)).first()
            if message is not None:
                logger.warning("Message already exist id %s" % message.id)
                continue
            else:
                message = MailMessage()
                message.date = history.Fecha
                message.body = body
                message.model = 'op.student'
                message.res_id = student.id
                message.record_name = student.first_name + ' ' + student.last_name
                message.type = 'notification'
                message.subtype_id = 2
                message.email_from = '"Administrator" <admin@example.com>'
                message.author_id = 3
                message.no_auto_thread = False
                message.add_sign = True
                session_pg.add(message)
                session_pg.commit()
                logger.warning("Message register for student gr_no %s" % student.gr_no)
        else:
            logger.warning("Student not exist gr_no %s" % history.N_Id)
    logger.warning("**************************************")
    logger.warning("End import students history")
    logger.warning("**************************************")