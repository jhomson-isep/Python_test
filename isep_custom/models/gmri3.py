# -*- coding: utf-8 -*-
# import pyodbc
import psycopg2
import MySQLdb
import datetime
import calendar
from decimal import *
import logging
from openerp import api, fields, models, _

_logger = logging.getLogger(__name__)

# conexion = "dbname='ISEP' user='gmri' password='Gr5p4mr3'"
# conexion = "dbname='Isep_produccion_28_07' user='odoo'"
conexion = ''


def Compania():
    return 1


def Decodificar(texto):
    if texto is None:
        texto = '-'
    decoded_read_value = texto.decode('8859')
    read_value = decoded_read_value.encode('utf-8')
    read_value = read_value.replace("'", "")
    return read_value


def Dato(valor):
    if valor is None:
        return ''
    else:
        return valor


def eliminarAcentos(cadena):
    d = {'Â¦': '',
         'Ãƒ?Ã‚Â­':'',
         '\u0083':'',
         '\xc1':'A',
         '\xc9':'E',
         '\xcd':'I',
         '\xd3':'O',
         '\xda':'U',
         '\xdc':'U',
         '\xd1':'N',
         '\xc7':'C',
         '\xed':'i',
         '\xf3':'o',
         '\xf1':'n',
         '\xe7':'c',
         '\xba':'',
         '\xb0':'',
         '\x3a':'',
         '\xe1':'a',
         '\xe2':'a',
         '\xe3':'a',
         '\xe4':'a',
         '\xe5':'a',
         '\xe8':'e',
         '\xe9':'e',
         '\xea':'e',
         '\xeb':'e',
         '\xec':'i',
         '\xed':'i',
         '\xee':'i',
         '\xef':'i',
         '\xf2':'o',
         '\xf3':'o',
         '\xf4':'o',
         '\xf5':'o',
         '\xf0':'o',
         '\xf9':'u',
         '\xfa':'u',
         '\xfb':'u',
         '\xfc':'u',
         'Ã¡':'a',
         'Ã©':'e',
         'Ã­':'i',
         'Ã³':'o',
         'Ãº':'u',
         'Ã ':'a',
         'Ã©':'e',
         'Ã­':'i',
         'Ã³':'o',
         'Ãº':'u',
         'Ã':'A',
         'Ã‰':'E',
         'Ã':'I',
         'Ã“':'O',
         'Ãš':'U',
         'Ã€':'A',
         'Ãˆ':'E',
         'ÃŒ':'I',
         'Ã’':'O',
         'Ã™':'U',
         '\xe5':'a'
    }

    nueva_cadena = cadena
    nueva_cadena =nueva_cadena.replace("Ãƒ?","")
    for c in d.keys():
        if len(c)>1:
            nueva_cadena = nueva_cadena.replace(c,d[c])
    return nueva_cadena


def now():
    return datetime.datetime.now().time()


def UTF8(valor):
	return valor
    #return valor.encode('utf-8')


class WizardDummyGmri(models.TransientModel):
    _name = "wizard.dummy.gmri"

    def getCursor(self):
        return self._cr




cursor = None

def setCursor(cursor_ext):
    cursor = cursor_ext



class Presupuesto:
    def __init__(self):
        self.Id = 0
        self.Limpiar()

    def Limpiar(self):
        self.Id = 0
        self.PartnerID = 0
        self.Payment_Term_Id = 0
        self.PresupuestoId = 0
        self.PVP = 0
        self.PresupuestoId = ''
        self.PartnerId = 0
        self.Fecha = now()
        self.Observaciones = ''
        self.CompanyId = Compania()
        self.UserId = 0
        self.FechaPrimerRecibo = ''
        self.Matricula = 0
        self._PagosPorcentaje = 0.0
        self._PagosFijos = 0.0
        self.NumeroPago = 0
        self.Descuentos = 0.0
        self.DescuentoMatricula = 0.0
        self.IncrementoMatricula = 0.0
        self.Penalizacion = 0.0
        self.Porcentaje = 0.0
        self.Gastos = 0.0

    def LeerDatos(self):
        query = "select id, partner_id, payment_term_id, origin, amount_untaxed, id, date_order from sale_order where id="+str(self.Id)
        # print query
        cursor.execute(query)
        for row in cursor.fetchall():
            self.Id = row[0]
            self.PartnerId = row[1]
            self.Payment_Term_Id = row[2]
            if (self.Payment_Term_Id is None):
                    self.Payment_Term_Id = 1
            self.PresupuestoId = row[3]
            self.PVP = row[4]
            self.PresupuestoId = row[5]
            self.Fecha = row[6]


class EmpresaPedido:
    def __init__(self):
        self.Id = 0
        self.Limpiar()

    def Limpiar(self):
        self.Id = 0
        self.Nombre = ""
        self.Email = ""
        self.Identidad = 2

    def LeerDatos(self, id):
        self.Id = id
        query = "select name, email  from res_company where id="+str(self.Id)
        # Escribir(query)
        cursor.execute(query)
        for row in cursor.fetchall():
            self.Nombre = row[0]
            self.Email = row[1]
            self.Identidad = self.Id


class Usuario:
    def __init__(self):
        self.Id = 0
        self.Limpiar()

    def Limpiar(self):
        self.Id = 0
        self.Login = ""
        self.Email = ""

    def LeerDatos(self, id):
        self.Id = id
        query = "select login from res_users where id="+str(self.Id)
        # Escribir(query)
        cursor.execute(query)
        for row in cursor.fetchall():
            self.Login = row[0]


class Tablas:
    def __init__(self):
        self.Id = 0
        self.Limpiar()

    def Limpiar(self):
        self.Id = 0

    def LeerDatos(self, Tabla, Campo, Valor):
        query = "select "+Campo+" from "+Tabla+" where id="+str(Valor)
        cursor.execute(query)
        Retorno = ""
        for row in cursor.fetchall():
            Retorno = row[0]
        return Retorno


class FormaPago:
    def __init__(self):
        self.Id = 0

    def Codigo(self, valor):
        if valor is None:
            return "-"
        else:
            query = "select name from payment_acquirer where id="+str(valor)
            cursor.execute(query)
            retorno = "-"
            for row in cursor.fetchall():
                retorno = row[0]
            return retorno

    def Codigo2(self, valor):
        if valor is None:
            return "-"
        else:
            query = "select \"x_Codigo\" from payment_acquirer where id="+str(valor)
            cursor.execute(query)
            retorno = "-"
            for row in cursor.fetchall():
                retorno = row[0]
            return retorno


class Persona:
    def __init__(self):
        self.Id = 0
        self.Limpiar()

    def GetNombre(self):
        self.Nombre = self.Nombre.replace("'", "")
        self.Nombre = self.Nombre.replace(",", " ")
        self.Nombre = self.Nombre.replace("  ", " ")
        return self.Nombre

    def GetApellidos(self):
        self.Apellidos = self.Apellidos.replace("'", "")
        self.Apellidos = self.Apellidos.replace(",", " ")
        self.Apellidos = self.Apellidos.replace("  ", " ")
        return self.Apellidos

    def GetDisplayName(self):
        retorno = self.GetApellidos()
        if len(self.GetNombre()) > 0:
            retorno = retorno + ", " + self.GetNombre()
        return retorno

    def GetName(self):
        return self.GetNombre()+" "+self.GetApellidos()

    def GetEmail(self):
        return Decodificar(self.Email)

    def Limpiar(self):
        self.Nombre = ""
        self.Apellidos = ""
        self.Email = ""

    def LeerDatos(self, Id):
        query = "select  name, email from res_partner where id="+str(Id)
        cursor.execute(query)
        self.Limpiar()
        for row in cursor.fetchall():
            self.Apellidos = Dato(row[0].split(' ', 1)[1])
            self.Nombre = Dato(row[0].split(' ', 1)[0])
            self.Email = Dato(row[1])


class Telefonia:
    def __init__(self):
        self.Id = 0
        self.Limpiar()

    def GetTelefono(self):
        self.Telefono = Decodificar(self.Telefono)
        return self.Telefono

    def GetMovil(self):
        self.Movil = Decodificar(self.Movil)
        return self.Movil

    def GetFax(self):
        self.Fax = Decodificar(self.Fax)
        return self.Fax

    def Limpiar(self):
        self.Telefono = ""
        self.Movil = ""
        self.Fax = ""

    def LeerDatos(self, Id):
        query = "select phone, mobile, fax from res_partner where id="+str(Id)
        ## print query
        cursor.execute(query)
        self.Limpiar()
        for row in cursor.fetchall():
            self.Telefono = Dato(row[0])
            self.Movil = Dato(row[1])
            self.Fax = Dato(row[2])


class Country:
    def __init__(self):
        self.Id = 0
        self.Limpiar()

    def Limpiar(self):
        self.Id = 0
        self.Code = ""
        self.Name = ""

    def Buscar(self, name):
        self.Name = eliminarAcentos(name.decode('latin1').encode('utf8'))
        if self.Name == "EspaÃ±a":
            self.Name = "Spain"
        query = "select id from res_country where upper(name)=upper('"+self.Name+"')"
        cursor.execute(query)
        self.Id = 0
        for row in cursor.fetchall():
            self.Id = row[0]
        if (self.Id == 0):
            self.Code = self.Name[:2]
            query = "select id from res_country where upper(code)=upper('"+self.Code+"')"
            cursor.execute(query)
            for row in cursor.fetchall():
                self.Id = row[0]

    def BuscarId(self, id):
        self.Id = id
        query = "select name from res_country where id="+str(id)+""
        cursor.execute(query)
        for row in cursor.fetchall():
            self.Name = row[0]


class State:
    def __init__(self):
        self.Id = 0
        self.Limpiar()

    def Limpiar(self):
        self.Id = 0
        self.CountryId = 0
        self.Name = ""
        self.Code = ""

    def Buscar(self, name):
        self.Name = eliminarAcentos(name.decode('latin1').encode('utf8'))
        query = "select id from res_country_state where upper(name)=upper('"+self.Name+"') and country_id="+str(self.CountryId)
        cursor.execute(query)
        self.Id = 0
        for row in cursor.fetchall():
            self.Id = row[0]

    def BuscarId(self, id):
        self.Id = id
        query = "select name from res_country_state where id="+str(id)+""
        cursor.execute(query)
        for row in cursor.fetchall():
            self.Name = row[0]


# Datos recogidos de la tabla vtiger_contactaddress
class Direccion:
    def __init__(self):
        self.Limpiar()
        self._Pais = Country()
        self._State = State()

    def LeerDatos(self, Id):
        query = "select  street, city, zip, country_id, state_id,display_name, vat, \"x_tipodocumento\",\"x_documentoidentidad\" from res_partner where id="+str(Id)
        print query
        cursor.execute(query)
        self.Limpiar()
        for row in cursor.fetchall():
            self.Direccion = Dato(row[0])
            self.Poblacion = Dato(row[1])
            self.CodPostal = Dato(row[2])
            self._Pais.Id = Dato(row[3])
            self._State.Id = Dato(row[4])
            self.Provincia = self._State.Name
            self.Titular = Dato(row[5])
            self.NIF = Dato(row[6])
            if (self.NIF == ""):
                if (row[7] == 'DNI'):
                    self.TipoDocID = 1
                self.NIF = Dato(row[8])
            if (not(self._Pais.Id is None)) and len(str(self._Pais.Id)) > 0:
                # print "no tiene que entrar aqui"
                self._Pais.BuscarId(self._Pais.Id)
                self.Pais = self._Pais.Name
            if (not(self._State.Id is None)) and len(str(self._State.Id)) > 0:
                self._State.BuscarId(self._State.Id)
                self.Provincia = self._State.Name

    def GetCalle(self):
        self.Calle = Decodificar(self.Calle)
        self.Calle = self.Calle.replace("-----", "")
        return self.Calle

    def GetCiudad(self):
        self.Ciudad = Decodificar(self.Ciudad)
        return self.Ciudad

    def GetCP(self):
        self.CP = Decodificar(self.CP)
        self.CP = self.CP.replace("-----", "")
        return self.CP

    def GetProvincia(self):
        self.Provincia = Decodificar(self.Provincia)
        return self.Provincia

    def GetPais(self):
        self.Pais = Decodificar(self.Pais)
        return self.Pais

    def Limpiar(self):
        self.Calle = ""
        self.Ciudad = ""
        self.CP = ""
        self.Provincia = ""
        self.Pais = ""


class Isep:
    def __init__(self):
        self.Id = 0
        self.Limpiar()

    def GetAcepta(self):
        return self.Acepta

    def GetSexo(self):
        return self.Sexo

    def GetTipoContacto(self):
        return self.TipoContacto

    def GetEstudios(self):
        return self.Estudios

    def GetHorario(self):
        return self.Horario

    def GetDocumentoIdentidad(self):
        return self.DocumentoIdentidad

    def GetCentro(self):
        return self.Centro

    def GetFinalizacionEstudios(self):
        return self.FinalizacionEstudios

    def GetProfesion(self):
        return self.Profesion

    def GetAnyo(self):
        return self.Anyo

    def GetTipoDocumento(self):
        return self.TipoDocumento

    def Limpiar(self):
        self.Acepta = ""
        self.Sexo = ""
        self.TipoContacto = ""
        self.Estudios = ""
        self.Horario = ""
        self.DocumentoIdentidad = ""
        self.FechaNacimiento = ""
        self.Centro = ""
        self.FinalizacionEstudios = ""
        self.Profesion = ""
        self.Anyo = ""
        self.TipoDocumento = ""
        self.FechaNacimiento = ""

    def Validar(self):
        if self.Acepta == 'None':
            self.Acepta = 0
        if self.Sexo == 'None':
            self.Sexo = ""
        if self.TipoContacto == 'None':
            self.TipoContacto = ""
        if self.Estudios == 'None':
            self.Estudios = ""
        if self.Horario == 'None':
            self.Horario = ""
        if self.DocumentoIdentidad == 'None':
            self.DocumentoIdentidad = ""
        if self.Centro == 'None':
            self.Centro = ""
        if self.FinalizacionEstudios == 'None':
            self.FinalizacionEstudios = ""
        if self.Profesion == 'None':
            self.Profesion = ""
        if self.Anyo == 'None':
            self.Anyo = ""
        if self.TipoDocumento == 'None':
            self.TipoDocumento = ""

    def LeerDatos(self, Id):
        query = "select  x_aceptacondiciones, x_sexo, x_tipodecontacto,x_titulacion ,x_horarioid,x_documentoidentidad,x_universidad,x_finalizacionestudios  "\
        +",x_profesion ,x_annonacimiento ,x_tipodocumento, x_birthdate from res_partner where id="+str(Id)
        # print query
        #Escribir(query)
        cursor.execute(query)
        self.Limpiar()
        for row in cursor.fetchall():
            self.Acepta = Dato(row[0])
            self.Sexo = Dato(row[1])
            self.TipoContacto = Dato(row[2])
            self.Estudios = Dato(row[3])
            self.Horario = Dato(row[4])
            self.DocumentoIdentidad = Dato(row[5])
            self.Centro = Dato(row[6])
            self.FinalizacionEstudios = Dato(row[7])
            self.Profesion = Dato(row[8])
            self.Anyo = Dato(row[9])
            self.TipoDocumento = Dato(row[10])
            fecha = ""
            if Dato(row[11]) and Dato(row[11]) != "":
                fecha = Dato(row[11])[:4]+''+Dato(row[11])[5:7]+''+Dato(row[11])[8:]
            self.FechaNacimiento = fecha
            self.Validar()


class PresupuestocionPartner:
    def __init__(self):
        self.Limpiar()
        self._Pais = Country()
        self._State = State()

    def Limpiar(self):
        self.NIF = ""
        self.Titular = ""
        self.Direccion = ""
        self.Poblacion = ""
        self.CodPostal = ""
        self.Provincia = ""
        self.Pais = ""

    def Verificar(self):
        # print "Verificando"
        self.CP = ""

    def LeerDatos(self, Id):
        query = "select  street, city, zip, country_id, state_id,display_name, vat, \"x_tipodocumento\",\"x_documentoidentidad\" from res_partner where id="+str(Id)
        print query
        cursor.execute(query)
        self.Limpiar()
        for row in cursor.fetchall():
            self.Direccion = Dato(row[0])
            self.Poblacion = Dato(row[1])
            self.CodPostal = Dato(row[2])
            self._Pais.Id = Dato(row[3])
            self._State.Id = Dato(row[4])

            self.Provincia = self._State.Name
            self.Titular = Dato(row[5])
            self.NIF = Dato(row[6])
            if (self.NIF == ""):
                if (row[7] == 'DNI'):
                    self.TipoDocID = 1
                self.NIF = Dato(row[8])
            if (not(self._Pais.Id is None)) and len(str(self._Pais.Id)) > 0:
                # print "no tiene que entrar aqui"
                self._Pais.BuscarId(self._Pais.Id)
                self.Pais = self._Pais.Name
            if (not(self._State.Id is None)) and len(str(self._State.Id)) > 0:
                self._State.BuscarId(self._State.Id)
                self.Provincia = self._State.Name


class Partner:
    def __init__(self):
        self.Persona = Persona()
        self.Telefonia = Telefonia()
        self.Direccion = Direccion()
        self.ISEP = Isep()
        self.Presupuestocion = PresupuestocionPartner()
        self.Id = 0
        self.CompanyId = Compania()

    def Limpiar(self):
        self.Id = 0
        self.Persona.Limpiar()
        self.Telefonia.Limpiar()
        self.Direccion.Limpiar()
        self.ISEP.Limpiar()

    def LeerDatos(self):
        self.Persona.LeerDatos(self.Id)
        self.Telefonia.LeerDatos(self.Id)
        self.ISEP.LeerDatos(self.Id)
        self.Direccion.LeerDatos(self.Id)
        self.Presupuestocion.LeerDatos(self.Id)


class PresupuestoLine:
    def __init__(self):
        self.Id = 0
        self.Limpiar()

    def Limpiar(self):
        self.Id = 0
        self.Descuento = 0
        self.DescuentoMatricula = 0
        self.IncrementoMatricula = 0
        self.PVP = 0
        self.Cantidad = 0
        self.PresupuestoId = 0

    def LeerDatos(self):
        query = "select a.id, a.product_uom_qty, a.price_total, a.discount, p.default_code  from sale_order_line  a left  join product_product p  on a.product_id=p.id where a.order_id="+str(self.PresupuestoId)
        cursor.execute(query)
        for row in cursor.fetchall():
            self.Id = row[0]
            self.Cantidad = row[1]
            if (row[3] > 0):
                self.Descuento = self.Descuento + ((row[2]*row[3])/100)
            if (row[2] < 0):
                self.DescuentoMatricula = self.DescuentoMatricula+row[2]
            else:
                self.PVP = self.PVP+(row[1]*row[2])
            if (row[4] == "Gastos"):
                self.IncrementoMatricula = self.IncrementoMatricula+row[2]


class TerminoPago:
    def __init__(self):
        self.Id = 0
        self.Limpiar()

    def Limpiar(self):
        self.Id = 0
        self.Nombre = ""
        self.Penalizacion = 0
        self.Porcentaje = 0

    def LeerDatos(self):
        query = "select name, \"x_Penalizacion\", \"x_Penalizacion_Porcentaje\" from account_payment_term where id="+str(self.Id)
        # print query
        cursor.execute(query)
        for row in cursor.fetchall():
            self.Nombre = row[0]
            self.Penalizacion = row[1]
            self.Porcentaje = row[2]


class WebService:

    def __init__(self):
        self.Id = 0
        self._Presupuesto = Presupuesto()
        self._empresa = EmpresaPedido()
        self._usuario = Usuario()
        self.Tabla = Tablas()
        self._FormaPago = FormaPago()
        self.Limpiar()

    def Limpiar(self):
        self.Id = 0
        self.PartnerId = 0
        self.PartnerIdInvoice = 0
        self.CRMUsuario = ''
        self.CRMIDPedido = 0
        self.TipoDocID = 0
        self.DocID = ""
        self.Apellidos = ""
        self.Nombres = ""
        self.Sexo = ""
        self.FechaNacimiento = ""
        self.Profesion = ""
        self.Estudios = ""
        self.CentroEstudios = ""
        self.AnyFinalizacionEstudios = 0
        self.Telefono = ""
        self.Movil = ""
        self.Fax = ""
        self.EMail = ""
        self.Direccion = ""
        self.Poblacion = ""
        self.CodPostal = ""
        self.Provincia = ""
        self.Pais = ""
        self.EnvioDireccion = ""
        self.EnvioPoblacion = ""
        self.EnvioCodPostal = ""
        self.EnvioProvincia = ""
        self.EnvioPais = ""
        self.EnvioHoraEntrega = ""
        self.CodIdentidad = ""
        self.Identidad = ""
        self.CRMServerPath = ""
        self.CodArea = ""
        self.Area = ""
        self.CodTipoCurso = ""
        self.GrupoPreferencia = ""
        self.TipoCurso = ""
        self.CodCurso = ""
        self.Curso = ""
        self.CodModalidad = ""
        self.Modalidad = ""
        self.CodSede = ""
        self.Sede = ""
        self.AnyAcademico = 0
        self.FechaMatricula = ""
        self.HorarioPreferencia = ""
        self.Observaciones = ""
        self.FormaPago = ""
        self.CuentaBancaria = ""
        self.TarjetaCredito = ""
        self.CaducidadTarjetaCredito = ""
        self.CobroExterno = 0
        self.PVP = 0.0
        self.Descuentos = 0.0
        self.DescuentoMatricula = 0.0
        self.IncrementoMatricula = 0.0
        self.Penalizacion = 0.0
        self.ImporteTotalFraccionado = 0.0
        self.ImporteMatricula = 0.0
        self.RestoRecibos = 0
        self.ImporteRecibos = 0.0
        self.ImporteUltimoRecibo = 0.0
        self.FechaPrimerRecibo = None
        self.PagaYSenyal = 0.0
        self.DeseaPresupuesto = 0
        self.NIF = ""
        self.PresupuestoNIF = ""
        self.PresupuestoTitular = ""
        self.PresupuestoDireccion = ""
        self.PresupuestoPoblacion = ""
        self.PresupuestoCodPostal = ""
        self.PresupuestoProvincia = ""
        self.PresupuestoPais = ""
        self.FormaPagoMatricula = "-"
        self.FormaPagoRecibos = "-"
        self.TipoPagoId = 0
        self.MoveId = 0
        self.Matricula = 0
        self.Total = 0

    def Error(self, id):
        # self.GenerarMove(48)
        print ("HAY ERROR")

    def Buscar(self):
        query = "select id, partner_id, x_pago_id, Company_id, amount_total, \"x_Paga_y_Senyal\" , user_id , \"x_Fecha_Primer_Recibo\",\"x_Anyo_Academico\",\"x_Matricula_Fecha_Pago\",\"x_CCC\",\"x_Tarjeta\",\"x_Mes\",\"x_Anyo\",\"x_Matricula_Forma_Pago\",\"x_Recibo_Forma_Pago\",partner_invoice_id,\"x_Desea_Factura\" from sale_order where id="+str(self.Id)
        print "******** BUSCAR"
        print str(query)
        cursor.execute(query)
        for row in cursor.fetchall():
            self.Id = row[0]
            self.PartnerId = row[1]
            self.PartnerIdInvoice = row[16]
            self.MoveId = row[2]
            self.CompanyId = row[3]
            self.Total = row[4]
            self.Matricula = row[5]
            self.UserId = row[6]
            self.FechaPrimerRecibo = row[7]
            self.AnyAcademico = row[8]
            self.FechaMatricula = row[9]
            self.CuentaBancaria = row[10]
            self.TarjetaCredito = row[11]
            if row[12] is None:
                self.Mes = '01'
            else:
                if (row[12] < 10):
                    self.Mes = '0'+str(row[12])
                    if (row[12] == 0):
                        self.Mes = '01'
                else:
                    self.Mes = str(row[12])
            if row[13] is None:
                self.Anyo = '2000'
            else:
                self.Anyo = str(row[13])
                if self.Anyo == '0':
                    self.Anyo = '2000'
            self.FormaPagoMatricula = self._FormaPago.Codigo(row[14])
            self.FormaPagoRecibos = self._FormaPago.Codigo(row[15])

            if (row[17]):
                self.DeseaPresupuesto = 1
            self.CaducidadTarjetaCredito = self.Anyo+self.Mes+'01'
            try:
                datetime.datetime.strptime(self.CaducidadTarjetaCredito, '%Y-%m-%d')
            except ValueError:
                self.CaducidadTarjetaCredito = '20020101'

        self.LeerPresupuesto()
        self.LeerPartner()
        if self.PartnerId != self.PartnerIdInvoice:
            self.LeerPartnerInvoice()

    def LeerPresupuesto(self):
        self._Presupuesto.Id = self.Id
        self._Presupuesto.LeerDatos()
        self.PVP = self._Presupuesto.PVP
        self.Observaciones = self._Presupuesto.Observaciones
        _Presupuestoline = PresupuestoLine()
        _Presupuestoline.PresupuestoId = self._Presupuesto.Id
        _Presupuestoline.LeerDatos()
        self.IncrementoMatricula = _Presupuestoline.IncrementoMatricula
        self.PVP = _Presupuestoline.PVP
        self._Presupuesto.PVP = self.PVP
        _pago = TerminoPago()
        if not(self._Presupuesto.Payment_Term_Id is None):
            _pago.Id = self._Presupuesto.Payment_Term_Id
            _pago.LeerDatos()
            if _pago.Penalizacion > 0:
                self.IncrementoMatricula = _pago.Penalizacion
            if _pago.Porcentaje > 0:
                self.IncrementoMatricula = (Decimal(self.PVP) * Decimal(_pago.Porcentaje))/100
            self.TipoPagoId = self._Presupuesto.Payment_Term_Id
        self.Descuentos = self.DescuentoSobreTotal()
        self.DescuentoMatricula = self.DescuentoSobreMatricula()

    def DescuentoSobreTotal(self):
        query = "select sum(price_total) from sale_order_line where order_id="+str(self.Id)+" and product_id in (select id from product_product where product_tmpl_id in (select id from product_template where x_tipodecurso=8))"
        cursor.execute(query)
        Retorno = 0
        for row in cursor.fetchall():
            try:
                Retorno = Retorno + Decimal(row[0])
            except:
                Retorno = Retorno + 0
        return Retorno

    def DescuentoSobreMatricula(self):
        query = "select sum(price_total) from sale_order_line where order_id="+str(self.Id)+" and product_id in (select id from product_product where product_tmpl_id in (select id from product_template where x_tipodecurso=9))"
        cursor.execute(query)
        Retorno = 0
        for row in cursor.fetchall():
            try:
                Retorno = Retorno + Decimal(row[0])
            except:
                Retorno = Retorno + 0
        return Retorno

    def LeerPartnerNif(self):
        _partner = Partner()
        if self.PartnerId == self.PartnerIdInvoice:
            _partner.Id = self.PartnerId
        else:
            _partner.Id = self.PartnerIdInvoice
        _partner.LeerDatos()
        return _partner.Presupuestocion.NIF

    def LeerPartner(self):
        _partner = Partner()
        _partner.Id = self.PartnerId
        _partner.LeerDatos()

        self.DocID = ""
        self.Apellidos = _partner.Persona.Apellidos
        self.Nombres = _partner.Persona.Nombre
        self.Sexo = _partner.ISEP.Sexo
        self.FechaNacimiento = str(_partner.ISEP.FechaNacimiento)
        self.Profesion = _partner.ISEP.Profesion
        self.Estudios = _partner.ISEP.Estudios
        self.Centro = _partner.ISEP.Centro
        self.CentroEstudios = _partner.ISEP.Centro
        self.AnyFinalizacionEstudios = _partner.ISEP.FinalizacionEstudios
        self.Telefono = _partner.Telefonia.Telefono
        self.Movil = _partner.Telefonia.Movil
        self.Fax = _partner.Telefonia.Fax
        self.EMail = _partner.Persona.Email
        self.Direccion = _partner.Direccion.Calle
        self.Poblacion = _partner.Direccion.Ciudad
        self.CodPostal = _partner.Direccion.CP
        self.Provincia = _partner.Direccion.Provincia
        self.Pais = _partner.Direccion.Pais
        self.EnvioDireccion = _partner.Direccion.Calle
        self.EnvioPoblacion = _partner.Direccion.Ciudad
        self.EnvioCodPostal = _partner.Direccion.CP
        self.EnvioProvincia = _partner.Direccion.Provincia
        self.EnvioPais = _partner.Direccion.Pais
        self.NIF = _partner.Presupuestocion.NIF
        self.PresupuestoNIF = _partner.Presupuestocion.NIF
        self.PresupuestoTitular = _partner.Presupuestocion.Titular
        self.PresupuestoDireccion = _partner.Presupuestocion.Direccion
        self.PresupuestoPoblacion = _partner.Presupuestocion.Poblacion
        self.PresupuestoCodPostal = _partner.Presupuestocion.CodPostal
        self.PresupuestoProvincia = _partner.Presupuestocion.Provincia
        self.PresupuestoPais = _partner.Presupuestocion.Pais

    def LeerPartnerInvoice(self):
        _partnerinvoice = Partner()
        _partnerinvoice.Id = self.PartnerIdInvoice
        _partnerinvoice.LeerDatos()

        self.PresupuestoNIF = _partnerinvoice.Presupuestocion.NIF
        self.PresupuestoTitular = _partnerinvoice.Presupuestocion.Titular
        self.PresupuestoDireccion = _partnerinvoice.Presupuestocion.Direccion
        self.PresupuestoPoblacion = _partnerinvoice.Presupuestocion.Poblacion
        self.PresupuestoCodPostal = _partnerinvoice.Presupuestocion.CodPostal
        self.PresupuestoProvincia = _partnerinvoice.Presupuestocion.Provincia
        self.PresupuestoPais = _partnerinvoice.Presupuestocion.Pais

    def Corregir(self):
        if self.PartnerId is None:
            self.PartnerId = 0
        if self.CRMUsuario is None:
            self.CRMUsuario = ''
        if self.CRMIDPedido is None:
            self.CRMIDPedido = 0
        if self.TipoDocID is None:
            self.TipoDocID = 0
        if self.DocID is None:
            self.DocID = ""
        if self.Apellidos is None:
            self.Apellidos = ""
        if self.Nombres is None:
            self.Nombres = ""
        if self.Sexo is None:
            self.Sexo = ""
        if self.FechaNacimiento is None:
            self.FechaNacimiento = ""
        if self.Profesion is None:
            self.Profesion = ""
        if self.Estudios is None:
            self.Estudios = ""
        if self.CentroEstudios is None:
            self.CentroEstudios = ""
        if self.AnyFinalizacionEstudios is None:
            self.AnyFinalizacionEstudios = 0
        else:
            try:
                val = int(self.AnyFinalizacionEstudios)
            except ValueError:
                self.AnyFinalizacionEstudios = 2000
        if self.Telefono is None:
            self.Telefono = ""
        if self.Movil is None:
            self.Movil = ""
        if self.Fax is None:
            self.Fax = ""
        if self.EMail is None:
            self.EMail = ""
        if self.Direccion is None:
            self.Direccion = ""
        if self.Poblacion is None:
            self.Poblacion = ""
        if self.CodPostal is None:
            self.CodPostal = ""
        if self.Provincia is None:
            self.Provincia = ""
        if self.Pais is None:
            self.Pais = ""
        if self.EnvioDireccion is None:
            self.EnvioDireccion = ""
        if self.EnvioPoblacion is None:
            self.EnvioPoblacion = ""
        if self.EnvioCodPostal is None:
            self.EnvioCodPostal = ""
        if self.EnvioProvincia is None:
            self.EnvioProvincia = ""
        if self.EnvioPais is None:
            self.EnvioPais = ""
        if self.EnvioHoraEntrega is None:
            self.EnvioHoraEntrega = ""
        if self.CodIdentidad is None:
            self.CodIdentidad = ""
        if self.Identidad is None:
            self.Identidad = ""
        if self.CRMServerPath is None:
            self.CRMServerPath = ""
        if self.CodArea is None:
            self.CodArea = ""
        if self.Area is None:
            self.Area = ""
        if self.CodTipoCurso is None:
            self.CodTipoCurso = ""
        if self.TipoCurso is None:
            self.TipoCurso = ""
        if self.CodCurso is None:
            self.CodCurso = ""
        if self.Curso is None:
            self.Curso = ""
        if self.FormaPago is None:
            self.FormaPago = ""
        if self.PresupuestoCodPostal is None:
            self.PresupuestoCodPostal = ""
        if self.PresupuestoDireccion is None:
            self.PresupuestoDireccion = ""
        if self.CodModalidad is None:
            self.CodModalidad = ""
        if self.Modalidad is None:
            self.Modalidad = ""
        if self.CodSede is None:
            self.CodSede = ""
        if self.Sede is None:
            self.Sede = ""
        if self.AnyAcademico is None:
            self.AnyAcademico = 0
        if self.FechaMatricula is None:
            self.FechaMatricula =  now()
        if self.HorarioPreferencia is None:
            self.HorarioPreferencia = ""
        if self.Observaciones is None:
            self.Observaciones = ""
        if self.FormaPago is None:
            self.FormaPago = ""
        if self.CuentaBancaria is None:
            self.CuentaBancaria = ""
        if self.TarjetaCredito is None:
            self.TarjetaCredito = ""
        if self.CaducidadTarjetaCredito is None:
            self.CaducidadTarjetaCredito = ""
        else:
            try:
                datetime.datetime.strptime(self.CaducidadTarjetaCredito, '%Y-%m-%d')
            except ValueError:
                self.CaducidadTarjetaCredito = '20100101'

        if self.CobroExterno is None:
            self.CobroExterno = 0
        if self.PVP is None:
            self.PVP = 0.0
        if self.Descuentos is None:
            self.Descuentos = 0.0
        if self.Penalizacion is None:
            self.Penalizacion = 0.0
        if self.ImporteTotalFraccionado is None:
            self.ImporteTotalFraccionado = 0.0
        if self.ImporteMatricula is None:
            self.ImporteMatricula = 0.0
        if self.RestoRecibos is None:
            self.RestoRecibos = 0
        if self.ImporteRecibos is None:
            self.ImporteRecibos = 0.0
        if self.ImporteUltimoRecibo is None:
            self.ImporteUltimoRecibo = 0.0
        if self.FechaPrimerRecibo is None:
            self.FechaPrimerRecibo = ""
        if self.PagaYSenyal is None:
            self.PagaYSenyal = 0.0
        if self.DeseaPresupuesto is None:
            self.DeseaPresupuesto = 0
        if self.PresupuestoNIF is None:
            self.PresupuestoNIF = ""
        if self.NIF is None:
            self.NIF = ""
        if self.PresupuestoTitular is None:
            self.PresupuestoTitular = ""
        if self.PresupuestoDireccion is None:
            self.PresupuestoDireccion = ""
        if self.PresupuestoPoblacion is None:
            self.PresupuestoPoblacion = ""
        if self.PresupuestoCodPostal is None:
            self.PresupuestoCodPostal = ""
        if self.PresupuestoProvincia is None:
            self.PresupuestoProvincia = ""
        if self.PresupuestoPais is None:
            self.PresupuestoPais = ""

    def Aplicacion(self, id, cursor_ext):
        #try :
        global cursor
        cursor = cursor_ext
        self.Id = id
        self.Buscar()
        self._empresa.LeerDatos(self.CompanyId)
        self._usuario.LeerDatos(self.UserId)
        self.CRMUsuario = self._usuario.Login
        self.OpportunityId = self.Tabla.LeerDatos("sale_order", "opportunity_id", str(self.Id))

        query = "select x_tipodedocumento, x_documentodeidentidad, x_codarea, x_codCurso, x_tipodecurso_id , x_area_id, x_sede_id, x_modalidad_id from crm_lead where id ="+str(self.OpportunityId)
        cursor.execute(query)
        for row in cursor.fetchall():
            if (self.NIF == ""):
                self.TipoDocID = row[0]
                if self.TipoDocID == 'DNI':
                    self.TipoDocID = 1
                self.NIF = row[1]

            if (self.NIF == ""):
                self.NIF = row[1]
            if (self.NIF == ""):
                self.NIF = self.LeerPartnerNif()

            self.CodArea = row[2]
            self.CodTipoCurso = row[3]
            self.CodTipoCurso = self.Tabla.LeerDatos("x_crmtipodecurso", "x_codigotipodecurso", row[4])
            self.TipoCurso = self.Tabla.LeerDatos("x_crmtipodecurso", "x_name", row[4])
            self.Area = self.Tabla.LeerDatos("product_category", "name", row[5])
            self.CodSede = self.Tabla.LeerDatos("product_attribute_value", "name", row[6])
            self.Sede = self.Tabla.LeerDatos("product_attribute_value", "x_descripcion", row[6])
            self.CodModalidad = self.Tabla.LeerDatos("product_attribute_value", "name", row[7])
            self.Modalidad = self.Tabla.LeerDatos("product_attribute_value", "x_descripcion", row[7])

        query = "select p.default_code, p.name_template, a.grupo_referencia  from sale_order_line  a left  join product_product p  on a.product_id=p.id, product_template as pt where pt.id = p.product_tmpl_id and a.order_id="+str(self.Id)+" and pt.tipodecurso  in ('curso', 'pgrado', 'diplo', 'mgrafico', 'master') limit 10"
        # Escribir(query)
        cursor.execute(query)
        i = 0
        for row in cursor.fetchall():
            self.CodCurso = row[0]
            self.Curso = row[1]
            self.GrupoPreferencia = row[2]
            if i == 0:
                self.CRMIDPedido = self.Id
            else:
                self.CRMIDPedido = str(self.Id+i)
            self.InsertarLineas()
            i += 1

    def InsertarLineas(self):
        print (" INSERTANDO LINEAS")
        self.Identidad = self._empresa.Identidad
        self.CodIdentidad = self._empresa.Nombre

        print (self.CodIdentidad)
        print (self.Identidad)
        self.CRMServerPath = self._empresa.Email
        if (self.FechaPrimerRecibo is None):
            print ("NO HAY FECHA PARA EL PRIMER RECIBO")
            self.FechaPrimerRecibo = self.FechaMatricula
        if (self.AnyFinalizacionEstudios is None):
            self.AnyFinalizacionEstudios = 1900

        self.Corregir()
        try:
            datetime.datetime.strptime(self.CaducidadTarjetaCredito, '%Y-%m-%d')
        except ValueError:
            self.CaducidadTarjetaCredito = '20100101'

        sql = " exec gin_ws_insertPreMatricula_Odoo  "
        sql += "@in_CRMUsuario='" + UTF8(str(self.CRMUsuario))+"',"
        sql += "@in_CRMIDPedido=" + UTF8(str(self.CRMIDPedido))+","
        sql += "@in_TipoDocID='" + UTF8(str(self.TipoDocID))+"',"
        sql += "@in_DocID='" + UTF8(self.NIF)+"',"
        sql += "@in_Apellidos='" + UTF8(self.Apellidos)+"',"
        sql += "@in_Nombres='" + UTF8(self.Nombres)+"',"
        sql += "@in_Sexo='" + UTF8(self.Sexo)+"',"
        sql += "@in_FechaNacimiento='" + UTF8(str(self.FechaNacimiento))+"',"
        sql += "@in_Profesion='" + UTF8(self.Profesion)+"',"
        sql += "@in_Estudios='" + UTF8(self.Estudios)+"',"
        sql += "@in_CentroEstudios='" + UTF8(self.CentroEstudios)+"',"
        sql += "@in_AnyFinalizacionEstudios=" + UTF8(str(self.AnyFinalizacionEstudios))+","
        sql += "@in_Telefono='" + UTF8(self.Telefono)+"',"
        sql += "@in_Movil='" + UTF8(self.Movil)+"',"
        sql += "@in_Fax='" + UTF8(self.Fax)+"',"
        sql += "@in_EMail='" + UTF8(self.EMail)+"',"
        sql += "@in_Direccion='" + UTF8(self.Direccion)+"',"
        sql += "@in_Poblacion='" + UTF8(self.Poblacion)+"',"
        sql += "@in_CodPostal='" + UTF8(self.CodPostal)+"',"
        sql += "@in_Provincia='" + UTF8(self.Provincia)+"',"
        sql += "@in_Pais='" + UTF8(self.Pais)+"',"
        sql += "@in_EnvioDireccion='" + UTF8(self.Direccion)+"',"  # + UTF8(self.EnvioDireccion)+"',"
        sql += "@in_EnvioPoblacion='" + UTF8(self.Poblacion)+"',"  # + UTF8(self.EnvioPoblacion)+"',"
        sql += "@in_EnvioCodPostal='" + UTF8(self.CodPostal)+"',"  # + UTF8(self.EnvioCodPostal)+"',"
        sql += "@in_EnvioProvincia='" + UTF8(self.Provincia)+"',"  # + UTF8(self.EnvioProvincia)+"',"
        sql += "@in_EnvioPais='" + UTF8(self.Pais)+"',"  # + UTF8(self.EnvioPais)+"',"
        sql += "@in_EnvioHoraEntrega='" + UTF8(self.EnvioHoraEntrega)+"',"
        sql += "@in_CodIdentidad='" + UTF8(str(self.CodIdentidad))+"',"
        sql += "@in_Identidad='" + UTF8(str(self.Identidad))+"',"
        sql += "@in_CRMServerPath='" + UTF8(self.CRMServerPath)+"',"
        sql += "@in_CodArea='" + UTF8(self.CodArea)+"',"
        sql += "@in_Area='" + UTF8(self.Area)+"',"
        sql += "@in_CodTipoCurso='" + UTF8(self.CodTipoCurso)+"',"
        sql += "@in_TipoCurso='" + UTF8(self.TipoCurso)+"',"
        sql += "@in_CodCurso='" + UTF8(self.CodCurso)+"',"
        sql += "@in_Curso='" + UTF8(self.Curso)+"',"
        sql += "@in_CodModalidad='" + UTF8(self.CodModalidad)+"',"
        sql += "@in_Modalidad='" + UTF8(self.Modalidad)+"',"
        sql += "@in_CodSede='" + UTF8(self.CodSede)+"',"
        sql += "@in_Sede='" + UTF8(self.Sede)+"',"
        sql += "@in_AnyAcademico=" + UTF8(str(self.AnyAcademico))+","
        sql += "@in_HorarioPreferencia='" + UTF8(self.HorarioPreferencia)+"',"
        sql += "@in_Observaciones='" + UTF8(self.Observaciones)+"',"
        sql += "@in_GrupoPreferencia='" + UTF8(self.GrupoPreferencia or '')+"',"
        # Lo comentado es la parte de pagos Se pasa todo vacio.

        sql += "@in_FormaPago=0,"
        sql += "@in_CuentaBancaria='" + UTF8(self.CuentaBancaria)+"',"
        sql += "@in_TarjetaCredito='" + UTF8(self.TarjetaCredito)+"',"
        sql += "@in_CaducidadTarjetaCredito='" + UTF8(str.replace(str(self.CaducidadTarjetaCredito), "-", ""))+"',"
        sql += "@in_CobroExterno=0,"
        sql += "@in_PVP=0,"
        sql += "@in_Descuentos=0,"
        sql += "@in_Penalizacion=0,"
        sql += "@in_ImporteTotalFraccionado=0,"
        sql += "@in_ImporteMatricula=0,"
        sql += "@in_RestoRecibos=0,"
        sql += "@in_ImporteRecibos=0,"
        sql += "@in_ImporteUltimoRecibo=0,"
        sql += "@in_FechaPrimerRecibo=0,"
        sql += "@in_PagaYSenyal=0,"
        sql += "@in_DeseaFactura=0,"
        sql += "@in_FacturaNIF='" + UTF8(self.PresupuestoNIF)+"',"
        sql += "@in_FacturaTitular='" + UTF8(self.PresupuestoTitular)+"',"
        sql += "@in_FacturaDireccion='" + UTF8(self.PresupuestoDireccion)+"',"
        sql += "@in_FacturaPoblacion='" + UTF8(self.PresupuestoPoblacion)+"',"
        sql += "@in_FacturaCodPostal='" + UTF8(self.PresupuestoCodPostal)+"',"
        sql += "@in_FacturaProvincia='" + UTF8(self.PresupuestoProvincia)+"',"
        sql += "@in_FacturaPais='" + UTF8(self.PresupuestoPais)+"',"
        sql += "@in_Pack=0"
        print "--->>> SQL envio aplicacion"
        _logger.info(sql)
    #     self.Send_SQL(sql)

    # def Send_SQL(self, sql):

    #     dsn = 'egServer70source'

    #     user = 'sa'
    #     password = 'Gr5p4mr3'
    #     database = 'GrupoISEPxtra'

    #     con_string = 'DSN=%s;UID=%s;PWD=%s;DATABASE=%s;' % (dsn, user, password, database)

    #     # con_string = 'DSN=85.118.244.220;UID=sa;PWD=Gr5p4mr3;DATABASE=GrupoISEPxtra;'
    #     cnxn = pyodbc.connect(con_string)
    #     # cnxn = pyodbc.connect(server='85.118.244.220',UID='sa',PWD='Gr5p4mr3',DATABASE='GrupoISEPxtra')
    #     cursorsql = cnxn.cursor()
    #     _logger.info(sql)
    #     cursorsql.execute(eliminarAcentos(sql))
    #     cnxn.commit()
