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
        "crm",
        "utm",
        "sale",
        "helpdesk",
        "project",
        "isep_custom",
        "sign"
    ],
    "data": [
        "data/mail_templates.xml",
        "views/res_partner.xml",
        "views/helpdesk_ticket.xml",
        "views/helpdesk_team.xml",
        "views/project_task.xml",
        "views/crm_lead.xml",
        "views/res_config_settings.xml",
        "views/payment_token.xml",
        "views/sale_order.xml",
        "data/res_groups.xml",
        "views/res_users.xml"
    ],
    'installable': True,
}
