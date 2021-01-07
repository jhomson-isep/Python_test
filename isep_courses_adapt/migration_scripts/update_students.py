# -*- coding: utf-8 -*-
from sqlachemy_conn import *
import json

session_pg = get_pg_session()

with open('moodle_campus.json') as json_file:
    data = json.load(json_file)
    for sql_student in data:
        try:
            student = session_pg.query(OpStudent).filter(
                OpStudent.n_id == str(sql_student['n_id'])).first()
            if student is not None:
                student.moodle_id = sql_student['id']
                student.moodle_user = sql_student['username']
                session_pg.commit()
                print("Student updated: ", student.n_id)
            else:
                print("Student not found: ", sql_student['n_id'])
        except Exception as e:
            print(e)
            continue
