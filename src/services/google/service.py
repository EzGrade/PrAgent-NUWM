"""
This module contains the GoogleSheet class that is used to interact with the Google Sheets API.
"""
import time

import gspread
import pandas as pd
from typing import List, Tuple

from gspread import Worksheet

import config
from services.student_variant.service import StudentVariant
from utils.logger import setup_logger

logger = setup_logger(__name__)


class GoogleSheet:
    """
    This class is used to interact with the Google Sheets.
    """

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

    def __init__(
            self,
            credentials: str = config.CREDENTIALS_CONTENT,
            spreadsheet_url: str = config.SPREADSHEET_URL,
    ):
        """
        Initialize the GoogleSheet client.
        """
        self.client = gspread.service_account_from_dict(credentials)
        self.spreadsheet = self.client.open_by_url(spreadsheet_url)

    def get_sheet_data(self, sheet_name: str) -> pd.DataFrame:
        """
        Get data from a specific sheet.
        """
        try:
            sheet = self.spreadsheet.worksheet(sheet_name)
            data = sheet.get_all_records()
            return pd.DataFrame(data)
        except Exception as e:
            logger.error("An error occurred while getting sheet '%s': %s", sheet_name, e)
            return pd.DataFrame()

    def get_teacher_prompts(self, lab_name: str) -> List[str]:
        """
        Get teacher prompts for a specific lab.
        """
        try:
            sheet = self.spreadsheet.worksheet(config.SHEETS_NAMING["prompts"])
            data = sheet.get_all_records()
            dataframe = pd.DataFrame(data)
            prompts = dataframe.loc[dataframe['lab_name'] == lab_name, 'Prompt'].values[0]
            return prompts.split(";;")
        except Exception as e:
            logger.error("An error occurred while getting teacher prompts: %s", e)

    def get_variants_sheet(self) -> pd.DataFrame:
        """
        Get the variants sheet from the spreadsheet.
        """
        return self.get_sheet_data(config.SHEETS_NAMING["variants"])

    def get_roster_sheet(self) -> pd.DataFrame:
        """
        Get the roster sheet from the spreadsheet.
        """
        return self.get_sheet_data(config.SHEETS_NAMING["roster"])

    def __copy_template_to_new_sheet(self, new_sheet_name: str) -> Worksheet:
        """
        Copy the template sheet to a new sheet.
        """
        try:
            template_sheet = self.spreadsheet.worksheet(config.SHEETS_NAMING["template"])
            self.spreadsheet.duplicate_sheet(source_sheet_id=template_sheet.id, new_sheet_name=new_sheet_name)
            time.sleep(2)
            return self.spreadsheet.worksheet(new_sheet_name)
        except Exception as e:
            logger.error("An error occurred while copying template to new sheet: %s", e)

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
            sheet = self.spreadsheet.worksheet(sheet_name)
        except gspread.exceptions.WorksheetNotFound:
            logger.info("Sheet '%s' not found, creating a new one", sheet_name)
            sheet = self.__copy_template_to_new_sheet(sheet_name)

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
            self.__write_dataframe_to_sheet(sheet_name, data)
            return True
        except Exception as e:
            logger.error("An error occurred while leaving response: %s", e)
            return False

    @staticmethod
    def __get_student_row(data: pd.DataFrame, student_name: str) -> Tuple[bool, int]:
        """
        Get the row number of a student by their real name.
        """
        try:
            students = data['ПІБ'].tolist()
            if student_name in students:
                row_number = students.index(student_name) + 1
                return True, row_number
            else:
                row_number = len(students) + 1
                return False, row_number
        except Exception as e:
            logger.error("An error occurred while getting student row: %s", e)
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

    def __write_dataframe_to_sheet(self, sheet_name: str, dataframe: pd.DataFrame) -> None:
        """
        Write a pandas DataFrame back to the Google Sheet.
        """
        try:
            sheet = self.spreadsheet.worksheet(sheet_name)
            dataframe = dataframe.ffill()
            sheet.clear()
            sheet.update([dataframe.columns.values.tolist()] + dataframe.values.tolist())
        except Exception as e:
            logger.error("An error occurred while writing DataFrame to sheet: %s", e)

    def __get_student_attempts(self, data: pd.DataFrame, student_name: str) -> int:
        """
        Get the number of attempts of a student.
        """
        try:
            _, row_number = self.__get_student_row(data, student_name)
            attempts = data.loc[row_number - 1, '№ Спроби']
            return int(attempts) if pd.notna(attempts) else 0
        except Exception as e:
            logger.error("An error occurred while getting student attempts: %s", e)
            return 0

    def __insert_new_student(self, student_variant: StudentVariant, sheet_name: str) -> bool:
        """
        Insert a new student into the Google Sheet.
        """
        logger.info("Inserting new student into the sheet")
        try:
            sheet = self.spreadsheet.worksheet(sheet_name)
            records = sheet.get_all_records()
            if not records:
                logger.info("Sheet is empty, inserting new student")
                data = pd.DataFrame({
                    "Номер варіанту": [student_variant.student_variant],
                    "ПІБ": [student_variant.student_real_name],
                    "github nickname": [student_variant.student_username],
                    "Коментар бота": [""],
                    "№ Спроби": [0],
                    "Час здачі": "",
                    "Лінк на останній PR": [""],
                    "Промт": [""],
                    "Підсумок": [""],
                    "Кнопка перевірки ще раз": [""],
                })
                self.__write_dataframe_to_sheet(sheet_name, data)
                return True

            data = pd.DataFrame(sheet.get_all_records())
            new_student = pd.DataFrame({
                "Номер варіанту": [student_variant.student_variant],
                "ПІБ": [student_variant.student_real_name],
                "github nickname": [student_variant.student_username],
            })
            data = pd.concat([data, new_student], ignore_index=True)
            self.__write_dataframe_to_sheet(sheet_name, data)
            return True

        except Exception as e:
            logger.error("An error occurred while inserting new student: %s", e)
            return False

    def get_all_nicknames(self) -> List[str]:
        """
        Get all nicknames from the Google Sheet.
        """
        try:
            sheet = self.spreadsheet.worksheet(config.SHEETS_NAMING["roster"])
            data = sheet.get_all_records()
            nicknames = [row["github_username"] for row in data if row.get("github_username")]
            return nicknames
        except Exception as e:
            logger.error("An error occurred while getting all nicknames: %s", e)
            return []

    def get_all_lab_names(self) -> List[str]:
        """
        Get all lab names from the Google Sheet.
        :return:
        """
        try:
            sheet = self.spreadsheet.worksheet(config.SHEETS_NAMING["prompts"])
            data = sheet.get_all_records()
            lab_names = [row["lab_name"] for row in data if row.get("lab_name")]
            return lab_names
        except Exception as e:
            logger.error("An error occurred while getting all lab names: %s", e)
            return []
