import datetime as dt
import json
import os
from pprint import pprint as pp
import re
import sys

from SPARQLWrapper import SPARQLWrapper, JSON


class BaseFinder():
    """
    Base class for query finders. Not intended to be used directly.
    """

    def __init__(self):
        self.query_filename = None
        self.query = None
        # data from Wikidata:
        self.url = None
        self.known_as = None
        self.birth_name = None
        self.date_of_birth = None
        self.father_known_as = None
        self.father_date_of_birth = None
        self.mother_known_as = None
        self.mother_date_of_birth = None
        self.spouse_known_as = None
        self.spouse_date_of_birth = None
        self.children = None
        self.siblings = None
        self.occupation = None
        self.education = None
        self.criminal_convictions = None


    def _read_query(self):
        """Read query from file and return as string.
        Query file is expected to be in queries/ directory.
        Query remains unformatted until _read_query is called in subclass.

        Returns:
            str: unformatted query.
        """
        project_root = os.path.dirname(os.path.dirname(__file__))
        query_path = os.path.join(project_root, "queries", self.query_filename)
        with open(query_path, "r") as f:
            query = f.read()
        return query
    
    def _get_response(self):
        """Get response from Wikidata SPARQL endpoint."""
        endpoint_url = "https://query.wikidata.org/sparql"
        user_agent = "xapien-tech-test (https://www.juancoquet.com/)/%s.%s" % (
            sys.version_info[0],
            sys.version_info[1],
        )
        sparql  = SPARQLWrapper(endpoint_url, agent=user_agent)
        sparql.setQuery(self.query)
        sparql.setReturnFormat(JSON)
        return sparql.query().convert()["results"]["bindings"][0]

    def _calculate_age(self, dob: dt.date) -> int:
        """Calculate age from date of birth.

        Args:
            dob (dt.date): date of birth

        Returns:
            int: age
        """
        today = dt.date.today()
        return today.year - dob.year - (
            (today.month, today.day) < (dob.month, dob.day)
            # evals to True (1) if today is before dob's birthday
            # else False (0)
        )

    def _parse_url(self):
        if self.response.get("item"):
            self.url = self.response["item"]["value"]

    def _parse_known_as(self):
        if self.response.get("itemLabel"):
            self.known_as = self.response["itemLabel"]["value"]

    def _parse_birth_name(self):
        if self.response.get("birthName"):
            self.birth_name = self.response["birthName"]["value"]

    def _parse_date_of_birth(self):
        if self.response.get("DOB"):
            dob = dt.datetime.strptime(
                self.response["DOB"]["value"], "%Y-%m-%dT%H:%M:%SZ"
            ).date()
            self.date_of_birth = dob

    def _parse_father_known_as(self):
        if self.response.get("fatherKnownAs"):
            self.father_known_as = self.response["fatherKnownAs"]["value"]

    def _parse_father_date_of_birth(self):
        if self.response.get("fatherDOB"):
            dob = dt.datetime.strptime(
                self.response["fatherDOB"]["value"], "%Y-%m-%dT%H:%M:%SZ"
            ).date()
            self.father_date_of_birth = dob

    def _parse_mother_known_as(self):
        if self.response.get("motherKnownAs"):
            self.mother_known_as = self.response["motherKnownAs"]["value"]

    def _parse_mother_date_of_birth(self):
        if self.response.get("motherDOB"):
            dob = dt.datetime.strptime(
                self.response["motherDOB"]["value"], "%Y-%m-%dT%H:%M:%SZ"
            ).date()
            self.mother_date_of_birth = dob

    def _parse_spouse_known_as(self):
        if self.response.get("spouseKnownAs"):
            self.spouse_known_as = self.response["spouseKnownAs"]["value"]

    def _parse_spouse_date_of_birth(self):
        if self.response.get("spouseDOB"):
            dob = dt.datetime.strptime(
                self.response["spouseDOB"]["value"], "%Y-%m-%dT%H:%M:%SZ"
            ).date()
            self.spouse_date_of_birth = dob

    def _parse_children(self):
        if self.response.get("children"):
            children_str = self.response["children"]["value"]
            self.children = json.loads(children_str)

    def _parse_siblings(self):
        if self.response.get("siblings"):
            siblings_str = self.response["siblings"]["value"]
            self.siblings = json.loads(siblings_str)

    def _parse_occupation(self):
        if self.response.get("occupations"):
            self.occupation = self.response["occupations"]["value"]

    def _parse_education(self):
        if self.response.get("educationHistory"):
            if self.response["educationHistory"]["value"]:
                self.education = self.response["educationHistory"]["value"]

    def _parse_criminal_convictions(self):
        if self.response.get("criminalConvictions"):
            if self.response["criminalConvictions"]["value"]:
                self.criminal_convictions = self.response["criminalConvictions"]["value"]


class QcodeFinder(BaseFinder):
    """
    Find Wikidata item by qcode.
    """

    def __init__(self, qcode):
        super().__init__()
        self.qcode = self._check_valid_qcode(qcode)
        self.query_filename = "query-qcode.rq"
        self.query = self._read_query()
        self.response = self._get_response()
        self._parse_response()

    def __str__(self):
        string = "-" * 80 + \
            f"\nDATA FOUND FOR Q-CODE {self.qcode}:\n" + "-" * 80 + "\n"
        if self.url:
            string += f"URL: {self.url}\n"
        if self.known_as:
            string += f"KNOWN AS: {self.known_as}\n"
        if self.birth_name:
            string += f"BIRTH NAME: {self.birth_name}\n"
        if self.date_of_birth:
            age = self._calculate_age(self.date_of_birth)
            string += f"DATE OF BIRTH: {self.date_of_birth} ({age} years old)\n"
        if self.father_known_as:
            if self.father_date_of_birth:
                age = self._calculate_age(self.father_date_of_birth)
                string += f"FATHER: {self.father_known_as} ({age} years old)\n"
            else:
                string += f"FATHER: {self.father_known_as} (age N/A)\n"
        if self.mother_known_as:
            if self.mother_date_of_birth:
                age = self._calculate_age(self.mother_date_of_birth)
                string += f"MOTHER: {self.mother_known_as} ({age} years old)\n"
            else:
                string += f"MOTHER: {self.mother_known_as} (age N/A)\n"
        if self.spouse_known_as:
            if self.spouse_date_of_birth:
                age = self._calculate_age(self.spouse_date_of_birth)
                string += f"SPOUSE: {self.spouse_known_as} ({age} years old)\n"
            else:
                string += f"SPOUSE: {self.spouse_known_as} (age N/A)\n"
        if self.children:
            string += "CHILDREN:\n"
            for child in self.children:
                known_as = child["childKnownAs"]
                if child["childDOB"]:
                    dob = dt.datetime.strptime(
                        child["childDOB"], "%Y-%m-%dT%H:%M:%SZ"
                    ).date()
                    age = self._calculate_age(dob)
                    string += f"    {known_as} ({age} years old)\n"
                else:
                    string += f"    {known_as} (age N/A)\n"
        if self.siblings:
            string += "SIBLINGS:\n"
            for sibling in self.siblings:
                known_as = sibling["siblingKnownAs"]
                if sibling["siblingDOB"]:
                    dob = dt.datetime.strptime(
                        sibling["siblingDOB"], "%Y-%m-%dT%H:%M:%SZ"
                    ).date()
                    age = self._calculate_age(dob)
                    string += f"    {known_as} ({age} years old)\n"
                else:
                    string += f"    {known_as} (age N/A)\n"
        if self.occupation:
            string += f"OCCUPATION: {self.occupation}\n"
        if self.education:
            string += f"EDUCATION: {self.education}\n"
        if self.criminal_convictions:
            string += f"CRIMINAL CONVICTIONS: {self.criminal_convictions}\n"
        return string

    def _check_valid_qcode(self, qcode):
        """Check if qcode is valid.
        Returns input qcode if valid, raise ValueError if not.

        Args:
            qcode (str): Qcode format Q\d+

        Raises:
            ValueError: If qcode is not in Q\d+ format.

        Returns:
            str: input qcode if valid.
        """
        if not re.match(r"Q\d+", qcode):
            raise ValueError("Invalid qcode format")
        return qcode

    def _read_query(self):
        query = super()._read_query()
        return query % {"qcode": self.qcode}

    def _parse_response(self):
        self._parse_url()
        self._parse_known_as()
        self._parse_birth_name()
        self._parse_date_of_birth()
        self._parse_father_known_as()
        self._parse_father_date_of_birth()
        self._parse_mother_known_as()
        self._parse_mother_date_of_birth()
        self._parse_spouse_known_as()
        self._parse_spouse_date_of_birth()
        self._parse_children()
        self._parse_siblings()
        self._parse_occupation()
        self._parse_education()
        self._parse_criminal_convictions()


class NameFinder(BaseFinder):
    """
    Not implemented. this is a rough sketch of how I would implement a
    name finder.
    """

    def __init__(self, name):
        super().__init__()
        self.name = name
        self.query_filename = "query-name.rq"
        self.query = self._read_query()
        self.response = self._get_response()
        self._parse_response()

    def __str__(self):
        # formats name, qcode, url, date of birth and occupation
        pass

    def _parse_response(self):
        # query-name.rq would return any matches for the given name.
        # I would likely implement a fuzzy match using a regex pattern.
        # This would potentially lead to too many results, so I would
        # set a limit on the number of results returned.
        # I would then parse the results using the methods inherited from
        # BaseFinder:

        # _parse_known_as()
        # _parse_qcode() (would be implemented in this class)
        # _parse_url()
        # _parse_date_of_birth()
        # _parse_occupation()

        # note that this would not return the full data for each person.
        # After parsing and displaying the results, the user could choose
        # to view the full data for a particular person by entering their
        # qcode.
        # This would then be handled by the QcodeFinder class.
        pass

    # see README.md for more details.