# -*- coding: utf-8 -*-
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "Customización CRM para ISEP",
    "version": "9.0.1.0.0",
    "author": "QubiQ",
    "website": "https://www.qubiq.es",
    "category": "crm",
    "license": "AGPL-3",
    "depends": [
        "base",
        "sale",
        "product",
        "crm",
        "account",
        "mail",
        "crm_duplicates",
        "base_vat",
        #"sale_stock",
        "website_partner",
        "base_location_geonames_import",
        "payment",
        "account_payment_sale",
        "account_payment_partner",
        "account_banking_sepa_direct_debit",
        "account_banking_mandate",
        "account_payment_order",
        "base_location",
        "account_due_list",
        "hr",
    ],
    "data": [
         "security/security.xml",
         #"data/isep_data.xml",
         "data/secuencias.xml",
         "data/grupos_usuarios.xml",
         #"data/plantillas_mail.xml",
         #"data/acciones_planificadas.xml",
         "views/res_partner_view.xml",
         "views/sale_order.xml",
         "views/mail_message.xml",
         "views/crm_lead.xml",
         "views/account_invoice.xml",
         "views/product_template.xml",
         "views/isep_pagos.xml",
         "views/account_move.xml",
         "views/account_move_line.xml",
         #"views/puntos_menus.xml",
         "views/payment_method.xml",
         "views/payment_token.xml",
         #"views/crm_calls.xml",
         #"views/crm_temp_leads.xml",
         #"views/crm_temp_calls.xml",
         "views/account_payment_line.xml",
         "wizard/account_payment_line_create_view.xml",
         "wizard/reasignacion_iniciativas_view.xml",
         "wizard/import_cobros_academica.xml",
         "reports/report_saleorder.xml",
         # "reports/report_sale_order_mandate.xml",
         "reports/report_sale_prematricula.xml",
         "reports/report_sale_prematricula2.xml",
         "reports/report_sale_prematricula_ised_onl.xml",
         "reports/report_sale_prematricula_isep_no_presencial.xml",
         "reports/report_sale_prematricula_isep_no_presencial_extranjero.xml",
         "reports/report_sale_prematricula_isep_presencial.xml",
         "reports/report_sale_prematricula_isep_presencial_extranjero.xml",
         "reports/report_sale_prematricula_titular.xml",
         "reports/report_sale_presupuesto.xml",
         # "reports/report_sale_seguridad2.xml",
         # "reports/report_saleorder_document_pagos.xml",
         # "reports/account_invoice.xml",
         # "reports/report_footer_header.xml",
         "security/ir.model.access.csv",
    ],
    'installable': True,
    "post_init_hook": "post_init_hook",
}