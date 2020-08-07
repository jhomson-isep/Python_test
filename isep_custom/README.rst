Customización CRM para ISEP
============================================================

Antes de instalar
* Se tiene que cambiar el archivo models/gmri.py en la linea 10 aproximada esta la variable conexion, se tiene que adaptar a la instancia.


Despues de instalar

* Se tiene que buscar el informe Hoja Prematrícula de sale.order y cambiarle el Nombre de la plantilla  por isep_custom.report_sale_presupuesto y añadirlo al menu de imprimir.
* Se debe de realizar la configuración de cuentas de los productos:
	* 7000 --> Importe de curso + Importe de Matrícula
	* 770  --> Importes de descuentos
	* 709 ---> Gastos Administrativos (Recargos)


Funcionalidad:
--------------

* Modifica la ficha de partner con campos personalizados.
