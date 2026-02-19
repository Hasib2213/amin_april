from gedcom.parser import Parser
from gedcom.element.individual import IndividualElement
from typing import List, Dict

def parse_gedcom(file_path: str) -> dict:
    gedcom_parser = Parser()
    try:
        gedcom_parser.parse_file(file_path, strict=False)
    except Exception as e:
        raise ValueError(f"Failed to parse GEDCOM file: {str(e)}")

    individuals = []
    families = []

    root_child_elements = gedcom_parser.get_root_child_elements()
    for element in root_child_elements:
        if isinstance(element, IndividualElement):
            indi = {
                "id": element.get_pointer(),
                "name": element.get_name(),
                "birth": element.get_birth_data(),
                "death": element.get_death_data(),
            }
            individuals.append(indi)
        # Add family parsing if needed

    return {"individuals": individuals, "families": families}