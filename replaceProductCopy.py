# Replaces old product copy with the new product copy
# Requires a csv of the current products and a csv of the new copy
# Outputs a file that can be imported into Shopify
import os
import re
import csv
import numpy as np
import pandas as pd

# Export all sheets in an xlsx file to individual csv files
def get_sheets(spreadsheet):
   os.chdir("spreadsheet")
   for file in spreadsheet:
      if os.path.splitext(file)[1] == ".xlsx":
         for sheet_name, df in pd.read_excel(file, sheet_name=None, header=None, index_col=None).items():
            df.to_csv(f'output_{sheet_name}.csv', index=False, encoding='utf-8')
   os.chdir("..")
   print("Spreadsheets converted to sheets.")

# Clean up the raw CSVs by removing empty stuff and site description
def clean_CSVs(spreadsheet):
   cleaned = []
   for file in spreadsheet:
      if os.path.splitext(file)[1] == ".csv":
         os.chdir('spreadsheet')
         with open(file) as csvfile:
               csvreader = csv.reader(csvfile, delimiter=',')
               # Get only the items that have at least two capital letters
               # Avoids grabbing the Site Description, etc.
               pattern = '[A-Z]{2}'
               for row in csvreader:
                  for item in row:
                     if re.search(pattern, item):
                        # print(item)
                        # input("")
                        cleaned.append(item)
         os.chdir('..')
   
   # for row in cleaned:
   #    print(row)
   #    input("")
   return(cleaned)

# Get the new copy ready to be put into the import file
def prepare_newCopy(cleaned):
   # Figure out how many products there are if each product is 6 rows
   numProds = len(cleaned) // 7
   # print(numProds)

   # Spilt the cleaned list into a list of lists to isolate products
   rowList = []
   rowList = np.array_split(cleaned, numProds)
   # for row in rowList:
   #    print(row, '\n')
   #    input("")

   # Convert the lists into dictionaries and add to newCopy list
   newCopy = []
   headers = ['sku', 'title', 'bullet1', 'bullet2', 'bullet3', 'bullet4', 'bullet5']
   for row in rowList:
      rowDict = {}
      for header in headers:
         item = row[headers.index(header)]
         rowDict[header] = item
      newCopy.append(rowDict)
      # print(rowDict, '\n')

   # Convert the bullets to a list with HTML added
   for rowDict in newCopy:
      bulletList = []
      for key in rowDict:
         if key != 'sku' and key != 'title':
            bulletList.append(rowDict[key])
      rowDict['copy'] = bulletList
      # print(bulletList, '\n')

      # Combine the html and copy into one item
      body = '<ul>'
      for item in rowDict['copy']:
         item = re.sub('TRAVEL-FRIENDLY', 'TRAVEL FRIENDLY', item)
         item = re.sub('â€“', '-', item)
         # Add the bold tags around the item header
         splitItem = item.split("-", 1)
         for chunk in splitItem:
            if splitItem.index(chunk) == 0:
               chunk = chunk.rstrip(chunk[-1])
               chunk = "<b>" + chunk + "</b>" + " -"
               # print(splitItem, '\n')
               item = chunk + splitItem[1]
         item = '<li>' + item + '</li>'
         body = body + item
      body = body + '</ul>'
      print(body, '\n')
      rowDict['copy'] = body
   return(newCopy)

# Read the current copy csv and make a list of dictionaries
def read_currentCopy(file):
   currentCopy = []
   with open(file) as csvfile:
         csvreader = csv.reader(csvfile, delimiter=',')
         headers = next(csvreader)
         for row in csvreader:
            rowDict = {}
            for header in headers:
               item = row[headers.index(header)]
               if item == '':
                  row[row.index(item)] = 'empty'
               else:
                  rowDict[header] = item
            currentCopy.append(rowDict)
            # print(rowDict, '\n')
   return(currentCopy)

# Update the currentCopy with the newCopy
def update_copy(newCopy, currentCopy):
   # Create a list to hold the products
   for_import = []

   # Create a list to hold any current images
   # current_images = []
   for dictC in currentCopy:
      # if 'Variant SKU' not in dictC:
      #    current_images.append(dictC)
      # # Checks the current dictionary for the Variant SKU key
      if 'Variant SKU' in dictC:
         for dictN in newCopy:
            if dictC['Variant SKU'] == dictN['sku']:
               # Create a dictionary to hold the product data
               prodDict = {}

               # Create a list to hold the product rows
               prodRows = []

               # Create a dictionary for the product columns
               prodCols = {}

               # Find out if there are already images for any product
                  # If so, find out how many there are and make enough rows
                  # This will have to happen outside of the if Variant SKU
               # If not, just count the number of images for the product
               # Iterate through the images for the product
               # Add a dictionary for each row

               # Add the keys and values to the columns dictionary
               prodCols['Handle'] = dictC['Handle']
               prodCols['Title'] = dictC['Title']
               prodCols['Body (HTML)'] = dictN['copy']
               prodCols['Variant SKU'] = dictC['Variant SKU']
               # prodCols['Image Src'] = dictC['Image Src']
               # prodCols['Image Position'] = dictC['Image Position']
               # prodCols['Image Alt Text'] = dictC['Image Alt Text']

               # Assign the key for the product dictionary to the SKU
               prodDict[dictC['Variant SKU']] = prodRows

   return for_import

# Write the currentCopy to a new csv for import
def write_csv(updated_Copy):
   csv_cols = ['Handle', 'Title', 'Body (HTML)', 'Variant SKU']
   csv_file = "newProductCopy.csv"
   try:
      with open(csv_file, 'w', newline='') as csvfile:
         writer = csv.DictWriter(csvfile, fieldnames=csv_cols)
         writer.writeheader()
         for data in updated_Copy:
            writer.writerow(data)
   except IOError:
      print("I/O error")

def main():
   spreadsheet = os.listdir("spreadsheet")
   file = "C:/Users/office/Downloads/currentCopy.csv"
   get_sheets(spreadsheet)
   spreadsheet = os.listdir("spreadsheet")
   clean_CSV = clean_CSVs(spreadsheet)
   prepped_copy = prepare_newCopy(clean_CSV)
   currentCopy = read_currentCopy(file)
   updated_copy = update_copy(prepped_copy, currentCopy)
   write_csv(updated_copy)

main()

