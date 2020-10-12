# -*- coding: utf-8 -*-
{
    'name': "Helpdesk Ticket Escalation & Reminders",
    'license': 'OPL-1',
    'support': 'support@optima.co.ke',

    'summary': """
        Enforce SLAs by activating Email reminders and escalations for tickets.
        """,

    'description': """
        Enforce SLAs by activating Email reminders and escalations for tickets.
    """,

    'author': "Optima ICT Services LTD",
    'website': "http://www.optima.co.ke",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Helpdesk',
    'version': '0.1',
    'price': 89,
    'currency': 'EUR',
    'images': ['static/description/main.png'],

    # any module necessary for this one to work correctly
    'depends': ['base', 'helpdesk', 'base_automation'],

    # always loaded
    'data': [
        'data/email_template.xml',
        'data/base_automation.xml',
        'data/ir_cron.xml',
        'views/views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        #'demo/demo.xml',
    ],
    'application': True,
}
