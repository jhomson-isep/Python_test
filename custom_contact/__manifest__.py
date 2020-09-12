# -*- coding: utf-8 -*-
{
    'name': "Valida email ISEP",

    'summary': """
        Módulo para validar el campo email en el formulario de contacto
        """,

    'description': """
        Este módulo permite verificar el correcto formato del campo correo
        además de corregir el dominio de manera automática de acuerdo a algunos
        patrones.        
    """,

    'author': "Isep Latam",
    'website': "http://www.isep.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Isep',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'crm'],

    # always loaded
    'data': []
}
