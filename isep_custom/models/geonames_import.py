# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.exceptions import UserError
import requests
import tempfile
# import StringIO
from io import StringIO
import zipfile
import os
import logging

try:
    import unicodecsv
except ImportError:
    unicodecsv = None

logger = logging.getLogger(__name__)


class BetterZipGeonamesImport(models.TransientModel):
    _inherit = 'better.zip.geonames.import'

    @api.model
    def create_better_zip(self, row, country):
        if row[0] != country.code:
            raise UserError(
                _("The country code inside the file (%s) doesn't "
                    "correspond to the selected country (%s).")
                % (row[0], country.code))
        logger.debug('ZIP = %s - City = %s' % (row[1], row[2]))
        if (self.title_case):
            row[2] = row[2].title()
            row[3] = row[3].title()
        if row[1] and row[2]:
            zip_model = self.env['res.better.zip']
            zips = zip_model.search(self._domain_search_better_zip(
                row, country))
            if zips:
                return zips[0]
            else:
                vals = self._prepare_better_zip(row, country)
                if vals:
                    return zip_model.create(vals)
                else:
                    return None
        else:
            return False

    @api.model
    def _prepare_better_zip(self, row, country):
        state = self.select_or_create_state(row, country)
        vals = None
        if state:
            vals = {
                'name': row[1],
                'city': self.transform_city_name(row[2], country),
                'state_id': state.id,
                'country_id': country.id,
                }
        return vals

    @api.model
    def select_or_create_state(
            self, row, country, code_row_index=4, name_row_index=3):
        states = self.env['res.country.state'].search([
            ('country_id', '=', country.id),
            ('code', '=', row[code_row_index]),
            ])
        logger.info(row[code_row_index])
        logger.info(states)
        if len(states) > 1:
            return None
        if len(states) == 1:
            return states[0]
        else:
            return self.env['res.country.state'].create({
                'name': row[name_row_index],
                'code': row[code_row_index],
                'country_id': country.id
                })

    @api.multi
    def run_import_all(self):
        zip_model = self.env['res.better.zip']
        country_list = self.env["res.country"].sudo().search(
            [('create_uid', '=', 1), ('code', '!=', ''), ('code', '!=', None)])  

        logger.info(country_list)  

        for country_code in country_list:
            config_url = self.env['ir.config_parameter'].get_param(
                'geonames.url',
                default='http://download.geonames.org/export/zip/%s.zip')
            url = config_url % country_code.code
            logger.info('Starting to download %s' % url)
            res_request = requests.get(url)
            if res_request.status_code == requests.codes.ok:
                # Store current record list
                zips_to_delete = zip_model.search(
                    [('country_id', '=', country_code.id)])
                f_geonames = zipfile.ZipFile(StringIO.StringIO(res_request.content))
                tempdir = tempfile.mkdtemp(prefix='openerp')
                f_geonames.extract('%s.txt' % country_code.code, tempdir)
                logger.info('The geonames zipfile has been decompressed')
                data_file = open(os.path.join(tempdir, '%s.txt' % country_code.code), 'r')
                data_file.seek(0)
                logger.info('Starting to create the better zip entries')
                max_import = self.env.context.get('max_import', 0)
                reader = unicodecsv.reader(data_file, encoding='utf-8', delimiter='	')
                for i, row in enumerate(reader):
                    zip_code = self.create_better_zip(row, country_code)
                    if zip_code:
                        if zip_code in zips_to_delete:
                            zips_to_delete -= zip_code
                        if max_import and (i + 1) == max_import:
                            break
                data_file.close()
                if zips_to_delete and not max_import:
                    zips_to_delete.unlink()
                    logger.info('%d better zip entries deleted for country %s' %
                                (len(zips_to_delete), country_code.name))
                logger.info(
                    'The wizard to create better zip entries from geonames '
                    'has been successfully completed.')
        return True