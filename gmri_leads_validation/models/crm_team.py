# -*- coding: utf-8 -*-
# © 2018 Qubiq 2010
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api
import logging
import unicodedata
from datetime import datetime
from dateutil import relativedelta
import sys
# reload(sys)
# sys.setdefaultencoding('utf8')
logger = logging.getLogger(__name__)


class crm_team(models.Model):
	  _inherit = 'crm.team'
	  code = fields.Char(string="Código")
