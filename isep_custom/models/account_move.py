# -*- coding: utf-8 -*-

from openerp import api, fields, models, _
from openerp.exceptions import RedirectWarning, UserError


class account_move(models.Model):
    _inherit = 'account.move'

    """
    Se hereda la funcion para realizar el chequeo de que los
    asientos al postearlo debido a que se quita esta funcionalidad
    cuando se hace el write por la herencia de la funcion assert_balanced
    """
    @api.multi
    def post(self):
        for move in self:
            move.assert_balanced(force=True)
        return super(account_move, self).post()

    """
    Se sobreescribe esta funcion debido a que si no,
    no es posible el cambio de los importes cuando se realiza
    la funcion de action_move_create de isep_custom.
    """
    @api.multi
    def assert_balanced(self, force=False):
        for s in self:
            if s.state != 'draft' or force:
                if not s.ids:
                    return True
                prec = s.env['decimal.precision'].precision_get('Account')

                s._cr.execute("""\
                    SELECT      move_id
                    FROM        account_move_line
                    WHERE       move_id in %s
                    GROUP BY    move_id
                    HAVING      abs(sum(debit) - sum(credit)) > %s
                    """, (tuple(s.ids), 10 ** (-max(5, prec))))
                if len(s._cr.fetchall()) != 0:
                    raise UserError(_("Cannot create unbalanced journal entry."))
        return True
