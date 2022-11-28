# Turns a folder of folders and its spreadsheets into a CSV for import into Shopify
import os
import re
import csv
import numpy as np
import pandas as pd
from datetime import date
import glob
import shutil
from PIL import Image

### DEFINE THE FUNCTIONS ###

## Convert all sheets in an xlsx file to individual csv files
def spreadsheet_to_sheets(spreadsheet):
   for sheet_name, df in pd.read_excel(spreadsheet, sheet_name=None, header=None, index_col=None).items():
      df.to_csv(f'output_{sheet_name}.csv', index=False, encoding='utf-8')

## Clean up the raw CSVs by removing empty stuff and site description
def clean_CSVs():
   # Get into the storage directory for the CSVs
   os.chdir('output_csv')
   cleaned_copy = []
   current_dir = os.getcwd()
   output_csv_list = os.listdir(current_dir)
   for item in output_csv_list:
      # Open each CSV file and read it
      with open(item) as csvfile:
            csvreader = csv.reader(csvfile, delimiter=',')
            # Get only the items that have at least two capital letters
            pattern = '[A-Z]{2}'
            for row in csvreader:
               for item in row:
                  if re.search(pattern, item):
                     cleaned_copy.append(item)
   # Exit the storage directory for the CSVs
   os.chdir('..')
   return(cleaned_copy)

## Compress the images in a directory based on size
def compress_images(directory, coll_item_path):
   for filename in directory:
      if os.path.splitext(filename) == '.jpg':
         filepath = os.path.join(coll_item_path, filename)
         filesize = os.path.getsize(filepath) / 1000
         # Only save images less than 900 kb
         if filesize > 900:
            picture = Image.open(filepath)
            picture.save(filename, "JPEG", optimize=True, quality=60)
            print('File ', filename, ' was compressed.')

## Chunk the copy into lists that are all the product's information
def chunk_copy(cleaned_copy):

   # Add the SKUs, which have no spaces in them, to a new list
   sku_list = []
   for row in cleaned_copy:
      res = bool(re.search(r"\s", row))
      if res == False:
         sku_list.append(row)

   # Add the matching SKU indexes in cleaned_copy to a new list
   index_list = []
   for sku in sku_list:
      for row in cleaned_copy:
         if sku == row:
            # print(sku, ' = ', row, ' at index ', cleaned_copy.index(row))
            index_list.append(int(cleaned_copy.index(row)))

   chunked_copy = list()

   # Pull out the product information into its own list and add it
   for i in range(0, len(cleaned_copy)):
      for index in range(0, len(index_list)):
         if index == i:
            if index != index_list.index(index_list[-1]):
               chunked_copy.append(cleaned_copy[index_list[index]:index_list[index+1]])
            else:
               chunked_copy.append(cleaned_copy[index_list[index]:])

   return(chunked_copy)

## Get the new copy ready to be put into the import file
def prepare_newCopy(cleaned):

   # Convert the lists into dictionaries and add to newCopy list
   newCopy = []
   headers = ['sku', 'title', 'bullet1',
               'bullet2', 'bullet3', 'bullet4', 'bullet5']
   for row in cleaned:
      rowDict = {}
      for header in headers:
         if len(row) == 7:
            item = row[headers.index(header)]
            rowDict[header] = item
         elif len(row) == 6:
            if header == 'title':
               item = 'NA'
               row.insert(1, item)
               rowDict[header] = item
            else:
               item = row[headers.index(header)]
               rowDict[header] = item
         else:
            continue
      if len(rowDict) != 0:
         newCopy.append(rowDict)

   # Convert the bullets to a list with HTML added
   for rowDict in newCopy:
      bulletList = []
      for key in rowDict:
         if key != 'sku' and key != 'title':
            bulletList.append(rowDict[key])
      if len(bulletList) > 0:
         rowDict['copy'] = bulletList

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
               item = chunk + splitItem[1]
         item = '<li>' + item + '</li>'
         body = body + item
      body = body + '</ul>'
      rowDict['copy'] = body
   return(newCopy)

## Read the current copy csv and make a list of dictionaries
def read_currentCopy(file):
   currentCopy = []
   with open(file, encoding='utf-8') as csvfile:
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
   return(currentCopy)

## Update the currentCopy with the newCopy
def update_import(new_copy, current_copy, product_images):
   # Create a list to hold the products
   for_import = []

   for dictN in new_copy:
      # Create a dictionary to hold the product data
      prodDict = {}
      # Create a list to hold the product rows
      prodRows = []
      for dictC in current_copy:
         # Checks the current dictionary for the Variant SKU key
         if 'Variant SKU' in dictC:
            if dictC['Variant SKU'] == dictN['sku']:
               # Create a dictionary for the product columns
               prodCols = {}

               # Add the keys and values to the columns dictionary
               prodCols['Handle'] = dictC['Handle']
               prodCols['Title'] = dictC['Title']
               prodCols['Body (HTML)'] = dictN['copy']
               prodCols['Variant SKU'] = dictC['Variant SKU']
               if dictN['sku'] in product_images:   
                  prodCols['Image Src'] = 'https://cdn.shopify.com/s/files/1/0577/0035/2197/files/' + product_images[dictC['Variant SKU']][0]
                  prodCols['Image Alt Text'] = dictC['Variant SKU'] + ' - ' + dictC['Title'] + dictC['Handle']

               # Add the rows for the product
               prodRows.append(prodCols)

         else:
            if dictN['sku'] in product_images:     
               for image in product_images[dictN['sku']]:
                  # Create a dictionary for the product columns
                  prodCols = {}

                  # Add the keys and values to the columns dictionary
                  prodCols['Handle'] = dictC['Handle']
                  prodCols['Image Src'] = 'https://cdn.shopify.com/s/files/1/0577/0035/2197/files/' + image
                  prodCols['Image Alt Text'] = dictN['sku'] + ' - ' + dictN['title'] + dictC['Handle']

                  # Add the rows for the product
                  prodRows.append(prodCols)

      # Assign the key for the product dictionary to the SKU
      prodDict[dictN['sku']] = prodRows
      for_import.append(prodDict)
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

# def main():
#    spreadsheet = os.listdir("spreadsheet")
#    file = "C:/Users/office/Downloads/currentCopy.csv"
#    get_sheets(spreadsheet)
#    spreadsheet = os.listdir("spreadsheet")
#    clean_CSV = clean_CSVs(spreadsheet)
#    prepped_copy = prepare_newCopy(clean_CSV)
#    currentCopy = read_currentCopy(file)
#    updated_copy = update_copy(prepped_copy, currentCopy)
#    write_csv(updated_copy)

# main()

### DO THE THINGS ###

wdir = 'C:/Users/office/local-programs'
cat_folder_path = 'C:/Users/office/Downloads/ART SETS'
cat_folder_list = os.listdir(cat_folder_path)

# Get a list of all the directories in the Product Images folder in Dropbox
product_images_root = 'D:/Software/Dropbox (Royal Brush Mfg Inc)/Pubfiles - Web/art.royalbrush.com/_2021 Shopify/assets/Product Images/**/'
product_image_folders = glob.glob(product_images_root, recursive=True)

# Iterate through the folders in the category directory
def iterate_folders():
   for item in cat_folder_list:
      os.chdir(wdir)
      item_path = os.path.join(cat_folder_path, item)
      dir_check = os.path.isdir(item_path)

      # Look inside collection directories only
      if dir_check:
         coll_folder_list = os.listdir(item_path)

         # Iterate through the items in each collection
         for coll_item in coll_folder_list:
               coll_item_path = os.path.join(item_path, coll_item)

               # Find the XLSX files and do stuff to them
               if os.path.splitext(coll_item)[1] == ".xlsx":

                  # Get into the storage directory for the CSVs
                  os.chdir('output_csv')

                  # Convert the spreadsheet into individual CSVs
                  spreadsheet_to_sheets(coll_item_path)
                  print('Converted ', coll_item, ' to individual CSVs.')

                  # Exit the storage directory for the CSVs
                  os.chdir('..')

               # Do stuff with the image folders
               else:
                  # Get a list of all the items within each image folder
                  prod_image_list = os.listdir(coll_item_path)

                  # Find out if the folder is empty and skip it
                  if len(prod_image_list) == 0:
                     print(coll_item, ' is empty')
                     continue

                  # Find out if there are subfolders in the image folders
                  for image_item in prod_image_list:
                     image_item_path = os.path.join(coll_item_path, image_item)
                     item_check = os.path.isdir(image_item_path)

                     # Move the items in the subfolder up a directory
                     if item_check:
                        subfolder_item_list = os.listdir(image_item_path)

                        # Skip images that already exist in the image folder
                        for sub_item in subfolder_item_list:
                           sub_item_path = os.path.join(image_item_path, sub_item)
                           if os.path.exists(coll_item_path + '/' + sub_item):
                              print('File already exists: ', sub_item_path)
                           else:
                              shutil.move(sub_item_path, coll_item_path)
                              print(sub_item, ' was moved to ', coll_item_path)

                        # Delete the subfolder now that we don't need it
                        print(image_item, ' was deleted.')
                        shutil.rmtree(image_item_path)

                  # Compress the images that we've moved and put them in Dropbox
                  for folder_path in product_image_folders:
                     no_slash = folder_path.rstrip(folder_path[-1])
                     folder_name = os.path.split(no_slash)[1]
                     
                     # See if there is a folder in Dropbox for the product
                     if coll_item == folder_name:
                        if len(os.listdir(coll_item_path)) == 0:
                           print('Folder ', coll_item_path, ' is empty.')
                           continue

                        # Move to the directory in Dropbox where the images will be saved
                        os.chdir(folder_path)

                        # Compress any images larger than 1000 KB
                        compress_images(prod_image_list, coll_item_path)

                        # Add the rest of the images to the Dropbox folder
                        for filename in prod_image_list:
                           if os.path.exists(folder_path + filename):
                              print('File ', filename, ' already exists on Dropbox.')
                           else:
                              shutil.move(coll_item_path + '/' + filename, folder_path + '/' + filename)
                              print(filename, ' was moved to Dropbox.')
                        
                        # Get back to the working directory for the program
                        os.chdir(wdir)

# Gather a list of all the images for each product and put them in a dictionary
def get_images(new_copy):
   sku_with_images = {}
   for dictN in new_copy:
      images = []
      root = 'D:/Software/Dropbox (Royal Brush Mfg Inc)/Pubfiles - Web/art.royalbrush.com/_2021 Shopify/assets/Product Images/**/' + dictN['sku'] + '/*.jpg'
      files = glob.glob(root, recursive=True)
      for file in files:
         images.append(os.path.basename(file))
      # Ignore any products that don't have any images
      if len(images) > 0:
         sku_with_images[dictN['sku']] = images
   return(sku_with_images)

# Work on the product copy
# iterate_folders()

# Clean the copy provided by the CSVs
cleaned_copy = clean_CSVs()

# Chunk the cleaned copy into lists
chunked_copy = chunk_copy(cleaned_copy)

# Prepare the chunked copy with HTML and a dictionary format
new_copy = prepare_newCopy(chunked_copy)

# Get a list of all the images for later
product_images = get_images(new_copy)

# Read the Shopify product export into a list of dictionaries
current_copy = read_currentCopy("C:/Users/office/Downloads/products_export_1.csv")

# Create a new file using the current copy and the new copy for import
write_me = update_import(new_copy, current_copy, product_images)

for row in write_me:
   print(row)