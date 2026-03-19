"""
This module contains the Google Sheets class that is used to interact with the Google Sheets API.
"""

import gspread
from gspread.exceptions import SpreadsheetNotFound
from typing import Dict
import config

class GoogleSheet:
    """
    This class is used to interact with the Google Sheets.
    """
    
    def __init__(
            self, 
            credentials: str = config.CREDENTIALS_CONTENT,
            spreadsheet_url: str = config.SHEETS_ULR
    ):
        """
        :param credentials: Content from credentials file
        :param sheet_url: Url to your Google Sheet 
        """
        self.client = gspread.service_account_from_dict(credentials)
        self.spreadsheet = self.client.open_by_url(spreadsheet_url)

    def write_user_result(
            self, 
            user: str, 
            result: Dict[str, str]
    ):
        """
        Add or update user result in sheet
        :param user: Github username
        :param result: Dict with results.
        """
        user_row = self._find_user_row(user)
        row_number = user_row if user_row else len(self.spreadsheet.sheet1.get_all_values()) + 1
        row_data = [row_number, user] + [result[key] for key in result]

        if user_row:
            self.spreadsheet.sheet1.update(values=[row_data], range_name=f"A{user_row}:E{user_row}")
        else:
            self.spreadsheet.sheet1.append_row(row_data)

    def _find_user_row(
            self, 
            user: str
    ) -> int:
        """
        Find the row number of a user by their GitHub username
        :param user: Github username
        :return: row number or None, if user is find.
        """
        users = self.spreadsheet.sheet1.col_values(2) 
        try:
            return users.index(user) + 1
        except ValueError:
            return None

        


gh = GoogleSheet()
gh.write_user_result(user='Dmytro', result={'Status': 'Not', 'Bal':'Good'})
