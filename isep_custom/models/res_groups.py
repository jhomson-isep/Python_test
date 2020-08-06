# -*- coding: utf-8 -*-
# Copyright (C) 2017 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from datetime import datetime
from psycopg2 import ProgrammingError

from openerp import _, api, fields, models, SUPERUSER_ID
from openerp.exceptions import Warning as UserError

_logger = logging.getLogger(__name__)


class ResGroups(models.Model):
    _inherit = 'res.groups'

    name = fields.Char(copy=False)


    @api.multi
    def copy(self, default=None):
        _logger.info('HOOOOOLA')
        self.ensure_one()
        default = dict(default or {})
        default.update({
            'name': _('%s (Copy)') % (self.name),

        })
        _logger.info(default)
        return super(ResGroups, self).copy(default=default)


