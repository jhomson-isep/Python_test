# -*- coding: utf-8 -*-
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Reportes OpenEducat ISEP',
    'summary': """Reportes OpenEducat ISEP""",
    'description': """
        Modulo para los reportes:
        - UVIC
    """,
    'version': '12.0.1.0.0',
    'author': 'Isep Latam, SC',
    'website': 'https://www.isep.es/contacto/',
    'category': 'Education',
    'license': 'AGPL-3',
    'depends': [
        'base',
        'openeducat_core',
        'report_xlsx'
    ],
    'installable': True,
    'data': [
        #'wizards/uvic_student_wizard.xml',
        #'wizards/batch_students_wizard.xml',
        'reports/report_uvic_students.xml',
        'reports/report_batch_students.xml',
        'reports/report_batch_students_image.xml',
        'reports/diploma_isep.xml',
        'reports/acceptance_letter.xml',
        'reports/certified_diploma.xml',
        #'reports/certified_enrollment.xml',
        'reports/diploma_ seminar.xml',
        'reports/diploma_isep.xml',
        'reports/report_attendance.xml',
        'reports/grades_card.xml',
        'menu/report_menu.xml'
    ]
}
