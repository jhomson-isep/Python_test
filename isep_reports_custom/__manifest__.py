# -*- coding: utf-8 -*-
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Reportes para ISEP',
    'summary': """Reportes para ISEP""",
    'description': """
        Modulo para los reportes, matriculas y facturas (Solo vistas).
    """,
    'version': '12.0.1.0.0',
    'author': 'Isep Latam, SC',
    'website': 'https://www.isep.es/contacto/',
    'category': 'Education',
    'license': 'AGPL-3',
    'depends': [
        'base',
        'sale'
    ],
    'installable': True,
    'data': [
        'reports/factura_isep_espana.xml',
        'reports/hoja_matricula_ISEPSL.xml',
        'reports/hoja_matricula_ISED.xml'

    ]
}
