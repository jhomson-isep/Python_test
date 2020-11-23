# -*- coding: utf-8 -*-
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "ISEP Portal Chatter Attachments",
    "summary": """ISEP archivos adjuntos en portal""",
    "description": """
        Añade funcionalidad para archivos adjuntos en el portal
    """,
    "version": "12.0.1.0.0",
    "author": "Isep Latam, SC",
    "website": "https://www.isep.es/contacto/",
    "category": "Education",
    "license": "AGPL-3",
    "depends": [
        "base",
        "purchase"
    ],
    "data": [
        "views/purchase_order_portal.xml",
        "views/purchase_order.xml"
    ],
    'qweb': [
        'static/src/xml/portal_chatter.xml'
    ],
    'installable': True,
}
