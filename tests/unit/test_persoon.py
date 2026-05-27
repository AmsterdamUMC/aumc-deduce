import unittest

from deduce.person import Person


class TestPersoon(unittest.TestCase):
    
    def test_production_call(self):
        dict = {
            "VOORNAAM" : "Jane Mary",
            "EIGENNAAM" : "Doe",
            "PARTNERNAAM" : "Smith",
            "ADRESREGEL_1" : "Dorpstraat 51",
            "WOONPLAATS" : "Mokum",
            "LAND_NAAM": "Belgie",
            "PAT_MRN_ID": "ID_123456"
        }
        # This test mimics the fields used in the Person class as done in the production situation.
        # See the worker1.py script in the aumc-deduce-prodserver.
        voornaam = None if dict['VOORNAAM'] == None else dict['VOORNAAM'].split()
        surname=[dict['EIGENNAAM'],dict['PARTNERNAAM']]
        surname=[w for w in surname if w is not None]
    #    r=[x['ADRESREGEL_1'],x['ADRESREGEL_2']]
        street=[dict['ADRESREGEL_1']]
        street=[w for w in street if w is not None]
        locality=[dict['WOONPLAATS']]
        locality=[woonplaats for woonplaats in locality if woonplaats is not None and woonplaats != 'Nederland']
        person_id = dict['PAT_MRN_ID']
        country = [dict['LAND_NAAM']]
        pers={"patient": Person(first_names=voornaam,
                                surname=surname,
                                street=street,
                                location=locality,
                                country = country, 
                                person_id = dict['PAT_MRN_ID'] )}
        
        self.assertEqual(["Doe", "Smith"], pers["patient"].surname)
        self.assertEqual(["Jane", "Mary"], pers["patient"].first_names)
        self.assertEqual(["Dorpstraat 51"], pers["patient"].street)
        self.assertEqual(["Mokum"], pers["patient"].location)
        self.assertEqual(["Belgie"], pers["patient"].country)
        self.assertEqual("ID_123456", pers["patient"].person_id)

    def test_irregular_spaces(self):
        # tests for spaces in irregular places (leading, trailing, between duplicate tokens)
        # test a single stam-naam with leading and trailing spaces
        person = Person(first_names=["Piet", "Jan", "Klaas"],
                        initials="P.  J.K.H, ",
                        surname=["  Zijstra        "],
                        partnername=[""],
                        given_name=[""],
                        person_id="",
                        location=[""],
                        country=[""],
                        street=[""])
        self.assertEqual(["Zijstra"], person.surname)


        # first names first
        person = Person(first_names=[" Mies", "Wilma", "   Trudy "],
                        initials="M.W.T.",
                        surname=["   Boer "],
                        partnername=[" Vries "],
                        given_name=["Wil", "Tru "],
                        person_id="144025",
                        location=["Utrecht ", " 3500 MG"],
                        country=["Verenigd","Koningrijk"],
                        street=["Dorpstraat 45"])
        self.assertEqual(["Mies", "Wilma", "Trudy"], person.first_names)
        self.assertEqual("M.W.T.", person.initials)
        self.assertEqual(["Wil", "Tru"], person.given_name)
        self.assertEqual(["Boer"], person.surname)
        self.assertEqual(["Vries"], person.partnername)
        self.assertEqual(["Utrecht", "3500 MG"], person.location)
        self.assertEqual(["Verenigd","Koningrijk"], person.country)
        self.assertEqual(["Dorpstraat 45"], person.street)
        self.assertEqual("144025", person.person_id)

        person = Person(first_names=["Piet", "Jan", "Klaas"],
                        initials="P.  J.K.H, ",
                        surname=["Pietersen"],
                        partnername=[],
                        given_name=[""],
                        person_id="",
                        location=[""],
                        country=[""],
                        street=[""])
        self.assertEqual("P.J.K.H.", person.initials)



        # person = Person("Piet Jan Klaas", " P.J.K.H", patient_surname=["Pietersen"])
        # self.assertEqual("Pietersen", person.surname)
        # person = Person("Piet Jan Klaas", " P.J.K.H", patient_surname=["   Pietersen"])
        # self.assertEqual("Pietersen", person.surname)
        # person = Person("Piet Jan Klaas", " P.J.K.H", patient_surname=["Pietersen   "])
        # self.assertEqual("Pietersen", person.surname)

    def test_missing_values(self):
        person = Person(first_names=[], initials="", surname=[], partnername=[],
                        given_name=[], person_id="", country=[], street=[], location=[])
        self.assertEqual(None, person.first_names)
        self.assertEqual("", person.initials)
        self.assertEqual(None, person.surname)
        self.assertEqual(None, person.given_name)
        self.assertEqual("", person.person_id)
        self.assertEqual(None, person.street)
        self.assertEqual(None, person.location)
        self.assertEqual(None, person.country)


    def test_family_names(self):
        person = Person(first_names=["Wilma"],
                        initials="W.",
                        surname=["van Flintstone"],
                        partnername=["Janssen"],
                        given_name=[],
                        person_id="",
                        street=[],
                        location=[],
                        country=[])
        self.assertEqual(["van Flintstone"], person.surname)
        self.assertEqual(["Janssen"], person.partnername)

        # single token in surname list with a minus
        person = Person(first_names=["Wilma"],
                        initials="W.",
                        surname=["van Flintstone"],
                        partnername=["Janssen"],
                        given_name=[],
                        person_id="",
                        street=[],
                        location=[],
                        country=[])
        self.assertEqual(["van Flintstone",], person.surname)
        self.assertEqual(["Janssen"], person.partnername)

        person = Person(first_names=["Wilma"],
                        initials="W.",
                        surname=["van Flintstone"],
                        partnername=["Nijkerk"],
                        given_name=[],
                        person_id="",
                        street=[],
                        location=[],
                        country=[])
        self.assertEqual(["van Flintstone"], person.surname)
        self.assertEqual(["Nijkerk"], person.partnername)

        # test 2 surnames both with prefixes
        person = Person(first_names=["Wilma"],
                        initials="W.",
                        surname=["Flintstone"],
                        partnername=["Janssen de Graaf"],
                        given_name=[],
                        person_id="",
                        street=[],
                        location=[],
                        country=[])
        self.assertEqual(["Flintstone"], person.surname)
        self.assertEqual(["Janssen de Graaf"], person.partnername)

if __name__ == '__main__':
    unittest.main()
