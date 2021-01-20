# -*- coding: utf-8 -*-
{
    'name': "Typeform Odoo Connector",
    "category": "Sales",
    "website": "https://melkart.io/",
    "author": "Melkart",
    "license": "Other proprietary",
    'depends': ['crm'],
    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/crm_typeform.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'qweb': [
    ],
    'application': True,
    "installable": True,
    'summary': """Typeform Odoo Connector""",
    'description': """
        Modulo para la comunicacion con Typeform 
    """,   
    "images": [
        "static/description/main.png"
    ],
    "currency": "EUR",
    "price": 49.99,
}
