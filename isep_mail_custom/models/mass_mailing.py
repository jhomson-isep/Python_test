# -*- encoding: utf-8 -*-

import logging
import threading
import re

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError
from mailjet_rest import Client

_logger = logging.getLogger(__name__)

api_key = '5350a6c8d4d0d5f00422c0204f95c756'
api_secret = 'e8238c1d9e9b090edce0ef413301fe69'
mailjet = Client(auth=(api_key, api_secret), version='v3.1')
EMAIL_PATTERN = '([^ ,;<@]+@[^> ,;]+)'


class MassMailing(models.Model):
    _inherit = 'mail.mass_mailing'

    use_api = fields.Boolean(string='Usar API de Mailjet', required=False, default=True)
    mailjet_campaign_id = fields.Integer(string='ID de campaña (Mailjet)')

    def send_api_mail(self, res_ids=None):
        author_id = self.env.user.partner_id.id

        for mailing in self:
            if not res_ids:
                res_ids = mailing.get_remaining_recipients()
            if not res_ids:
                raise UserError(_('There is no recipients selected.'))

            while len(res_ids) > 0:
                recipients = []
                _logger.info(mailing.mailing_model_real)
                extra_context = self._get_mass_mailing_context()
                recipients_list = self.env[mailing.mailing_model_real].search([('id', 'in', res_ids)], limit=50)
                recipients_list = recipients_list.with_context(active_ids=res_ids, **extra_context)
                _logger.info(type(res_ids))

                for rl in recipients_list:
                    is_blacklisted = False
                    statistics_values = {
                        'model': mailing.mailing_model_real,
                        'res_id': rl.id,
                        'mass_mailing_id': mailing.id,
                        'sent': fields.Datetime.now(),
                        'state': 'sent'
                    }
                    email_to = ''
                    name = ''
                    if mailing.mailing_model_real == "crm.lead":
                        email_to = rl.partner_id.email
                        name = rl.partner_id.name
                        if not rl.is_blacklisted and not rl.partner_is_blacklisted and re.match(EMAIL_PATTERN,
                                                                                                email_to):
                            recipients.append({'Email': email_to, 'Name': name})
                            statistics_values.update({'email': email_to, 'partner_id': rl.partner_id})
                        else:
                            statistics_values.update({'email': email_to, 'partner_id': rl.partner_id,
                                                      'ignored': fields.Datetime.now(), 'state': 'ignored',
                                                      'sent': None})
                            is_blacklisted = True
                    else:
                        email_to = rl.email
                        name = rl.name
                        if not rl.is_blacklisted and rl.is_email_valid:
                            recipients.append({'Email': email_to, 'Name': name})
                            statistics_values.update({'email': email_to})
                        else:
                            statistics_values.update(
                                {'email': email_to, 'ignored': fields.Datetime.now(), 'state': 'ignored', 'sent': None})
                            is_blacklisted = True

                    # =========== Create mail.mail ===========
                    mail = self.env['mail.mail']
                    mail_values = {
                        'subject': mailing.name,
                        'email_from': mailing.email_from,
                        'email_to': email_to,
                        'model': mailing.mailing_model_real,
                        'body': tools.html2plaintext(mailing.body_html),
                        'body_html': mailing.body_html,
                        'res_id': rl.id,
                        'mailing_id': mailing.id,
                        'state': 'sent',
                        # 'auto_delete': True,
                        'scheduled_date': fields.Datetime.now()
                    }
                    msg_id = mail.create(mail_values)
                    statistics_values.update(
                        {'mail_mail_id': msg_id.id, 'mail_mail_id_int': msg_id.id, 'message_id': msg_id.message_id})
                    # ============= Create mail.mail ============

                    _logger.info("========== is_blacklisted ===========")
                    _logger.info(is_blacklisted)
                    _logger.info("========== is_blacklisted ===========")
                    statistics = self.env['mail.mail.statistics'].with_context(active_ids=res_ids,
                                                                               **extra_context).create(
                        statistics_values)

                data = {
                    'Messages': [
                        {
                            "From": {
                                "Email": mailing.email_from,
                                "Name": mailing.email_from,
                            },
                            "To": recipients,
                            "Subject": mailing.name,
                            "TextPart": tools.html2plaintext(mailing.body_html),
                            "HTMLPart": mailing.body_html,
                            "CustomCampaign": mailing.name,
                            "DeduplicateCampaign": True
                        }
                    ]
                }

                _logger.info(data)
                result = mailjet.send.create(data=data)
                if result.status_code == 200:
                    _logger.info(result)
                    _logger.info(result.json())
                else:
                    raise UserError(_("Error on mailjet connection: " % str(result.json())))
                    _logger.info(result)
                    _logger.info(result.json())
                res_ids = mailing.get_remaining_recipients()
        return True

    @api.model
    def _process_mass_mailing_queue(self):
        mass_mailings = self.search(
            [('state', 'in', ('in_queue', 'sending')), '|', ('schedule_date', '<', fields.Datetime.now()),
             ('schedule_date', '=', False)])
        for mass_mailing in mass_mailings:
            user = mass_mailing.write_uid or self.env.user
            mass_mailing = mass_mailing.with_context(**user.sudo(user=user).context_get())
            _logger.info(mass_mailing.use_api)
            if not mass_mailing.use_api:
                if len(mass_mailing.get_remaining_recipients()) > 0:
                    mass_mailing.state = 'sending'
                    mass_mailing.send_mail()
                else:
                    mass_mailing.write({'state': 'done', 'sent_date': fields.Datetime.now()})
            else:
                _logger.info("========== Use api ===========")
                _logger.info(mass_mailing)
                _logger.info("========== Use api ===========")
                if len(mass_mailing.get_remaining_recipients()) > 0:
                    mass_mailing.state = 'sending'
                    mass_mailing.write({'state': 'sending'})
                    mass_mailing.send_api_mail()
                else:
                    mass_mailing.write({'state': 'done', 'sent_date': fields.Datetime.now()})
