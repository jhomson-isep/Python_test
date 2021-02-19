# -*- coding: utf-8 -*-
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "ISEP Portal Attendances",
    "summary": """ISEP Asistencia en portal""",
    "description": """
        Añade registro de asistencia en el portal
    """,
    "version": "12.0.1.0.0",
    "author": "Isep Latam, SC",
    "website": "https://www.isep.es/contacto/",
    "category": "RRHH",
    "license": "AGPL-3",
    "depends": [
        "base",
        "hr_attendance",
    ],
    "data": [
        "views/portal_attendances.xml",

    ],
    'qweb': [
    ],
    'installable': True,
}