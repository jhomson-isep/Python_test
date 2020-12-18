from sqlalchemy import and_, desc
from datetime import datetime
from sqlachemy_conn import *
import traceback

# POSTGRES SERVER SESSION
session_pg = get_pg_session()

batch_subjects = session_pg.query(OpBatchSubjectRel).all()

for batch_subject in batch_subjects:
    try:
        exam_session = session_pg.query(OpExamSession).filter(
            OpExamSession.batch_id == batch_subject.batch_id).first()
        batch = session_pg.query(OpBatch).filter(
            OpBatch.id == batch_subject.batch_id).first()
        course = session_pg.query(OpCourse).filter(
            OpCourse.id == batch.course_id).first()
        subject = session_pg.query(OpSubject).filter(
            OpSubject.id == batch_subject.subject_id).first()
        if subject is not None and batch_subject is not None:
            exam = session_pg.query(OpExam).filter(
                OpExam.exam_code == batch.code + subject.code).first()
            if exam is None:
                exam = OpExam()
                exam.session_id = exam_session.id
                exam.course_id = course.id
                exam.batch_id = batch.id
                exam.subject_id = subject.id
                exam.exam_code = batch.code + subject.code
                exam.name = "-".join([batch.code, subject.code])
                exam.start_time = batch.start_date
                exam.end_time = batch.end_date
                exam.total_marks = 10
                exam.min_marks = 5
                exam.state = 'done'
                exam.active = True
                session_pg.add(exam)
                session_pg.commit()
                print("Exam created: ", exam.exam_code)
            else:
                print("Exam Already exist: ", exam.exam_code)
        else:
            not_found = "Subject" if subject is None else "Batch"
            print("{} not found".format(not_found))
    except Exception as e:
        print(e)
        traceback.print_tb(e.__traceback__)
        continue
print("Migration terminated")
