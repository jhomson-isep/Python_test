# -*- coding: utf-8 -*-
from datetime import datetime

from sqlalchemy import and_, desc
from sqlachemy_conn import *

# POSTGRES SERVER SESSION
session_pg = get_pg_session()

batches = session_pg.query(OpBatch).all()

for batch in batches:
    try:
        exam_session = session_pg.query(OpExamSession).filter(
            OpExamSession.exam_code == batch.code).first()
        exam_type = session_pg.query(OpExamType).filter(
            OpExamType.code == 'SUBJ').first()
        if exam_session is None:
            exam_session = OpExamSession()
            exam_session.name = batch.name
            exam_session.course_id = batch.course_id
            exam_session.batch_id = batch.id
            exam_session.exam_code = batch.code
            exam_session.start_date = batch.start_date
            exam_session.end_date = batch.end_date
            exam_session.evaluation_type = 'grade'
            exam_session.exam_type = exam_type.id
            exam_session.state = 'done'
            exam_session.active = True
            session_pg.add(exam_session)
            session_pg.commit()
            print("Exam Session created: ", exam_session.exam_code)
        else:
            print("Exam Session Already exist: ", batch.code)
    except Exception as e:
        print(e)
        continue
print("The migration is over")
