# Read excel file
import pandas as pd

spreadsheet = "C:/Users/office/local-programs/spreadsheet/EASEL COPY.xlsx"

# print(pd.read_excel(spreadsheet, index_col=0))

# Export all sheets in an xlsx file to individual csv files
def get_sheets():
   for sheet_name, df in pd.read_excel(spreadsheet, index_col=0, sheet_name=None).items():
      df.to_csv(f'output_{sheet_name}.csv', index=False, encoding='utf-8')