# -*- coding: utf-8 -*-

from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, formataddr
from odoo import api, fields, models, _
from werkzeug.urls import url_join
import logging

logger = logging.getLogger(__name__)


class SignRequest(models.Model):
    _inherit = 'sign.request'

    @api.one
    def _sign_imc_send_follower_accesses(self, followers, subject=None,
                                         message=None):
        base_url = self.env['ir.config_parameter'].sudo().get_param(
            'web.base.url')
        config_params = self.env['ir.config_parameter'].sudo()
        mail_server_id = config_params.get_param('sign_mail_server_id')
        logger.info("mail_server_id: {}".format(mail_server_id))
        tpl = self.env.ref('sign.sign_template_mail_follower')
        body = tpl.render({
            'record': self,
            'link': url_join(base_url, 'sign/document/%s/%s' % (
            self.id, self.access_token)),
            'subject': subject,
            'body': message,
            'mail_server_id': mail_server_id or None,
        }, engine='ir.qweb', minimal_qcontext=True)
        for follower in followers:
            if not follower.email:
                continue
            self.env['sign.request']._message_send_mail(
                body, 'mail.mail_notification_light',
                {'record_name': self.reference},
                {'model_description': 'signature',
                 'mail_server_id': mail_server_id or None,
                 'company': self.create_uid.company_id},
                {'email_from': formataddr(
                    (self.create_uid.name, self.create_uid.email)),
                 'email_to': formataddr((follower.name, follower.email)),
                 'subject': subject or _(
                     '%s : Signature request') % self.reference}
            )
            self.message_subscribe(partner_ids=follower.ids)

    @api.model
    def _message_send_mail(self, body, notif_template_xmlid, message_values,
                           notif_values, mail_values, **kwargs):
        """ Shortcut to send an email. """
        msg = self.env['mail.message'].sudo().new(
            dict(body=body, **message_values))

        config_params = self.env['ir.config_parameter'].sudo()
        mail_server_id = config_params.get_param('sign_mail_server_id')
        logger.info("mail_server_id: {}".format(mail_server_id))

        notif_layout = self.env.ref(notif_template_xmlid)
        body_html = notif_layout.render(dict(message=msg, **notif_values),
                                        engine='ir.qweb',
                                        minimal_qcontext=True)
        body_html = self.env['mail.thread']._replace_local_links(body_html)
        mail = self.env['mail.mail'].create(dict(body_html=body_html,
                                                 state='outgoing',
                                                 mail_server_id=mail_server_id,
                                                 **mail_values))
        mail.send()
        return mail
