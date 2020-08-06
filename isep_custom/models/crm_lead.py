# -*- coding: utf-8 -*-

from openerp import api, fields, models


class crm_lead(models.Model):
    _inherit = 'crm.lead'

    x_universidad = fields.Char(string="Universidad")
    x_titulacion = fields.Char(string="Estudios")
    x_tipodedocumento = fields.Selection([('DNI', 'DNI'), ('Pasaporte', 'Pasaporte')], "Tipo de Documento")
    x_tipodecurso_id = fields.Many2one('x.crmtipodecurso', string="Tipo de Curso")
    x_tipodecontacto = fields.Selection([
                                ('-----', '-----'), ('Alumno', 'Alumno'), ('Alumno Potencial', 'Alumno Potencial'),
                                ('Cliente', 'Cliente'), ('Cliente Potencial', 'Cliente Potencial'),
                                ('Contacto', 'Contacto'), ('Distribuidor', 'Distribuidor'),
                                ('LOPD', 'LOPD'), ('Personal', 'Personal'),
                                ('Posible Distribuidor', 'Posible Distribuidor')],
                                string="Tipo de Contacto")
    x_sexo = fields.Selection([('Mujer', 'Mujer'), ('Hombre', 'Hombre')], string="Sexo")
    x_sede_id = fields.Many2one('product.attribute.value', string="Sede")
    x_profesion = fields.Char(string="Profesion")
    x_producto_id = fields.Many2one('product.product', string="Producto")
    x_precontactonuevodup = fields.Char(string="Precontacto")
    x_plannedrevenue = fields.Float(string="Ingreso Estimado")
    x_oldcrmpotentialid = fields.Integer(string="Ols Crm Potential ID")
    x_oldcrmleadid = fields.Integer(string="Old Crm Lead ID")
    x_odoosafe = fields.Integer(string="Odoo Safe")
    x_numdups = fields.Integer(string="Duplicados")
    x_modalidad_id = fields.Many2one('product.attribute.value', string="Modalidad")
    x_horario_id = fields.Many2one('x.crm.horariosdecontacto', string="Horario de Contacto")
    x_grupoduplicado = fields.Integer(string="Grupo Duplicado")
    x_ga_utma = fields.Char(string="UTMA")
    x_ga_source = fields.Char(string="Source")
    x_ga_medium = fields.Char(string="Medium")
    x_ga_campaign = fields.Char(string="Campaign")
    x_finalizacionestudios = fields.Char(string="Finalización de Estudios")
    x_documentodeidentidad = fields.Char(string="Documento de Identidad")
    x_dateactiontime = fields.Datetime(string="Fecha y hora siguiente actividad")
    x_curso_id = fields.Many2one('product.template', string="Curso")
    x_contactonuevoodup = fields.Char(string="Contacto")
    x_contactonuevoodup12 = fields.Many2one('res.users',related='partner_id.user_id',string="Contacto 2",store=True)    
    x_contactoduplicado = fields.Many2one('res.partner', string="Contacto Duplicidado")
    x_codtipodecurso = fields.Char(string="Código Tipo de Curso")
    x_codsede = fields.Char(string="Código Sede")
    x_codmodalidad = fields.Char(string="Código Modalidad")
    x_codcurso = fields.Char(string="Código de Curso")
    x_codarea = fields.Char(string="Código Area")
    x_area_id = fields.Many2one('product.category', string="Área")
    x_annonacimiento = fields.Integer(string="Año de Nacimiento")
    x_aceptacondiciones = fields.Boolean(string="Acepta Condiciones")
    x_term = fields.Char(string="Term")
    x_content = fields.Char(string="Content")
    x_colorcondup = fields.Integer(string="Color duplicidad")

    """
    Sobreescrito para que cuando se crea un lead para la empresa
    mande un mail.
    """
    @api.model
    def create(self, values):
        res = super(crm_lead, self).create(values)
        for r in res:
            if r.company_id.id == 7:
                self.env.ref('isep_custom.email_template_creacion_lead_ised_asturias').send_mail(r.id, force_send=True)
        return res

    @api.multi
    def unlink_states_leads(self):
        self.env.cr.execute("UPDATE crm_lead SET state_id=NULL WHERE state_id is not NULL")

    @api.multi
    def correccion_paises_leads(self):
        self.env.cr.execute('UPDATE crm_lead SET country_id=69 WHERE country_id=254')
