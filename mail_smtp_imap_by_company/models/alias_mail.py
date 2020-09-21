# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2016-Today Geminate Consultancy Services (<http://geminatecs.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import re
from odoo.exceptions import ValidationError
from odoo.tools import remove_accents
from odoo import _, api, exceptions, fields, models, tools

class AliasMail(models.Model):
    _name = 'alias.mail'
    _rec_name = 'domain_name'
    
    domain_name = fields.Char(string="Domain Name")
    company_id = fields.Many2one('res.company', string="Company")

class Alias(models.Model):
    _inherit = "mail.alias"
    
    alias_domain = fields.Many2one('alias.mail')
    name = fields.Char(store=True)
    
    _sql_constraints = [
        ('alias_unique', 'Check(1=1)', 'Unfortunately this email alias is already used, please choose a unique one')
    ]
    
    @api.model
    def _clean_and_make_unique(self, name, alias_ids=False):
        # when an alias name appears to already be an email, we keep the local part only
        name = remove_accents(name).lower().split('@')[0]
        name = re.sub(r'[^\w+.]+', '-', name)
        return name

class Team(models.Model):
    _inherit = "crm.team"
    
    alias_domain = fields.Many2one('alias.mail')
    name = fields.Char(store=True)

class Project(models.Model):
    _inherit = "project.project"
    
    alias_domain = fields.Many2one('alias.mail')
    name = fields.Char(store=True)

class AccountJournal(models.Model):
    _inherit = "account.journal"
    
    alias_domain = fields.Many2one('alias.mail')
    name = fields.Char(store=True)

class Job(models.Model):
    _inherit = "hr.job"
    
    alias_domain = fields.Many2one('alias.mail')
    name = fields.Char(store=True)
    
