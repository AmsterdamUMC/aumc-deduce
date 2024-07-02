import unittest

from deduce.person import Person


class MyTestCase(unittest.TestCase):
    def test_persoon(self):
        persoon_to_test = Person.from_keywords(patient_given_name="Jantinus Nicolaas",
                                               patient_surname="Klaassen",
                                               patient_initials="J.K.",
                                               patient_first_names="Jan Klaas")
        assert "Klaassen" == persoon_to_test.surname
        assert "J.K." == persoon_to_test.initials
        assert ["Jan", "Klaas", "Jantinus Nicolaas"] == persoon_to_test.first_names


if __name__ == '__main__':
    unittest.main()
