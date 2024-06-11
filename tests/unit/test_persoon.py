import unittest

from deduce.person import Person


class TestPersoon(unittest.TestCase):

    def test_irregular_spaces(self):
        # tests for spaces in irregular places (leading, trailing, between duplicate tokens)
        # first names first
        person = Person.from_keywords(" Mies  Wilma Trudy", "M.W.T.", patient_surname="Pietersen")
        self.assertEqual(["Mies", "Wilma", "Trudy"], person.first_names)  # add assertion here

        person = Person.from_keywords("Piet Jan Klaas", " P.  J.K. H, ", patient_surname="Pietersen")
        self.assertEqual("P.J.K.H.", person.initials)  # add assertion here


        # test a single stam-naam with leading and trailing spaces
        person = Person.from_keywords("Piet Jan Klaas", " P.J.K.H", patient_surname="Pietersen")
        self.assertEqual("Pietersen", person.surname)  # add assertion here
        person = Person.from_keywords("Piet Jan Klaas", " P.J.K.H", patient_surname="   Pietersen")
        self.assertEqual("Pietersen", person.surname)  # add assertion here
        person = Person.from_keywords("Piet Jan Klaas", " P.J.K.H", patient_surname="Pietersen   ")
        self.assertEqual("Pietersen", person.surname)  # add assertion here

    def test_missing_values(self):
        person = Person.from_keywords("Piet", "P.", patient_surname="")
        self.assertEqual(None, person.surname)  # add assertion here
        person = Person.from_keywords("Piet", "P.", patient_surname=None)
        self.assertEqual(None, person.surname)  # add assertion here
        person = Person.from_keywords("Piet", "P.")
        self.assertEqual(None, person.surname)  # add assertion here

        person = Person.from_keywords("Piet", "", patient_surname="Pietersen")
        self.assertEqual(None, person.initials)  # add assertion here
        person = Person.from_keywords("Piet", None, patient_surname="Pietersen")
        self.assertEqual(None, person.initials)  # add assertion here
        person = Person.from_keywords("Piet", "   ", patient_surname="Pietersen")
        self.assertEqual(None, person.initials)  # add assertion here
        person = Person.from_keywords("Piet", patient_surname="Pietersen")
        self.assertEqual(None, person.initials)  # add assertion here

        person = Person.from_keywords("", "P.", patient_surname="Pietersen")
        self.assertEqual(None, person.first_names)  # add assertion here
        person = Person.from_keywords(None, "P.", patient_surname="Pietersen")
        self.assertEqual(None, person.first_names)  # add assertion here
        person = Person.from_keywords("     ", "P", patient_surname="Pietersen")
        self.assertEqual(None, person.first_names)  # add assertion here
        person = Person.from_keywords(patient_initials="P.", patient_surname="Pietersen")
        self.assertEqual(None, person.first_names)  # add assertion here

    def test_family_names(self):
        person = Person.from_keywords("Wilma", "W.", patient_surname="van Flintstone - Janssen")
        self.assertEqual("van Flintstone - Janssen", person.surname)  # add assertion here

if __name__ == '__main__':
    unittest.main()
