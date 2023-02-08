import datetime as dt
from unittest import TestCase
from unittest.mock import patch
from unittest import skip

from query_finders.query_finder import BaseFinder, QcodeFinder


class TestQcodeFinder(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.qf = QcodeFinder("Q615") # Lionel Messi
        cls.alt_qf = QcodeFinder("Q317521") # Elon Musk # marie

    def test_valid_qcode(self):
        with self.assertRaises(ValueError):
            QcodeFinder("ABC")

    def test_init_sets_qcode(self):
        self.assertEqual(self.qf.qcode, "Q615")

    @patch ("query_finders.query_finder.QcodeFinder._read_query")
    @patch ("query_finders.query_finder.QcodeFinder._get_response") # don't call SPARQLWrapper
    @patch ("query_finders.query_finder.dt.datetime")   # interfering with __str__
    @patch ("query_finders.query_finder.json")        # interfering with __str__
    def test_init_calls_read_query(self, mock_json, mock_dt, _, mock_read_query):
        QcodeFinder("Q615")
        mock_read_query.assert_called_once()

    def test_init_reads_in_query(self):
        self.assertIsInstance(self.qf.query, str)

    def test_query_is_formatted_with_qcode(self):
        self.assertIn(self.qf.qcode, self.qf.query)

    @patch ("query_finders.query_finder.QcodeFinder._get_response")
    @patch ("query_finders.query_finder.dt.datetime")   # interfering with __str__
    @patch ("query_finders.query_finder.json")        # interfering with __str__
    def test_qf_init_calls_get_response(self, mock_json, mock_dt, mock_get_response):
        QcodeFinder("Q615")
        mock_get_response.assert_called_once()

    def test_response_is_valid_json(self):
        self.assertIsInstance(self.qf.response, dict)

    def test_parse_age(self):
        # TODO: mock date.today() to return a fixed date
        dob = dt.date(1987, 6, 24)
        age = self.qf._calculate_age(dob)
        self.assertEqual(age, 35)

    def test_parse_url(self):
        self.qf._parse_url()
        self.assertEqual(self.qf.url, f"http://www.wikidata.org/entity/{self.qf.qcode}")

    def test_parse_known_as(self):
        self.qf._parse_known_as()
        self.assertEqual(self.qf.known_as, "Lionel Messi")

    def test_parse_birth_name(self):
        self.qf._parse_birth_name()
        self.assertEqual(self.qf.birth_name, "Lionel Andrés Messi")

    def test_parse_date_of_birth(self):
        self.qf._parse_date_of_birth()
        dob = dt.date(1987, 6, 24)
        self.assertEqual(self.qf.date_of_birth, dob)

    def test_parse_father_known_as(self):
        self.qf._parse_father_known_as()
        self.assertEqual(self.qf.father_known_as, "Jorge Messi")

    def test_parse_father_date_of_birth(self):
        self.qf._parse_father_date_of_birth()
        dob = dt.date(1958, 1, 1)
        self.assertEqual(self.qf.father_date_of_birth, dob)

    def test_parse_mother_known_as(self):
        # TODO: mock
        self.qf._parse_mother_known_as() # has no mother data
        self.assertEqual(self.qf.mother_known_as, None)
        self.alt_qf._parse_mother_known_as()
        self.assertEqual(self.alt_qf.mother_known_as, "Maye Musk")

    def test_parse_mother_date_of_birth(self):
        self.qf._parse_mother_date_of_birth() # has no mother data
        self.assertEqual(self.qf.mother_date_of_birth, None)
        self.alt_qf._parse_mother_date_of_birth()
        dob = dt.date(1948, 4, 18)
        self.assertEqual(self.alt_qf.mother_date_of_birth, dob)

    def test_parse_spouse_known_as(self):
        self.qf._parse_spouse_known_as()
        self.assertEqual(self.qf.spouse_known_as, "Antonela Roccuzzo")

    def test_parse_spouse_date_of_birth(self):
        self.qf._parse_spouse_date_of_birth()
        dob = dt.date(1988, 2, 26)
        self.assertEqual(self.qf.spouse_date_of_birth, dob)

    def test_parse_children(self):
        self.qf._parse_children()
        expected = [
            {'childQ': 'http://www.wikidata.org/entity/Q108049158',
            'childKnownAs': 'Thiago Messi', 'childDOB': '2012-11-02T00:00:00Z'},
            {'childQ': 'http://www.wikidata.org/entity/Q108049261',
            'childKnownAs': 'Mateo Messi Roccuzzo', 'childDOB': '2015-01-01T00:00:00Z'},
            {'childQ': 'http://www.wikidata.org/entity/Q108049303',
            'childKnownAs': 'Ciro Messi Roccuzzo', 'childDOB': '2018-01-01T00:00:00Z'}
        ]
        self.assertEqual(self.qf.children, expected)
        # TODO: test with no children & missing values

    def test_parse_siblings(self):
        self.qf._parse_siblings()
        self.assertEqual(self.qf.siblings, None)
        self.alt_qf._parse_siblings()
        expected = [
            {'siblingQ': 'http://www.wikidata.org/entity/Q6409751',
            'siblingKnownAs': 'Kimbal Musk', 'siblingDOB': '1972-09-20T00:00:00Z'},
            {'siblingQ': 'http://www.wikidata.org/entity/Q7827568',
            'siblingKnownAs': 'Toscá Musk', 'siblingDOB': '1974-01-01T00:00:00Z'},
            {'siblingQ': 'http://www.wikidata.org/entity/Q104721244',
            'siblingKnownAs': 'Elliot Rush Musk', 'siblingDOB': '2017-01-01T00:00:00Z'},
            {'siblingQ': 'http://www.wikidata.org/entity/Q105538968',
            'siblingKnownAs': 'Alexandra Musk', 'siblingDOB': ''},
            {'siblingQ': 'http://www.wikidata.org/entity/Q111363577',
            'siblingKnownAs': 'Asha Rose Musk', 'siblingDOB': ''},
        ]
        for sibling in expected:
            self.assertIn(sibling, self.alt_qf.siblings)

    def test_parse_occupation(self):
        self.qf._parse_occupation()
        self.assertEqual(self.qf.occupation, "association football player")
        self.alt_qf._parse_occupation()
        expected = "engineer, entrepreneur, inventor, investor, angel investor, " \
            "business magnate, programmer, international forum participant"
        for occ in expected.split(", "):
            self.assertIn(occ, self.alt_qf.occupation)

    def test_parse_education(self):
        self.qf._parse_education()
        self.assertEqual(self.qf.education, None)
        self.alt_qf._parse_education()
        expected = "Stanford University, University of Pennsylvania, " \
            "University of Pretoria, The Wharton School, Queen's University, " \
            "Pretoria Boys High School, Waterkloof House Preparatory School, " \
            "Bryanston High School, Smith School of Business"
        for edu in expected.split(", "):
            self.assertIn(edu, self.alt_qf.education)

    def test_parse_criminal_convictions(self):
        self.qf._parse_criminal_convictions()
        self.assertEqual(self.qf.criminal_convictions, "tax fraud")
        self.alt_qf._parse_criminal_convictions()
        self.assertEqual(self.alt_qf.criminal_convictions, None)

    def test_parse_response(self):
        self.qf = QcodeFinder("Q615") # reset all attributes
        self.qf._parse_response()
        self.assertIsNotNone(self.qf.response)
        self.assertIsNotNone(self.qf.known_as)
        self.assertIsNotNone(self.qf.date_of_birth)
        self.assertIsNotNone(self.qf.father_known_as)
        self.assertIsNotNone(self.qf.father_date_of_birth)
        self.assertIsNone(self.qf.mother_known_as)
        self.assertIsNone(self.qf.mother_date_of_birth)
        self.assertIsNotNone(self.qf.spouse_known_as)
        self.assertIsNotNone(self.qf.spouse_date_of_birth)
        self.assertIsNotNone(self.qf.children)
        self.assertIsNone(self.qf.siblings)
        self.assertIsNotNone(self.qf.occupation)
        self.assertIsNone(self.qf.education)
        self.assertIsNotNone(self.qf.criminal_convictions)
