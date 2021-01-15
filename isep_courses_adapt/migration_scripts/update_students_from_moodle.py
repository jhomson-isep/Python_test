# -*- coding: utf-8 -*-

from sqlachemy_conn import *
from sqlalchemy import or_
from moodle import *
import traceback

session_pg = get_pg_session()
Moodle = MoodleLib()

users = Moodle.get_all_users()
for index, user in enumerate(users):
    try:
        if 'idnumber' in user:
            students = session_pg.query(OpStudent, ResPartner).join(
                ResPartner, OpStudent.partner_id == ResPartner.id).filter(
                or_(OpStudent.moodle_id == user['id'],
                    OpStudent.document_number == user['idnumber'],
                    ResPartner.email == user['email'])).all()
        else:
            students = session_pg.query(OpStudent, ResPartner).join(
                ResPartner, OpStudent.partner_id == ResPartner.id).filter(
                or_(OpStudent.moodle_id == user['id'],
                    ResPartner.email == user['email'])).all()
        print("{} Students found: {}".format(index, len(students)))
        for student in students:
            student.OpStudent.moodle_id = user['id']
            student.OpStudent.moodle_user = user['username']
            if 'idnumber' in user and (
                    student.OpStudent.document_number is None
                    or not student.OpStudent.document_number
            ):
                student.OpStudent.document_number = user['idnumber']
            session_pg.commit()
            print("Student updated: ", student.OpStudent.id)
    except Exception as e:
        print(e)
        print(user)
        traceback.print_exc()
        break
