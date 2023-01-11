# Xapien Tech Test - Juan Coquet
## Introduction
The program takes a person's Wikidata Qcode as input and finds (where available) the following information:
- Name (how they are most commonly known)
- Birth name
- Father
  - Father's age
- Mother
  - Mother's age
- Current spouse
  - Current spouse's age
- Children
  - Children's ages
- Siblings
  - Siblings' ages
- Occupation
- Education
- Criminal convictions

## Usage
The program uses the SPARQLWrapper library to query Wikidata. Pipenv is used to manage the virtual environment and dependencies. To run the program, first install the dependencies with `pipenv install`.
The program can be run with `pipenv run python main.py <Qcode>`.

#### Examples
```
$ pipenv run python3 main.py Q615
--------------------------------------------------------------------------------
DATA FOUND FOR Q-CODE Q615:
--------------------------------------------------------------------------------
URL: http://www.wikidata.org/entity/Q615
KNOWN AS: Lionel Messi
BIRTH NAME: Lionel Andrés Messi
DATE OF BIRTH: 1987-06-24 (35 years old)
FATHER: Jorge Messi (65 years old)
SPOUSE: Antonela Roccuzzo (34 years old)
CHILDREN:
    Thiago Messi (10 years old)
    Mateo Messi Roccuzzo (8 years old)
    Ciro Messi Roccuzzo (5 years old)
OCCUPATION: association football player
CRIMINAL CONVICTIONS: tax fraud
```
```
$ pipenv run python3 main.py Q317521
--------------------------------------------------------------------------------
DATA FOUND FOR Q-CODE Q317521:
--------------------------------------------------------------------------------
URL: http://www.wikidata.org/entity/Q317521
KNOWN AS: Elon Musk
BIRTH NAME: Elon Reeve Musk
DATE OF BIRTH: 1971-06-28 (51 years old)
FATHER: Errol Musk (77 years old)
MOTHER: Maye Musk (74 years old)
CHILDREN:
    X Æ A-Ⅻ Musk (2 years old)
    Griffin Musk (19 years old)
    Kai Musk (17 years old)
    Vivian Jenna Wilson (19 years old)
    Saxon Musk (17 years old)
    Damian Musk (17 years old)
    Nevada Musk (21 years old)
    Exa Dark Sideræl Musk (1 years old)
SIBLINGS:
    Kimbal Musk (50 years old)
    Toscá Musk (49 years old)
    Elliot Rush Musk (6 years old)
    Alexandra Musk (age N/A)
    Asha Rose Musk (age N/A)
OCCUPATION: engineer, entrepreneur, inventor, business magnate, programmer, investor, angel investor, international forum participant
EDUCATION: Stanford University, University of Pennsylvania, University of Pretoria, The Wharton School, Queen's University, Pretoria Boys High School, Waterkloof House Preparatory School, Bryanston High School, Smith School of Business
```
## Approach
I found a few possible approaches to this problem.

I first found Wikidata Client Library (https://wikidata.readthedocs.io/en/stable/), but decided against it because it seemed to be more geared towards querying Wikidata for specific entities, rather than for specific properties. That is, requests are made for a specific entity using a Qcode, and all available data on that entity is returned. This seemed inefficient for two main reasons:
- Lots of unnecessary data is returned
- Where relatives are available, I would have had to make a separate request for each relative
  - This compounds with the first point, as each relative would return a lot of unnecessary data

I wanted to optimise runtime by only requesting the data I needed, and only requesting it once. For this reason, I decided to use the SPARQLWrapper library (https://sparqlwrapper.readthedocs.io/en/latest/main.html) to make requests to the Wikidata SPARQL endpoint. This allowed me to write a single query that returned all the data I needed (and _only_ the data I needed).

Writing the query was the most time consuming part of the task. I haven't used SPARQL before, and only had limited experience writing raw SQL queries, as I've mostly interacted with databases through ORMs (Django). Through trial and error I eventually managed to write a working query.

Once I had the data I needed, the actual code was fairly straightforward as I didn't have to parse through multiple long responses.

## Improvements
- The query is quite long and unwieldy. I don't know if there is a better approach to writing it, but the self-imposed limitation of only using a single query meant that I had to pack a lot of logic into it.
- I only part-implemented the stretch goal of taking a person's name as input, instead of their Qcode. However, I made sure to have an inheritance structure in place that would allow me to easily implement this – I included a rough implementation that demonstrates how it would work.
- Testing can be improved by mocking requests and including more edge cases. I have covered the main functionality, but there are some edge cases that are not covered. Common sense usage of the program is assumed on behalf of the user – for example, I have not handled edge cases where a non-existent Qcode is passed as input. There should not be any issues as long as the user passes in a valid Qcode for a person. With more time, I could have made the program more robust by handling more edge cases. Some examples:
  - Don't allow the user to pass in a Qcode for an entity that is not a person
  - Don't allow the user to pass in a Qcode for a person that is no longer alive

## Testing
```
$ pipenv run python3 -m unittest
........................
----------------------------------------------------------------------
Ran 24 tests in 0.357s

OK
```