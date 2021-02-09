# -*- coding: utf-8 -*-

from sqlachemy_conn import get_pg_session, OpCourse, OpModality, \
    OpMoodleCategoryRel
import csv


def get_categories_from_csv():
    courses = []
    with open('./moodle_category_rel.csv', 'r') as f:
        reader = csv.reader(f)
        for line in reader:
            courses.append({'name': line[0], 'code': line[1], 'course': line[
                2], 'course_name': line[3], 'modality': line[4], 'category':
                                line[5]})
    return courses


def set_moodle_categories():
    session_pg = get_pg_session()
    categories = get_categories_from_csv()
    for category in categories:
        courses = session_pg.query(OpCourse).filter(
            OpCourse.code == category.get('course')).all()
        modality = session_pg.query(OpModality).filter(
            OpModality.code == category.get('modality')).first()
        if modality is not None:
            moodle_category_rel = session_pg.query(OpMoodleCategoryRel).filter(
                OpMoodleCategoryRel.name == category.get('name')).first()
            if moodle_category_rel is None:
                for course in courses:
                    moodle_category_rel = OpMoodleCategoryRel()
                    moodle_category_rel.name = "-".join(
                        [category.get('name'), course.id])
                    moodle_category_rel.code = category.get('code')
                    moodle_category_rel.moodle_category = category.get(
                        'category')
                    moodle_category_rel.modality_id = modality.id
                    moodle_category_rel.course_id = course.id
                    session_pg.add(moodle_category_rel)
                    session_pg.commit()
                    print("Moodle category created: ",
                          moodle_category_rel.name)
                else:
                    print("Moodle category already exist: ", category)
        else:
            print("modality not found: ", category.get('modality'))


if __name__ == "__main__":
    set_moodle_categories()
