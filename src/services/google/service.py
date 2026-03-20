"""
This module contains the GoogleSheet class that is used to interact with the Google Sheets API.
"""

import gspread
from gspread.exceptions import SpreadsheetNotFound
from typing import Dict, Optional
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


gh = GoogleSheet()
gh.write_user_result(user='Dmytro', result={'Status': 'Not', 'Bal': 'Good'})
