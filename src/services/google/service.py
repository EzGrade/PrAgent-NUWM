"""
This module contains the GoogleSheet class that is used to interact with the Google Sheets API.
"""

import gspread
from gspread.exceptions import SpreadsheetNotFound
import pandas as pd

from typing import Dict, Optional, List
import config
from utils.logger import setup_logger

logger = setup_logger(__name__)


class GoogleSheet:
    """
    This class is used to interact with the Google Sheets.
    """

    USER_COLUMN_INDEX = 2

    def __init__(
            self,
            credentials: str = config.CREDENTIALS_CONTENT,
            spreadsheet_url: str = config.SPREADSHEET_URL
    ):
        """
        :param credentials: Content from credentials file
        :param spreadsheet_url: URL to your Google Sheet
        """
        logger.debug("Initializing GoogleSheet with spreadsheet URL: %s", spreadsheet_url)
        self.client = gspread.service_account_from_dict(credentials)
        self.spreadsheet = self.client.open_by_url(spreadsheet_url)
        logger.info("GoogleSheet initialized")

    def get_variants_sheet(self) -> pd.DataFrame:
        """
        Get the variants sheet from the spreadsheet.
        :return: DataFrame containing the sheet's data
        """
        logger.debug("Getting variants sheet")
        try:
            sheet = self.spreadsheet.worksheet(config.SHEETS_NAMING["variants"])
            data = sheet.get_all_records()
            df = pd.DataFrame(data)
            logger.info("Got variants sheet")
            return df
        except Exception as e:
            logger.error("An error occurred: %s", e)

            # Returns an empty DataFrame in case of an error.
            return pd.DataFrame()

    def get_roster_sheet(self) -> pd.DataFrame:
        """
        Get the roster sheet from the spreadsheet.
        :return: DataFrame containing the sheet's data
        """
        logger.debug("Getting roster sheet")
        try:
            sheet = self.spreadsheet.worksheet(config.SHEETS_NAMING["roster"])
            data = sheet.get_all_records()
            df = pd.DataFrame(data)
            logger.info("Got roster sheet")
            return df
        except Exception as e:
            logger.error("An error occurred: %s", e)

            # Returns an empty DataFrame in case of an error.
            return pd.DataFrame()

    def write_user_result(
            self,
            user: str,
            result: Dict[str, str]
    ) -> None:
        """
        Add or update user result in sheet.
        :param user: GitHub username
        :param result: Dict with results.
        """
        logger.debug("Writing user result for user: %s with result: %s", user, result)
        try:
            user_row = self._find_user_row(user)
            row_number = user_row if user_row else len(self.spreadsheet.sheet1.get_all_values()) + 1
            row_data = [row_number, user] + [result[key] for key in result]

            if user_row:
                self.spreadsheet.sheet1.update(f"A{user_row}:E{user_row}", [row_data])
                logger.info("Updated user result for user: %s at row: %d", user, user_row)
            else:
                self.spreadsheet.sheet1.append_row(row_data)
                logger.info("Appended new user result for user: %s at row: %d", user, row_number)
        except SpreadsheetNotFound:
            logger.error("Spreadsheet not found: %s", self.spreadsheet.url)
        except Exception as e:
            logger.error("An error occurred: %s", e)

    def _find_user_row(
            self,
            user: str
    ) -> Optional[int]:
        """
        Find the row number of a user by their GitHub username.
        :param user: GitHub username
        :return: Row number or None if user is not found.
        """
        logger.debug("Finding user row for user: %s", user)
        try:
            users = self.spreadsheet.sheet1.col_values(self.USER_COLUMN_INDEX)
            row_number = users.index(user) + 1
            logger.info("Found user: %s at row: %d", user, row_number)
            return row_number
        except ValueError:
            logger.info("User: %s not found", user)
            return None
        except Exception as e:
            logger.error("An error occurred while finding the user row: %s", e)
            return None

    def leave_response(
            self,
            student_name: str,
            sheet_name: str,
            ai_response: str,
            last_pr_link: str,
            prompt: str,
            summary: str,
    ) -> bool:

        """
        Leave response in the Google Sheet using pandas DataFrame.
        :param student_name: Real name of the student
        :param sheet_name: Name of the sheet
        :param ai_response: AI response
        :param last_pr_link: Link to the last PR
        :param prompt: Prompt for the student
        :param summary: Summary of the response
        :return: True if the response was left successfully, False otherwise
        """
        logger.debug("Leaving response in the Google Sheet")
        try:
            sheet = self.spreadsheet.worksheet(sheet_name)
            data = pd.DataFrame(sheet.get_all_records())
            row_number = self.__get_student_row(data, student_name)
            attempts = self.__get_student_attempts(data, student_name) + 1
            date = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")

            # Update DataFrame with new values
            data.at[row_number - 1, 'розгорнуте зауваження, коментар бота'] = ai_response
            data.at[row_number - 1, '# спроби'] = attempts
            data.at[row_number - 1, 'час здачі'] = date
            data.at[row_number - 1, 'лінк на останній пулріквест'] = last_pr_link
            data.at[row_number - 1, 'Промт'] = prompt
            data.at[row_number - 1, 'підсумок, розпарсили із розгорнутого зауваження'] = summary
            # Write back the DataFrame to the Google Sheet
            self.__write_dataframe_to_sheet(sheet_name, data)
            return True
        except Exception as e:
            logger.error("An error occurred: %s", e)
            return False

    @staticmethod
    def __get_student_row(data: pd.DataFrame, student_name: str) -> int:
        """
        Get the row number of a student by their real name.
        :param data: DataFrame containing the sheet's data
        :param student_name: Real name of the student
        :return: Row number
        """
        logger.debug("Getting student row for student: %s", student_name)
        try:
            students = data['ПІБ'].tolist()
            row_number = students.index(student_name) + 1
            logger.info("Found student: %s at row: %d", student_name, row_number)
            return row_number
        except Exception as e:
            logger.error("An error occurred: %s", e)

    def __write_dataframe_to_sheet(self, sheet_name: str, dataframe: pd.DataFrame) -> None:
        """
        Write a pandas DataFrame back to the Google Sheet.
        :param sheet_name: Name of the sheet
        :param dataframe: Pandas DataFrame to write
        """
        logger.debug("Writing DataFrame to Google Sheet")
        try:
            sheet = self.spreadsheet.worksheet(sheet_name)
            sheet.clear()
            sheet.update([dataframe.columns.values.tolist()] + dataframe.values.tolist())
            logger.info("Successfully wrote DataFrame to Google Sheet")
        except Exception as e:
            logger.error("An error occurred while writing DataFrame to sheet: %s", e)

    def __get_ai_response(self, data: pd.DataFrame, student_name: str) -> str:
        """
        Get the AI response of a student.
        :param data: DataFrame containing the sheet's data
        :param student_name: Real name of the student
        :return: AI response
        """
        logger.debug("Getting AI response for student: %s", student_name)
        try:
            row_number = self.__get_student_row(data, student_name)
            ai_response = data.loc[row_number - 1, 'розгорнуте зауваження, коментар бота']
            logger.info("Found student: %s with AI response: %s", student_name, ai_response)
            return ai_response
        except Exception as e:
            logger.error("An error occurred: %s", e)

    def __get_student_attempts(self, data: pd.DataFrame, student_name: str) -> int:
        """
        Get the number of attempts of a student.
        :param data: DataFrame containing the sheet's data
        :param student_name: Real name of the student
        :return: Number of attempts
        """
        logger.debug("Getting student attempts for student: %s", student_name)
        try:
            row_number = self.__get_student_row(data, student_name)
            attempts = data.loc[row_number - 1, '# спроби']
            logger.info("Found student: %s with attempts: %s", student_name, attempts)
            return int(attempts) if attempts else 0
        except Exception as e:
            logger.error("An error occurred: %s", e)
