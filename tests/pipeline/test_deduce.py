import docdeid as dd
from deduce.person import Person
import pytest

text = (
    "betreft: Jan Jansen, bsn 111222333, patnr 000334433. De patient J. Jansen is 64 "
    "jaar oud en woonachtig in Utrecht. Hij werd op 10 oktober 2018 door arts "
    "Peter de Visser ontslagen van de kliniek van het UMCU. Voor nazorg kan hij "
    "worden bereikt via j.JNSEN.123@gmail.com of (06)12345678."
)


class TestDeduce:
    def test_annotate_first_name_and_surname(self, model):
        metadata = {"patient": Person(first_names=["Jan"],
                                       initials="",
                                       surname=["Jansen"],
                                       partnername=[""],
                                       given_name=[],
                                       patient_id="",
                                       street=[],
                                       country=[],
                                       location=[])}
        doc = model.deidentify(text, metadata=metadata)
        doc.annotations.sorted(by=("start_char",))

        expected_annotations = dd.AnnotationSet(
            [
                dd.Annotation(
                    text="(06)12345678",
                    start_char=272,
                    end_char=284,
                    tag="telefoonnummer",
                ),
                dd.Annotation(text="bsn ", start_char=21, end_char=25, tag="nummerwoord"),
                dd.Annotation(text="111222333", start_char=25, end_char=34, tag="bsn", priority=100),
                dd.Annotation(
                    text="Peter de Visser", start_char=153, end_char=168, tag="persoon"
                ),
                dd.Annotation(
                    text="j.JNSEN.123@gmail.com",
                    start_char=247,
                    end_char=268,
                    tag="emailadres",
                ),
                dd.Annotation(
                    text="J. Jansen", start_char=64, end_char=73, tag="patient"
                ),
                dd.Annotation(
                    text="Jan Jansen", start_char=9, end_char=19, tag="patient"
                ),
                dd.Annotation(
                    text="10 oktober 2018", start_char=127, end_char=142, tag="datum"
                ),
                dd.Annotation(text="64", start_char=77, end_char=79, tag="leeftijd"),
              # dd.Annotation(text="oud", start_char=85, end_char=88, tag="persoon"),
                dd.Annotation(text="000334433", start_char=42, end_char=51, tag="id"),
                dd.Annotation(
                    text="Utrecht", start_char=106, end_char=113, tag="locatie"
                ),
                dd.Annotation(
                    text="UMCU", start_char=202, end_char=206, tag="ziekenhuis"
                )
            ]
        )

        doc.annotations = doc.annotations.sorted(by=("start_char",))
        expected_annotations = expected_annotations.sorted(by=("start_char",))
        assert doc.annotations == expected_annotations

    def test_deidentify(self, model):

        metadata = {"patient": Person(first_names=["Jan"],
                                       initials="",
                                       surname=["Jansen"],
                                       partnername=[""],
                                       given_name=[],
                                       patient_id="",
                                       street=[],
                                       country=[],
                                       location=[])}
        doc = model.deidentify(text, metadata=metadata)

        expected_deidentified = (
            "betreft: [PATIENT], [NUMMERWOORD-1][BSN-1], patnr [ID-1]. De patient [PATIENT] is "
            "[LEEFTIJD-1] jaar oud en woonachtig in [LOCATIE-1]. Hij werd op "
            "[DATUM-1] door arts [PERSOON-1] ontslagen van de kliniek van het "
            "[ZIEKENHUIS-1]. Voor nazorg kan hij worden bereikt via [EMAILADRES-1] "
            "of [TELEFOONNUMMER-1]."
        )

        assert doc.deidentified_text == expected_deidentified

    def test_annotate_intext(self, model):
        metadata = {"patient": Person(first_names=["Jan"],
                                       initials="",
                                       surname=["Jansen"],
                                       partnername=[""],
                                       given_name=[],
                                       patient_id="",
                                       street=[],
                                       country=[],
                                       location=[])}
        doc = model.deidentify(text, metadata=metadata)

        expected_intext_annotated = (
            "betreft: <PATIENT>Jan Jansen</PATIENT>, <NUMMERWOORD>bsn </NUMMERWOORD><BSN>111222333</BSN>, "
            "patnr <ID>000334433</ID>. De patient <PATIENT>J. Jansen</PATIENT> is "
            "<LEEFTIJD>64</LEEFTIJD> jaar oud en woonachtig in <LOCATIE>Utrecht"
            "</LOCATIE>. Hij werd op <DATUM>10 oktober 2018</DATUM> door arts "
            "<PERSOON>Peter de Visser</PERSOON> ontslagen van de kliniek van het "
            "<ZIEKENHUIS>UMCU</ZIEKENHUIS>. Voor nazorg kan hij worden bereikt "
            "via <EMAILADRES>j.JNSEN.123@gmail.com</EMAILADRES> of "
            "<TELEFOONNUMMER>(06)12345678</TELEFOONNUMMER>."
        )

        assert dd.utils.annotate_intext(doc) == expected_intext_annotated

    def test_deidentify_location_with_space(self, model):
        metadata = {"patient": Person(first_names=["Pieter", "Jan", "Klaas"],
                                      surname=["Jansen"],
                                      partnername=[""],
                                      patient_id="1234567",
                                      street=["Oude Turfmarkt"],
                                      location=["Oude Turfmarkt", "Amsterdam"],
                                      country=["Burkina Faso"],
                                      given_name=[],
                                      initials="")}
        print("Metadata: ", metadata, flush=True)
        text_with_location = ("betreft: Jan Jansen, bsn 111222333, patnr 000334433. De patient J. Jansen is 64 "
                              "jaar oud en woonachtig in Amsterdam, Oude Turfmarkt, Adres Oude Turfmarkt.")
        doc = model.deidentify(text_with_location, metadata=metadata, disabled={'dates','age','longnumber'})
        expected_deidentified = (
            "betreft: [PATIENT], [NUMMERWOORD-1][BSN-1], patnr [ID-1]. De patient [PATIENT] is "
            "64 jaar oud en woonachtig in [LOCATIE-1], [LOCATIE-2], Adres [LOCATIE-2]."
        )

        assert doc.deidentified_text == expected_deidentified

    def test_deidentify_placenames(self, model):
        metadata = {"patient": Person(first_names=["Jan"],
                                       initials="",
                                       surname=["Jansen"],
                                       partnername=[""],
                                       given_name=[],
                                       patient_id="",
                                       street=[],
                                       country=[],
                                       location=[])}
        text_with_location = ("betreft: Jan Jansen, bsn 111222333, patnr 000334433. De patient J. Jansen is 64 "
                              "jaar oud en woonachtig in Utrecht, Bilthoven, Zaltbommel, Bunnik, Halfweg, Helfweg, "
                              "Súdwest-Fryslân, Alphen ( NB ), Alphen (ZH)")
        doc = model.deidentify(text_with_location, metadata=metadata)

        expected_deidentified = (
            "betreft: [PATIENT], [NUMMERWOORD-1][BSN-1], patnr [ID-1]. De patient [PATIENT] is "
            "[LEEFTIJD-1] jaar oud en woonachtig in [LOCATIE-1], [LOCATIE-2], [LOCATIE-3], [LOCATIE-4], "
            "[LOCATIE-5], Helfweg, [LOCATIE-6], [LOCATIE-7], [LOCATIE-8] (ZH)"
        )

        assert doc.deidentified_text == expected_deidentified

    def test_deidentifystreetnames(self, model):
        metadata = {"patient": Person(first_names=["Jan"],
                                       initials="",
                                       surname=["Janssen"],
                                       partnername=[""],
                                       given_name=[],
                                       patient_id="0003344",
                                       street=["dorpstraat"],
                                       country=[],
                                       location=[])}
        text_with_location = ("betreft: Jan Jansen, bsn 111222333, med. dossier 000.334.4. De patient J. Jansen is 64 "
                              "jaar oud en woonachtig in Dorpstraat 1, DORPSTRAAT 2, DorpStraat 3, dorpstraat 4, "
                              "Dorpstraat 6, Amsterdamsestraatweg, 1234 AA, 1e Achterstraat, "
                              "Amsterdamsestraatweg")

        doc = model.deidentify(text_with_location, metadata=metadata)
        # TODO: lowercase and mixed case locations (typo's) don't seem to work. Discussion point
        expected_deidentified = (
            "betreft: [PATIENT], [NUMMERWOORD-1][BSN-1], med. dossier [MRN-1]. De patient [PATIENT] is [LEEFTIJD-1] jaar oud en "
            "woonachtig in [LOCATIE-1], [LOCATIE-2], DorpStraat 3, dorpstraat 4, [LOCATIE-1], [LOCATIE-3], "
            "[LOCATIE-4], [LOCATIE-5], [LOCATIE-3]"
        )

        assert doc.deidentified_text == expected_deidentified

    def test_deidentify_careinstitutes(self, model):
        metadata = {"patient": Person(first_names=["Jan"],
                                       initials="",
                                       surname=["Jansen"],
                                       partnername=[""],
                                       given_name=[],
                                       patient_id="",
                                       street=[],
                                       country=[],
                                       location=[])}
        text_with_careinstitutes = ("betreft: Jan Jansen, bsn 111222333, patnr 000334433. De patient J. Jansen is 64 "
                              "jaar oud en opgenomen in GGZ inGeest, daarna in Reade. Hij haalt zijn medicatie"
                              "bij Rijn apotheek of 'Rijn apotheek'")
        # TODO 2 problem remain to be solved with care-institutes:
        # 1) Institutes with a space in their name compared to the look items are not masked. E.g. in the 
        # test above 'GGZingeest' is skipped whilst 'GGZ inGeest' is correctly masked. 
        # 2) Additionally upper- and lower-case variants are not masked. e.g. 'GGZ ingeest'

        doc = model.deidentify(text_with_careinstitutes, metadata=metadata)

        expected_deidentified = (
            "betreft: [PATIENT], [NUMMERWOORD-1][BSN-1], patnr [ID-1]. De patient [PATIENT] is [LEEFTIJD-1] jaar oud en"
            " opgenomen in [ZORGINSTELLING-1], daarna in [ZORGINSTELLING-2]. Hij haalt zijn medicatie"
            "bij [LOCATIE-1] apotheek of '[LOCATIE-1] apotheek'"
        )

        assert doc.deidentified_text == expected_deidentified

    def test_duplicate_prefix_surname_and_multiple_token_maiden_name(self, model):
        metadata = {"patient": Person(first_names=["Fien"],
                                               initials="",
                                               surname=["van der Heide", "Jagers Op Akkerhuis"],
                                               partnername=[""],
                                               given_name=[],
                                               patient_id="",
                                               street=[],
                                               country=[],
                                               location=[])}

        text_with_duplicate_prefix_surname = "Mevrouw van der Heide-Jagers Op Akkerhuis werd opgenomen op 15 mei"

        doc = model.deidentify(text_with_duplicate_prefix_surname, metadata=metadata)
        # TODO: surname with multiple tokens combined with prefix name does not work. Discussion point.
        expected_deidentified = (
            "[PERSOON-1] Op Akkerhuis werd opgenomen op [DATUM-1]"
        )
        assert doc.deidentified_text == expected_deidentified

    def test_duplicate_prefix_surname(self, model):
            metadata = {"patient": Person(first_names=["Fien"],
                                          initials="",
                                          surname=["van der Heide", "de Boer"],
                                          partnername=[""],
                                          given_name=[],
                                          patient_id="",
                                          street=[],
                                          country=[],
                                          location=[])}

            text_with_duplicate_prefix_surname = "Mevrouw van der Heide-de Boer werd opgenomen op 15 mei"

            doc = model.deidentify(text_with_duplicate_prefix_surname, metadata=metadata)

            expected_deidentified = (
                "[PERSOON-1] werd opgenomen op [DATUM-1]"
            )

            assert doc.deidentified_text == expected_deidentified

    @pytest.mark.skip(reason="See TODO comments below")
    def test_variants_with_multiple_tokens_in_location_and_surname(self, model):
        metadata = {"patient": Person(first_names=["Jan", "Piet"], surname=["Welter"], partnername=[""], initials="W.",
                                      given_name=[],
                                      street=["Pëver", "Eerste Steeg", "Tweede Weg"],
                                      country=["Nieuw Zeeland"],
                                      location=["Laag Plek","Wëst Nederland","1234 MG", "1234MG"], patient_id="1234")}
        text_input = ("Dhr Welder is ziek, volledige naam WELTER,T.G. Woont in de straat EERSTE STEEG, vroeger in "
                      "de Tweede weg 218 en in de Kalverstraat 23 in het dorp lage vuursche, postcode 1234 MG "
                      "en 1234MG in het land Nieuw Zeoland.")
        # TODO the location 'lage vuursche' exists in the lookup tables but is not masked because residence lookup is
        # TODO case sensitive. Discussion point 1.
        # TODO Discussion point 2: no fuzzy matching for countries: 'Nieuw Zeoland'
        # TODO Discussion point 3: Postcodes with letter combinations which are SI-units (mg of ml etc) are  masked.

        doc = model.deidentify(text_input, metadata=metadata)
        deidentified_text = doc.deidentified_text
        expected_deidentified = (
            "[PATIENT] is ziek, volledige naam [PATIENT],[PERSOON-1] in de straat EERSTE [LOCATIE-1], vroeger in de "
            "[LOCATIE-2] en in de [LOCATIE-3] in het dorp lage vuursche, postcode [LOCATIE-4] en [LOCATIE-4] "
            "in het land Nieuw Zeoland."
        )

        assert deidentified_text == expected_deidentified
