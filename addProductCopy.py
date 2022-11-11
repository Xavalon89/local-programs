# Automatically add product copy to a Shopify import file.
# Sort the csvs by sku before downloading them.
import csv

# Read the new copy csv and make a list of dictionaries
newCopy = []
with open('newCopy.csv') as csvfile:
      csvreader = csv.reader(csvfile, delimiter=',')
      # get the headers of the csv
      headers = next(csvreader)
      # print(headers)
      # iterate through each row in the csv
      for row in csvreader:
         # print("Row: ", row)
         rowDict = {}
         # iterate through each of the headers
         for header in headers:
            # print('Header: ', header)
            # get the item in the row list that matches the header index
            item = row[headers.index(header)]
            # remove any items that have no value
            if item == '':
               row.remove(item)
            else:
               rowDict[header]=item
         # print('rowDict: ', rowDict)
         newCopy.append(rowDict)

# Convert the bullets to a list with HTML added
for rowDict in newCopy:
   # create a list to hold the bullet points
   bulletList = []
   # iterate through each key in the dict
   for key in rowDict:
      # ignore the 'sku' key in the dict
      if key != 'sku':
         # append the bullet point to the list
         bulletList.append(rowDict[key])
         # delete the key:value pair from the dict
         # rowDict.pop(key)
   rowDict['copy'] = bulletList
   # print(rowDict)

   # get the HTML started
   body = '<ul>\n'
   # iterate through each item in the copy list
   for item in rowDict['copy']:
      item = '<li>' + item + '</li>'
      body = body + item + '\n'
   body = body + '</ul>'
   # updated the copy with the html
   rowDict['copy'] = body
   # print(rowDict['copy'])

# Read the current copy csv and make a list of dictionaries
currentCopy = []
with open('currentCopy.csv') as csvfile:
      csvreader = csv.reader(csvfile, delimiter=',')
      # get the headers of the csv
      headers = next(csvreader)
      # print(headers)
      # iterate through each row in the csv
      for row in csvreader:
         # print("Row: ", row)
         rowDict = {}
         # iterate through each of the headers
         for header in headers:
            # print('Header: ', header)
            # get the item in the row list that matches the header index
            item = row[headers.index(header)]
            # remove any items that have no value
            if item == '':
               row.remove(item)
            else:
               rowDict[header] = item
         # print('rowDict: ', rowDict)
         currentCopy.append(rowDict)
      # print(currentCopy)

# Update the currentCopy with the newCopy
i = 0
for dictC in currentCopy:
   for dictN in newCopy:
      if dictC['Variant SKU'] == dictN['sku']:
         currentCopy[i]['Body (HTML)'] = dictN['copy']
         # print(currentCopy[i]['Body (HTML)'], '\n')
   i += 1

# for rowDict in currentCopy:
#    for key in rowDict:
#       print(key, ':', rowDict[key])

# Write the currentCopy to a new csv for import
csv_cols = ['Handle', 'Title', 'Body (HTML)', 'Variant SKU']
csv_file = "newProductCopy.csv"
try:
   with open(csv_file, 'w') as csvfile:
      writer = csv.DictWriter(csvfile, fieldnames=csv_cols)
      writer.writeheader()
      for data in currentCopy:
         # print(data)
         writer.writerow(data)
except IOError:
   print("I/O error")

