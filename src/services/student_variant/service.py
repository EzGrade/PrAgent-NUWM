import re

from loguru import logger
import pandas as pd


def get_text_after_phrase(phrase, text):
    pattern = f'{phrase}(.+)'
    result = re.search(pattern, text, re.DOTALL)
    if result:
        return result.group(1)
    return ""  # Return empty string instead of None


class StudentVariant:
    def __init__(
            self,
            student_username: str,
            readme_variants: str,
            variants_sheet: pd.DataFrame,
            roster_sheet: pd.DataFrame
    ):
        logger.debug(f"Initializing StudentVariant with username: {student_username}")
        self.student_username = student_username
        self.readme_variants = readme_variants
        self.variants = self.__parse_readme()

        self.roster_sheet = roster_sheet
        self.student_real_name = self.__get_student_real_name()

        self.variants_sheet = variants_sheet
        self.student_variant = self.__get_student_variant()

        self.student_assignment = self.get_student_assignment()

        logger.info("StudentVariant initialized")

    def __parse_readme(self) -> dict[int, str]:
        """
        Parse the readme variants.

        :return: Dictionary of readme variants with variant number as key and assignment as value.
        """
        logger.debug("Parsing readme variants")
        variants_part = get_text_after_phrase("Варіанти завдань для самостійної роботи", self.readme_variants)
        pattern = re.compile(r'(\d+)\.\s+(.+?)(?=\d+\.|$)', re.DOTALL)
        matches = pattern.findall(variants_part)
        variants = {int(variant): assignment.strip() for variant, assignment in matches}
        logger.info(f"Parsed {len(variants)} variants")
        return variants

    def __get_student_real_name(self) -> str:
        """
        Get student real name from the roster sheet.

        :return: Student real name.
        """
        try:
            logger.debug("Getting student real name")
            logger.debug(f"Looking for github_username: '{self.student_username}'")
            student_row = self.roster_sheet.loc[self.roster_sheet['github_username'] == self.student_username]
            logger.debug(f"Found {len(student_row)} matching rows")
            
            if student_row.empty:
                logger.warning(f"Student '{self.student_username}' not found in roster sheet!")
                return None
                
            student_real_name = student_row['identifier'].values[0]
            student_real_name = ' '.join(student_real_name.split()) if student_real_name else None
            logger.info(f"Got student real name: {student_real_name}")
            return student_real_name
        except Exception as e:
            logger.error(f"An error occurred: {e}")
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
            logger.info(f"Got student variant: {student_variant}")
            return student_variant
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            return None

    def get_student_assignment(self) -> str:
        """
        Get student assignment.

        :return: Student assignment.
        """
        logger.debug("Getting student assignment")
        student_assignment = self.variants.get(self.student_variant)
        logger.info(f"Got student assignment: {student_assignment}")
        return student_assignment
