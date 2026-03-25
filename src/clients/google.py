from time import sleep

import gspread
import pandas as pd
from gspread import Worksheet
from loguru import logger

from ..configs.google import GoogleSheetsConfig
from ..utils.enums.sheets import SheetsNamingEnum


class GoogleSheetsClient:
    def __init__(self):
        self.__config = GoogleSheetsConfig()

        self.__client = gspread.service_account_from_dict(
            self.__config.CREDENTIALS_CONTENT
        )
        self.__spreadsheet = self.__client.open_by_url(
            self.__config.SPREADSHEET_URL
        )

    @property
    def config(self):
        return self.__config

    @property
    def spreadsheet(self):
        return self.__spreadsheet

    def get_sheet_data(
            self,
            sheet_name: str,
            convert_to_pd: bool = True
    ) -> Worksheet | pd.DataFrame:
        """
        Get data from a specific sheet.
        """
        try:
            sheet = self.__spreadsheet.worksheet(sheet_name)

            if not convert_to_pd:
                return sheet

            data = sheet.get_all_records()
            return pd.DataFrame(data)
        except Exception as e:
            logger.error(f"An error occurred while getting sheet {sheet_name}: {e}")
            if not convert_to_pd:
                raise
            return pd.DataFrame()

    def duplicate_sheet(self, source_sheet_id: int, new_sheet_name: str) -> None:
        """
        Duplicate a sheet within the spreadsheet.
        """
        try:
            source_sheet = self.__spreadsheet.get_worksheet_by_id(source_sheet_id)
            if not source_sheet:
                raise ValueError(f"Source sheet with ID {source_sheet_id} not found")

            source_sheet.duplicate(new_sheet_name=new_sheet_name)
            logger.info(f"Sheet duplicated successfully: {new_sheet_name}")
        except Exception as e:
            logger.error(f"An error occurred while duplicating sheet: {e}")
            raise

    def copy_template_to_new_sheet(self, new_sheet_name: str) -> Worksheet:
        """
        Copy a template sheet to a new sheet with the specified name.
        If template doesn't exist, create a basic sheet structure.
        """
        try:
            template_sheet = self.get_sheet_data(SheetsNamingEnum.TEMPLATE, convert_to_pd=False)
            self.duplicate_sheet(source_sheet_id=template_sheet.id, new_sheet_name=new_sheet_name)
            sleep(2)
            return self.__spreadsheet.worksheet(new_sheet_name)
        except Exception as e:
            logger.error(f"An error occurred while copying template sheet: {e}")
            logger.info(f"Creating new sheet {new_sheet_name} without template")
            try:
                new_sheet = self.__spreadsheet.add_worksheet(title=new_sheet_name, rows=100, cols=10)
                return new_sheet
            except Exception as create_error:
                logger.error(f"Failed to create new sheet: {create_error}")
                raise

    def write_dataframe_to_sheet(self, sheet_name: str, dataframe: pd.DataFrame) -> None:
        """
        Write a pandas DataFrame back to the Google Sheet.
        """
        try:
            sheet = self.spreadsheet.worksheet(sheet_name)
            dataframe = dataframe.fillna('').infer_objects(copy=False)
            sheet.clear()
            sheet.update([dataframe.columns.values.tolist()] + dataframe.values.tolist())
        except Exception as e:
            logger.error(f"An error occurred while writing DataFrame to sheet: {e}")
