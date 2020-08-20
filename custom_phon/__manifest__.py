# -*- coding: utf-8 -*-
{
    'name': "Validar Teléfono ISEP",

    'summary': """
        Modulo para la estandarización del campo teléfono""",

    'description': """
        Éste módulo regulariza el ingreso de números telefónicos en el campo teléfono de acuerdo
        a las normas internacionales.
    """,

    'author': "ISEP LATAM",
    'website': "http://www.isep.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}