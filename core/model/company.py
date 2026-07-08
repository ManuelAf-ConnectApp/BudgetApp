#
# Author: Manuel Maria Alconchel Fernandez
# E-mail: incidencias@connectapp.es
# Date: 30/06/2026
#
# Licensed under the Apache License, Version 2.0.

from dataclasses import dataclass


@dataclass
class Company:
    name: str = ""
    cif: str= ""
    address: str = ""
    email: str = ""
    phone: str = ""
