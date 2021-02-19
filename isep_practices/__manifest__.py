# -*- coding: utf-8 -*-
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'ISEP Practicas',
    'summary': """Módulo practicas para ISEP""",
    'description': """
        Módulo de Prácticas
    """,
    'version': '12.0.1.0.0',
    'author': 'Isep Latam, SC',
    'website': 'https://www.isep.es/contacto/',
    'category': 'Education',
    'license': 'AGPL-3',
    'depends': [
        'base',
        'mail',
        'portal',
        'openeducat_core',
        'openeducat_fees',
        'openeducat_admission'
    ],
    'data': [
        'security/ir.model.access.csv',
        'portal/portal_practice.xml',
        'reports/specific_agreement_report.xml',
        'reports/framework_agreement_report.xml',
        'views/practice_temary.xml',
        'views/practice_tutor_course.xml',
        'views/practice_schedule_days.xml',
        'views/practice_schedule.xml',
        'views/practice_practice.xml',
        'views/res_partner_center.xml',
        'views/res_partner_change.xml',
        'views/practice_center_course.xml',
        'views/practice_center_tutor.xml',
        'menu/isep_practices_menu.xml'
    ],

    'installable': True,
    'auto_install': False,
    'application': True,
}