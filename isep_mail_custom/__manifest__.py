# -*- coding: utf-8 -*-
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Customización mails Isep',
    'version': '12.0.1',
    'summary': 'Agrega funcionalidades para la optimizacion del envio de campañas de marketing.',
    'description': """
Agrega funcionalidades para la optimizacion del envio de campañas de marketing con api de Mailjet
========================================
- Go to settings -> General Settings -> Mail Send Limit. Set limit value when mail scheduler run.
    """,
    'author': 'Isep Latam S.C.',
    'website': 'https://www.isep.com',
    'category': 'mail',
    'license': 'AGPL-3',
    'depends': [
        'base',
        'mail',
        'mass_mailing'
    ],
    'data': [
        'views/mass_mailing.xml'
    ],
    'installable': True
}
