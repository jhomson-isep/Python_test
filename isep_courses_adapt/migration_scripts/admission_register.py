# -*- coding: utf-8 -*-

from datetime import date, datetime
from sqlachemy_conn import *

session_pg = get_pg_session()


def update_start_date():
    """
    Función creada con el fin de actualizar la fecha de inicio (start_date)
    a los registros de admisión (op_admission_register) que inician a una
    fecha superior o igual a hoy. Esto generaba una incidencia al matricular
    un alumno debifo a las restricciones de Odoo
    """
    today = date.today()
    start_date = datetime.strptime('2020-12-30', '%Y-%m-%d')
    admission_registers = session_pg.query(OpAdmissionRegister).filter(
        OpAdmissionRegister.start_date >= today).all()

    for admission_register in admission_registers:
        try:
            admission_register.start_date = start_date.date()
            session_pg.commit()
            print("Course updated: ", admission_register.name)
        except Exception as e:
            print(e)
            continue


if __name__ == "__main__":
    update_start_date()
