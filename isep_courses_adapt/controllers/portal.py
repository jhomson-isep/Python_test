from odoo import fields, http, _
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from collections import OrderedDict
from odoo.addons.portal.controllers.mail import _message_post_helper
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.addons.portal.controllers.portal import pager as portal_pager
import logging

logger = logging.getLogger(__name__)


class CustomerPortal(CustomerPortal):

    @http.route(['/my/gdrive/documents'], type='http', auth='user', website=True)
    def my_gdrive_documents(self, redirect=None, **post):
        values = None
