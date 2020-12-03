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
        'openeducat_core'
    ],
    'installable': True,
    'data': [
        'reports/report_uvic_students.xml'
    ]
}
