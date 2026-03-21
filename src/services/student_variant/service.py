from typing import List, Dict
import re
import pandas as pd
from utils.logger import setup_logger

logger = setup_logger(__name__)


def get_text_after_phrase(phrase, text):
    pattern = f'{phrase}(.+)'
    result = re.search(pattern, text, re.DOTALL)
    if result:
        return result.group(1)


class StudentVariant:
    def __init__(
            self,
            student_username: str,
            readme_variants: str,
            variants_sheet: pd.DataFrame,
            roster_sheet: pd.DataFrame
    ):
        logger.debug("Initializing StudentVariant with username: %s", student_username)
        self.student_username = student_username
        self.readme_variants = readme_variants
        self.variants = self.__parse_readme()

        self.roster_sheet = roster_sheet
        self.student_real_name = self.__get_student_real_name()

        self.variants_sheet = variants_sheet
        self.student_variant = self.__get_student_variant()

        self.student_assignment = self.get_student_assignment()

        logger.info("StudentVariant initialized")

    def __parse_readme(self) -> Dict[int, str]:
        """
        Parse the readme variants.

        :return: Dictionary of readme variants with variant number as key and assignment as value.
        """
        logger.debug("Parsing readme variants")
        variants_part = get_text_after_phrase("Варіанти завдань для самостійної роботи:", self.readme_variants)
        pattern = re.compile(r'(\d+)\.\s+(.+?)(?=\d+\.|$)', re.DOTALL)
        matches = pattern.findall(variants_part)
        variants = {int(variant): assignment.strip() for variant, assignment in matches}
        logger.info("Parsed %d variants", len(variants))
        return variants

    def __get_student_real_name(self) -> str:
        """
        Get student real name from the roster sheet.

        :return: Student real name.
        """
        try:
            logger.debug("Getting student real name")
            student_row = self.roster_sheet.loc[self.roster_sheet['github_username'] == self.student_username]
            student_real_name = student_row['identifier'].values[0] if not student_row.empty else None
            student_real_name = ' '.join(student_real_name.split()) if student_real_name else None
            logger.info("Got student real name: %s", student_real_name)
            return student_real_name
        except Exception as e:
            logger.error("An error occurred: %s", e)
            return None

    def __get_student_variant(self) -> int:
        """
        Get student variant from the variants sheet.

        :return: Student variant number.
        """
        try:
            logger.debug("Getting student variant")
            student_row = self.variants_sheet.loc[self.variants_sheet['Прізвище'] == self.student_real_name]
            student_variant = student_row['Варіант'].values[0] if not student_row.empty else None
            logger.info("Got student variant: %s", student_variant)
            return student_variant
        except Exception as e:
            logger.error("An error occurred: %s", e)
            return None

    def get_student_assignment(self) -> str:
        """
        Get student assignment.

        :return: Student assignment.
        """
        logger.debug("Getting student assignment")
        student_assignment = self.variants.get(self.student_variant)
        logger.info("Got student assignment: %s", student_assignment)
        return student_assignment
