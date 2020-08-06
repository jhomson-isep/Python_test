# -*- coding: utf-8 -*-
# Copyright 2015-2016 Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import _, api, SUPERUSER_ID


def post_init_hook(cr, registry):
    """
    product_template: Realizamos el cambio del campo x_tipodecurso a
    tipodecurso que es un selection por lo tanto se requieren varias querys.
    """
    cr.execute("""
                update product_template
                set tipodecurso = 'curso'
                where x_tipodecurso in (4);

                update product_template
                set tipodecurso = 'desc'
                where x_tipodecurso in (8,10);

                update product_template
                set tipodecurso = 'desc_ma'
                where x_tipodecurso in (9);

                update product_template
                set tipodecurso = 'inc'
                where x_tipodecurso in (23);

                update product_template
                set tipodecurso = 'pgrado'
                where x_tipodecurso in (1,2);

                update product_template
                set tipodecurso = 'diplo'
                where x_tipodecurso in (5);

                update product_template
                set tipodecurso = 'mgrafico'
                where x_tipodecurso in (3);
            """)

    """
    Se eliminan las lineas de pago fijo de los modos de pago debido a que
    pertenecen a la parte antigua de facturacion y ya no se necesitan.
    """
    cr.execute("""
                delete from account_payment_term_line where value='fixed';
            """)
