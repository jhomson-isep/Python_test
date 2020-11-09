# -*- coding: utf-8 -*-
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "ISEP cambios minimos",
    "summary": """Cambios minimos en vistas o módulos""",
    "description": """
        Cambios pequeños en algunas vistas o módulos
    """,
    "version": "12.0.1.0.0",
    "author": "Isep Latam, SC",
    "website": "https://www.isep.es/contacto/",
    "category": "Education",
    "license": "AGPL-3",
    "depends": [
        "base",
        "utm",
        "sale",
        "helpdesk"
    ],
    "data": [
        "views/res_partner.xml",
        "views/helpdesk_ticket.xml",
        "views/helpdesk_team.xml"
    ],
    'installable': True,
}
