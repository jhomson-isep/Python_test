# -*- coding: utf-8 -*-

from odoo import models, fields

class ResUsers(models.Model):
    _inherit = 'res.users'

    is_commercial = fields.Boolean(string='Is commercial', default=False)

#Se importa de odoo models, fields, se va a trabajar con campos
#Se crea una clase de nombre ResUsers(usando la clase Model del objeto models ya importado)
#_inherit = 'res_user' indica que la clase hereda las propiedades y metodos de la clase res.users ya existente en odoo
#is_commercial es el campo booleano que se desea mostrar en un modulo particular.
#Del objeto fields se obtiene el tipo Boolean y en sus atributos se establece
#(string='Titulo que lleva el campo', default=Opcion por defecto para el campo)

#En este momento se acaba de crear el modelo que sirve para insertar en el modulo que deseemos
#Ahora falta colocarle una vista para que se vea en el modulo que deseemos, para eso se deben ubicar
#El id del modulo donde se va a insertar el nuevo modelo y el grupo donde se va a insertar

#La vista o view sirve para visualizar el elemento en el modulo que deseemos, este se condigura con un
#archivo de extension xml en la carpeta views, si no existe debe crearse con el mismo nombre que el modelo
#que se esta creando, si es users.py entonces la vista seria views.py

#Una vez configuardo el view se deben hacer referencia al mismo en el archivo __init.py de la carpeta models
#asi como en el archivo manifest.py de la carpeta views, de esta forma si se podra ver correctamente

#Se debe saber donde se ubica cada elemento en la interfaz odoo, para esto se configura el xml en la carpeta
#views, dependiendo como se vaya a colocar se debe configurar el tipo de elemento asi como donde se desea
#colocar en pantalla.

#Buscar el id de cada modulo es el saunto mas complicado hasta ahora, se recomienda analizar el codigo
#fuente del modulo que se quiere editar para ubicar el group y el id al que se va a hacer referencia y
#ubicar el elemento antes o despues en pantalla, para esto debes iniciar el odoo en DEBUG!.

#En debug puedes buscar vistas, modelos, objetos, escribiendolo en la barra de busqueda en la pantalla
#central, alli busca y comprueba que se esten cargando tus vistas y modelos nuevos sin problema.

#Cada vez que cargues una vista o modelo nuevo debes reiniciar el servicio odoo para observar los
#nuevos cambios, ahora sobre los views...

#Los views dentro de la etiqueta data siempre tienen la etiqueta record donde hacen referencia al
#id que va a identificar la nueva vista, y el modelo que usara para obtener las propiedades de view.

#Luego vienen los fields:
#Field name: Nombre de la vista
#Field model: nombre del modelo que usa la vista
#Field inherit: modelo de donde hereda las propieades la vista, en el caso de una vista
#es base.view_users_form
#Field arch: de tipo xml, es la arquitectura con la que trabaja la vista

#Posteriormente se declara la etiqueta xpath, donde se van a definir la posicion y referencia del 
#nuevo modelo y vista creados

#<xpath expr="//group[@name='messaging']" position="before">
#                    <group string="Isep" name="isep">
#                        <field name="is_commercial"/>
#                    </group>
#                </xpath>

#                <xpath expr="//field[@name='signature']" position="after">
#                    <field name="is_commercial"/>
#                </xpath>

#Aca se establece un xpath del tipo group asociado al id del grupo messaging, y que este se coloque antes
#de dicho grupo, es decir, el nuevo elemento se ubicara antes de los elementos del grupo messaging.

#En el caso del field con id signature significa que directamente el field y model is_commercial se
#ubicaran directamente despues del field con id signature, sin necesidad de declarar un grupo en particular