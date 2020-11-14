# -*- coding: utf-8 -*-


#1715069;711057;410202;1141;3714
#1744437;777171;438163;1170;3712
#1744450;777177;438173;1135;3700

import pyodbc
import psycopg2
import MySQLdb
import pprint
import datetime
from numeros import *	
def Escribir(texto):
	
	if 1==1:	
		print texto
class Grabar:
	def __init__(self):
		self.GrabarLead=""
		self.GrabarPartner=""
		self.GrabarSale=""
		self.GrabarProducto=""
		self.Grabar=False
		
	def Limpiar(self):
		self.GrabarLead=""
		self.GrabarPartner=""
		self.GrabarSale=""
		self.GrabarProducto=""
		self.Grabar=False	
		
class Partner:
	def __init__(self):
		self.Id=0
		
	
	def Limpiar(self):
		self.g.Limpiar()
	
	def LeerDatos(self, idinicial, idfinal):
		sql="select * from crm_lead where  partner_id in ("+str(idinicial)+","+str(idfinal)+")"
		Escribir(sql) 
		#cursor.execute(sql)
		
		#for row in cursor.fetchall():
		#	Escribir(row[0])
			
			
		
		
			
conexion="dbname='ISEP' user='isep_mexico' host='app.isep.com' password='Gr5p43s2p'"

#host=app.isep.com dbname=ISEP user=isep_mexico password=Gr5p43s2p

conn = psycopg2.connect(conexion)
cursor = conn.cursor()


consulta =" select importe,id from isep_pagoslineas order by id desc "

cursor.execute(consulta)
#partner.execute(query_partner)
#sale.execute(query_sale)


conn2= psycopg2.connect(conexion)
conn2.autocommit = True
cursor_g=conn2.cursor()



texto=""

Encontrado=False
for row in cursor.fetchall():
	importe= row[0] 
	id1 = row[1]
	print importe
	print numero_a_letras(importe)
	sql = "update isep_pagoslineas set  \"ImporteTexto\"='"+numero_a_letras(importe)+"' where id="+str(id1)
	print sql
	cursor_g.execute(sql)
	print "************"


	

	
	