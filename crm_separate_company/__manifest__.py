# -*- coding: utf-8 -*-
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "ISEP Separador de Leads por compañias",
    "summary": """Separador de Leads mediante la compañia a la que corresponde""",
    "description": """
        Separar los leads mediante:
            - URL
            - Alguna Variable que defina la compañia
            - Formularios
    """,
    "version": "12.0.1.0.0",
    "author": "Isep Latam, SC",
    "website": "https://www.isep.es/contacto/",
    "category": "Education",
    "license": "AGPL-3",
    "depends": [
        "base",
        "crm"
    ],
    "data": [
        "security/ir.model.access.csv"
    ],
    'installable': True,
}
