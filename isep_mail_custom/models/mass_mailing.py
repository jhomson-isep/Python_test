# -*- encoding: utf-8 -*-

import logging
import threading
import re

from odoo import api, fields, models, tools, _
from binascii import Error as binascii_error
from odoo.exceptions import UserError
from odoo.tools import email_re
from mailjet_rest import Client

_image_dataurl = re.compile(r'(data:image/[a-z]+?);base64,([a-z0-9+/\n]{3,}=*)\n*([\'"])(?: data-filename="([^"]*)")?', re.I)
_logger = logging.getLogger(__name__)

api_key = '5350a6c8d4d0d5f00422c0204f95c756'
api_secret = 'e8238c1d9e9b090edce0ef413301fe69'
mailjet = Client(auth=(api_key, api_secret), version='v3.1')
EMAIL_PATTERN = '([^ ,;<@]+@[^> ,;]+)'


class MassMailing(models.Model):
    _inherit = 'mail.mass_mailing'

    use_api = fields.Boolean(string='Usar API de Mailjet', required=False,
                             default=True)
    mailjet_campaign_id = fields.Integer(string='ID de campaña (Mailjet)')

    def send_api_mail(self, res_ids=None):

        for mailing in self:
            if not res_ids:
                res_ids = mailing.get_remaining_recipients()
            if not res_ids:
                raise UserError(_('There is no recipients selected.'))

            while len(res_ids) > 0:
                messages = []
                extra_context = self._get_mass_mailing_context()
                recipients_list = self.env[mailing.mailing_model_real].search(
                    [('id', 'in', res_ids)], limit=50)
                recipients_list = recipients_list.with_context(
                    active_ids=res_ids, **extra_context)

                for rl in recipients_list:
                    recipient = []
                    extra_context = self._get_mass_mailing_context()
                    opt_out_list = extra_context.get(
                        'mass_mailing_opt_out_list')
                    seen_list = extra_context.get('mass_mailing_seen_list')
                    statistics_values = {
                        'model': mailing.mailing_model_real,
                        'res_id': rl.id,
                        'mass_mailing_id': mailing.id,
                        'sent': fields.Datetime.now(),
                        'state': 'sent'
                    }

                    if mailing.mailing_model_real == "crm.lead":
                        email_to = rl.partner_id.email
                        name = rl.partner_id.name
                        try:
                            if (opt_out_list and email_to in opt_out_list) or (
                                    seen_list and email_to in seen_list) or (
                                    not email_to or not email_re.findall(
                                    email_to)):
                                statistics_values.update(
                                    {'email': email_to,
                                     'ignored': fields.Datetime.now(),
                                     'state': 'ignored',
                                     'sent': None})
                            else:
                                recipient.append(
                                    {'Email': email_to, 'Name': name})
                                statistics_values.update(
                                    {'email': email_to})
                        except Exception as e:
                            _logger.info(e)
                            statistics_values.update(
                                {'email': email_to,
                                 'ignored': fields.Datetime.now(),
                                 'state': 'ignored',
                                 'sent': None})
                    else:
                        email_to = rl.email
                        name = rl.name
                        try:
                            if (opt_out_list and email_to in opt_out_list) or (
                                    seen_list and email_to in seen_list) or (
                                    not email_to or not email_re.findall(
                                    email_to)):
                                statistics_values.update(
                                    {'email': email_to,
                                     'ignored': fields.Datetime.now(),
                                     'state': 'ignored', 'sent': None})
                            else:
                                statistics_values.update({'email': email_to})
                                recipient.append(
                                    {'Email': email_to, 'Name': name})
                        except Exception as e:
                            _logger.info(e)
                            statistics_values.update(
                                {'email': email_to,
                                 'ignored': fields.Datetime.now(),
                                 'state': 'ignored', 'sent': None})

                    # # =========== Create mail.mail ===========
                    mail = self.env['mail.mail']
                    body = self.env['mail.thread']._replace_local_links(
                        mailing.body_html)
                    mail_values = {
                        'subject': mailing.name,
                        'email_from': mailing.email_from,
                        'email_to': email_to,
                        'model': mailing.mailing_model_real,
                        'body': tools.html2plaintext(body),
                        'body_html': body,
                        'res_id': rl.id,
                        'mailing_id': mailing.id,
                        'state': 'sent',
                        # 'auto_delete': True,
                        'scheduled_date': fields.Datetime.now()
                    }

                    msg_id = mail.create(mail_values)
                    statistics_values.update(
                        {'mail_mail_id': msg_id.id,
                         'mail_mail_id_int': msg_id.id,
                         'message_id': msg_id.message_id})

                    base_url = self.env[
                        'ir.config_parameter'].sudo().get_param(
                        'web.base.url').rstrip('/')
                    link_to_replace = base_url + '/unsubscribe_from_list'
                    unsubscribe_url = msg_id._get_unsubscribe_url(email_to)

                    if link_to_replace in body:
                        msg_id.update({'body_html': body.replace(
                            link_to_replace,
                            unsubscribe_url if unsubscribe_url else '#')})
                        mailing.update({'body_html': body.replace(
                            link_to_replace,
                            unsubscribe_url if unsubscribe_url else '#')})
                    # ============= Create mail.mail ============

                    statistics = self.env['mail.mail.statistics'].with_context(
                        active_ids=res_ids, **extra_context).create(
                        statistics_values)
                    self.env.cr.commit()

                    if len(recipient) > 0:
                        message = {
                                "From": {
                                    "Email": mailing.email_from,
                                    "Name": mailing.email_from,
                                },
                                "To": recipient,
                                "Subject": mailing.name,
                                "TextPart": tools.html2plaintext(body),
                                "HTMLPart": body
                            }
                        messages.append(message)

                if len(messages) > 1:
                    data = {
                        'Messages': messages
                    }
                    result = mailjet.send.create(data=data)
                    if result.status_code == 200:
                        _logger.info(result.json())
                    else:
                        _logger.info(data)
                        _logger.info(result.json())
                        raise UserError(_(
                            "Error on mailjet connection: " % str(result.json())))
                res_ids = mailing.get_remaining_recipients()
                messages = []
        return True

    @api.model
    def _process_mass_mailing_queue(self):
        mass_mailings = self.search(
            [('state', 'in', ('in_queue', 'sending')), '|',
             ('schedule_date', '<', fields.Datetime.now()),
             ('schedule_date', '=', False)])
        for mass_mailing in mass_mailings:
            user = mass_mailing.write_uid or self.env.user
            mass_mailing = mass_mailing.with_context(
                **user.sudo(user=user).context_get())
            if len(mass_mailing.get_remaining_recipients()) > 0:
                mass_mailing.state = 'sending'
                if mass_mailing.use_api:
                    mass_mailing.send_api_mail()
                else:
                    mass_mailing.send_mail()
            else:
                mass_mailing.write(
                    {'state': 'done', 'sent_date': fields.Datetime.now()})

    def prepare_images(self, values):
        Attachments = self.env['ir.attachment']
        data_to_url = {}

        def base64_to_boundary(match):
            key = match.group(2)
            if not data_to_url.get(key):
                name = match.group(4) if match.group(
                    4) else 'image%s' % len(data_to_url)
                try:
                    attachment = Attachments.create({
                        'name': name,
                        'datas': match.group(2),
                        'datas_fname': name,
                        'res_model': values.get('model'),
                        'res_id': values.get('res_id'),
                    })
                except binascii_error:
                    _logger.warning(
                        "Impossible to create an attachment out of badly formated base64 embedded image. Image has been removed.")
                    return match.group(
                        3)  # group(3) is the url ending single/double quote matched by the regexp
                else:
                    attachment.generate_access_token()
                    values['attachment_ids'].append((4, attachment.id))
                    data_to_url[key] = ['/web/image/%s?access_token=%s' % (
                        attachment.id, attachment.access_token), name]
            return '%s%s alt="%s"' % (
                data_to_url[key][0], match.group(3), data_to_url[key][1])

        values['body'] = _image_dataurl.sub(base64_to_boundary,
                                            tools.ustr(values['body']))

        return values
