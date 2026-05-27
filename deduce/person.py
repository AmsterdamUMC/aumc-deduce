import re

import itertools
from dataclasses import dataclass
from typing import Optional


@dataclass(init=False)
class Person:
    """
    Contains information on a person.

    Usable in a document metadata, where annotators can access it for annotation.
    The mapping between the production fields is as follows:
    first_names: VOORNAAM
    initials: missing in production
    surname: EIGENNAAM
    partername: PARTNERNAAM
    missing: VOLLEDIGE_NAAM
    street: ADRESREGEL_1
    location: woonplaats
    country: LAND_NAAM
    person_id: PAT_MRN_ID
    
    
    The production calls on the production environment are found under the user 'pod-deduce' and located under the
    directories main-sub, main-sub1, main-sub2 and main-sub3. The call is performed in the python script 'worker1.py'
    Each version of the scripts uses a different set of fields and a different implementation of the Deduce Person class.
    
    The worker1.py script is to be found in the project 'aumc-deduce-prod-server' under the main-sub directory. 
    
    Remarks: the ADRESREGEL_2 field contains a lot of invalid values and is not passed on to DEDUCE.
    """

    first_names: Optional[list[str]] = None
    initials: Optional[str] = ""
    surname: Optional[list[str]] = None
    partnername: Optional[list[str]] = None
    given_name: Optional[list[str]] = None
    person_id: Optional[str] = ""
    street: Optional[list[str]] = None
    location: Optional[list[str]] = None
    country: Optional[list[str]] = None
    
    def __init__(self, first_names: list[str],
                 surname : list[str],
                 person_id: str,
                 street: list[str],
                 location: list[str],
                 country: list[str],
                 initials: str = "",
                 partnername: list[str] = [],
                 given_name: list[str] = []):
        # remove all leading and trailing spaces from all elements in the lists
        if first_names:
            self.first_names = list(map(lambda arg:arg.strip(), first_names)) or None

        if surname:
            self.surname = list(map(str.strip, surname)) or None

        if partnername:
            self.partnername = list(map(str.strip, partnername)) or None
        
        if given_name:
            self.given_name = list(map(str.strip, given_name)) or None

        if street:
            self.street  = list(map(str.strip, street)) or None

        if location:
            self.location = list(map(str.strip, location)) or None
            
        if country:
            self.country = list(map(str.strip, country)) or None

        if person_id:
            self.person_id = person_id or None

        if initials:
            self.initials = initials.strip().replace(" ", "").replace(",", ".") or None