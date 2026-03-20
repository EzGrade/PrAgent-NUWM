from typing import List, Dict
import re
import pandas as pd
from utils.logger import setup_logger

logger = setup_logger(__name__)


class StudentVariant:
    def __init__(
            self,
            student_username: str,
            readme_variants: str,
            csv_roaster: pd.DataFrame
    ):
        logger.debug("Initializing StudentVariant with username: %s", student_username)
        self.student_username = student_username
        self.readme_variants = readme_variants
        self.variants = self.__parse_readme()
        self.csv_roaster = csv_roaster
        logger.info("StudentVariant initialized")

    def __parse_readme(self) -> Dict[int, str]:
        """
        Parse the readme variants.

        :return: Dictionary of readme variants with variant number as key and assignment as value.
        """
        logger.debug("Parsing readme variants")
        pattern = re.compile(r'(\d+)\.\s+(.+?)(?=\n\d+\.|$)', re.DOTALL)
        matches = pattern.findall(self.readme_variants)
        variants = {int(variant): assignment.strip() for variant, assignment in matches}
        logger.info("Parsed %d variants", len(variants))
        return variants

    def map_student_to_variant(self) -> str:
        """
        Map the student to a variant based on their username.

        :return: The assignment corresponding to the student's variant.
        :raises ValueError: If the student username is not found in the CSV roster.
        """
        logger.debug("Mapping student '%s' to a variant", self.student_username)
        student_index = self.__find_student_index()
        student_variant = self.__calculate_variant(student_index)
        student_assignment = self.variants[student_variant]
        logger.info("Mapped student '%s' to variant %d: %s", self.student_username, student_variant, student_assignment)
        return student_assignment

    def __find_student_index(self) -> int:
        """
        Find the index of the student in the CSV roster.

        :return: Index of the student.
        :raises ValueError: If the student username is not found in the CSV roster.
        """
        try:
            student_index = self.csv_roaster.loc[self.csv_roaster['github_username'] == self.student_username].index[0]
            logger.debug("Found student '%s' at index %d", self.student_username, student_index)
            return student_index
        except IndexError:
            logger.error("Student username '%s' not found in the CSV roster", self.student_username)
            raise ValueError(f"Student username '{self.student_username}' not found in the CSV roster.")

    def __calculate_variant(self, student_index: int) -> int:
        """
        Calculate the variant number for the student based on their index.

        :param student_index: Index of the student in the CSV roster.
        :return: Variant number.
        """
        student_variant = student_index % len(self.variants) + 1
        logger.debug("Calculated variant %d for student index %d", student_variant, student_index)
        return student_variant
