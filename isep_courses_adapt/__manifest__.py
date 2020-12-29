# -*- coding: utf-8 -*-
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Adaptación de cursos OpenEducat para ISEP',
    'summary': """Adaptación de cursos OpenEducat para ISEP""",
    'description': """
        Modulo para la adaptacion de cursos Odoo / Moodle:
            - Cursos
            - Asignaturas
            - Lotes
    """,
    'version': '12.0.1.0.0',
    'author': 'Isep Latam, SC',
    'website': 'https://www.isep.es/contacto/',
    'category': 'Education',
    'license': 'AGPL-3',
    'depends': [
        'base',
        'sale',
        'mail',
        'portal',
        'l10n_mx_einvoice',
        'openeducat_core',
        'openeducat_fees',
        'openeducat_exam',
        'openeducat_library',
        'openeducat_admission',
        'openeducat_attendance',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/op_course.xml',
        'views/op_batch.xml',
        'views/op_modality.xml',
        'views/op_workplace.xml',
        'views/op_gdrive_documents.xml',
        'views/op_student_access.xml',
        'views/op_evaluation_type.xml',
        'views/op_campus.xml',
        'views/op_practices_types.xml',
        'views/res_config_settings_views.xml',
        'views/op_subject.xml',
        'views/op_batch_subject_rel.xml',
        'views/op_contact_type.xml',
        'views/op_study_type.xml',
        'views/op_document_type.xml',
        'views/op_student.xml',
        'views/op_university.xml',
        'views/op_faculty.xml',
        'views/op_student_view.xml',
        'views/op_area_course.xml',
        'views/res_partner_documentation.xml',
        'views/op_portal_documentation.xml',
        'views/op_attendance_line.xml',
        'views/op_admission.xml',
        'views/op_admission_register.xml',
        # 'views/sale_order.xml',
        'views/op_exam_session.xml',
        'views/op_exam_attendances.xml',
        'menu/isep_courses_adapt_menu.xml',
        'data/op_document_type.xml',
        'data/op_evaluation_type.xml',
        'data/op.study.type.csv',
        'data/op.university.csv',
        'data/op_modality.xml',
        'data/op_exam_type.xml',
        'data/op.campus.csv',
        'data/cron.xml',
        'data/plantillas_mail.xml',
        'data/list_fields_op_admission_export.xml',
        'data/sequences.xml'
    ],
    'installable': True,
}
