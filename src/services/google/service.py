import gspread
import pandas as pd

from loguru import logger

from src.services.student_variant.service import StudentVariant

from src.clients.google import GoogleSheetsClient
from src.models.google.entity import ReviewModel
from src.utils.enums.sheets import SheetsNamingEnum


class GoogleSheet:
    ALL_COLUMNS = [
        "Номер варіанту",
        "ПІБ",
        "github nickname",
        "Коментар бота",
        "№ Спроби",
        "Час здачі",
        "Лінк на останній PR",
        "Промт",
        "Підсумок",
        "Кнопка перевірки ще раз"
    ]

    def __init__(self):
        self.__client = GoogleSheetsClient()
        self.__config = self.__client.config

    def get_teacher_prompts(self, name: str) -> list[str]:
        """
        Get teacher prompts for a specific lab.
        """
        try:
            sheet = self.__client.get_sheet_data(
                self.__config.get_sheet_name(
                    SheetsNamingEnum.PROMPTS
                )
            )
            matching_prompts = sheet.loc[sheet['lab_name'] == name, 'Prompt']
            if matching_prompts.empty:
                logger.warning(f"No prompts found for lab name: {name}")
                return []
            prompts = matching_prompts.values[0]
            return prompts.split(";;")
        except Exception as e:
            logger.error(f"An error occurred while getting teacher prompts: {e}")
            return []

    def get_variants_sheet(self) -> pd.DataFrame:
        """
        Get the variants sheet from the spreadsheet.
        """
        return self.__client.get_sheet_data(
            self.__config.get_sheet_name(
                SheetsNamingEnum.VARIANTS
            )
        )

    def get_roster_sheet(self) -> pd.DataFrame:
        """
        Get the roster sheet from the spreadsheet.
        """
        return self.__client.get_sheet_data(
            self.__config.get_sheet_name(
                SheetsNamingEnum.ROSTER
            )
        )

    def get_all_nicknames(self) -> list[str]:
        """
        Get all nicknames from the Google Sheet.
        """

        try:
            data = self.__client.get_sheet_data(
                self.__config.get_sheet_name(
                    SheetsNamingEnum.ROSTER
                )
            )
            nicknames = data["github_username"].dropna().tolist()
            nicknames = [nick for nick in nicknames if nick.strip()]
            return nicknames
        except Exception as e:
            logger.error(f"An error occurred while getting all nicknames: {e}")
            return []

    def get_all_lab_names(self) -> list[str]:
        """
        Get all lab names from the Google Sheet.
        :return:
        """
        try:
            data = self.__client.get_sheet_data(
                self.__config.get_sheet_name(
                    SheetsNamingEnum.PROMPTS
                )
            )
            lab_names = data["lab_name"].dropna().tolist()
            lab_names = [name for name in lab_names if name.strip()]
            return lab_names
        except Exception as e:
            logger.error(f"An error occurred while getting all lab names: {e}")
            return []

    def get_all_repositories(self, sheet_name: str) -> list[str]:
        """
        Get all repositories from the Google Sheet.
        """
        try:
            data = self.__client.get_sheet_data(sheet_name)
            repositories = data["Лінк на останній PR"].dropna().tolist()
            repositories = [repo for repo in repositories if repo.strip()]

            result = []
            for repo in repositories:
                temp = repo.split("/")
                if len(temp) >= 5:
                    result.append((temp[3], temp[4]))
            return result
        except Exception as e:
            logger.error(f"An error occurred while getting all repositories: {e}")
            return []

    def leave_response(
            self,
            student_variant: StudentVariant,
            student_name: str,
            sheet_name: str,
            ai_response: str,
            last_pr_link: str,
            prompt: str,
            summary: str,
    ) -> bool:
        """
        Leave response in the Google Sheet.
        """
        try:
            sheet = self.__client.spreadsheet.worksheet(sheet_name)
        except gspread.exceptions.WorksheetNotFound:
            logger.info(f"Sheet {sheet_name} not found, creating a new one")
            sheet = self.__client.copy_template_to_new_sheet(sheet_name)

        try:
            records = sheet.get_all_records()
            if not records:
                self.__insert_new_student(student_variant, sheet_name)
                records = sheet.get_all_records()

            data = pd.DataFrame(records)
            logger.debug(data.to_string())
            found, row_number = self.__get_student_row(data, student_name)
            if not found:
                self.__insert_new_student(student_variant, sheet_name)
                data = pd.DataFrame(sheet.get_all_records())
                _, row_number = self.__get_student_row(data, student_name)
            attempts = self.__get_student_attempts(data, student_name) + 1
            date = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
            self.__update_student_data(
                data,
                row_number,
                ai_response,
                attempts,
                date,
                last_pr_link,
                prompt,
                summary,
            )
            self.__client.write_dataframe_to_sheet(sheet_name, data)
            return True
        except Exception as e:
            logger.error(f"An error occurred while leaving response: {e}")
            return False

    @staticmethod
    def __get_student_row(data: pd.DataFrame, student_name: str) -> tuple[bool, int]:
        """
        Get the row number of a student by their real name.
        """
        try:
            # Check if DataFrame is empty or doesn't have the expected column
            if data.empty or 'ПІБ' not in data.columns:
                return False, 1

            students = data['ПІБ'].tolist()
            if student_name in students:
                row_number = students.index(student_name) + 1
                return True, row_number
            else:
                row_number = len(students) + 1
                return False, row_number
        except Exception as e:
            logger.error(f"An error occurred while getting student row: {e}")
            return False, -1

    @staticmethod
    def __update_student_data(
            data: pd.DataFrame,
            row_number: int,
            ai_response: str,
            attempts: int,
            date: str,
            last_pr_link: str,
            prompt: str,
            summary: str,
    ):
        """
        Update student data in the DataFrame.
        """
        idx = row_number - 1
        data.at[idx, 'Коментар бота'] = ai_response
        data.at[idx, '№ Спроби'] = attempts
        data.at[idx, 'Час здачі'] = date
        data.at[idx, 'Лінк на останній PR'] = last_pr_link
        data.at[idx, 'Промт'] = prompt
        data.at[idx, 'Підсумок'] = summary

    def __get_student_attempts(self, data: pd.DataFrame, student_name: str) -> int:
        """
        Get the number of attempts of a student.
        """
        try:
            found, row_number = self.__get_student_row(data, student_name)
            if not found or data.empty or '№ Спроби' not in data.columns:
                return 0

            attempts = data.loc[row_number - 1, '№ Спроби']

            # Handle empty string, None, or non-numeric values
            if pd.isna(attempts) or attempts == '' or attempts is None:
                return 0

            # Convert to int safely
            if isinstance(attempts, (int, float)):
                return int(attempts)

            # Try to parse string
            try:
                return int(str(attempts))
            except (ValueError, TypeError):
                return 0

        except Exception as e:
            logger.error(f"An error occurred while getting student attempts: {e}")
            return 0

    def __insert_new_student(self, student_variant: StudentVariant, sheet_name: str) -> bool:
        """
        Insert a new student into the Google Sheet.
        """
        logger.info("Inserting new student into the sheet")
        try:
            sheet = self.__client.spreadsheet.worksheet(sheet_name)
            records = sheet.get_all_records()
            if not records:
                model = ReviewModel(
                    variant_number=student_variant.student_variant,
                    student_name=student_variant.student_real_name,
                    student_github_username=student_variant.student_username,
                    comment=None,
                    attempt_number=0,
                    attempt_time=None,
                    last_pr_link=None,
                    prompt=None,
                    summary=None,
                    retry_button=None
                )
                data = pd.DataFrame(model.to_pd_dict())
                self.__client.write_dataframe_to_sheet(sheet_name, data)
                return True

            data = pd.DataFrame(sheet.get_all_records())
            model = ReviewModel(
                variant_number=student_variant.student_variant,
                student_name=student_variant.student_real_name,
                student_github_username=student_variant.student_username,
                comment=None,
                attempt_number=0,
                attempt_time=None,
                last_pr_link=None,
                prompt=None,
                summary=None,
                retry_button=None
            )
            new_student = pd.DataFrame(model.to_pd_dict())
            data = pd.concat([data, new_student], ignore_index=True)
            self.__client.write_dataframe_to_sheet(sheet_name, data)
            return True

        except Exception as e:
            logger.error(f"An error occurred while inserting new student: {e}")
            return False
