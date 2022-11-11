# Replaces old product copy with the new product copy
# Requires a csv of the current products and a csv of the new copy
# Outputs a file that can be imported into Shopify
import csv
import numpy as np

# Clean up the raw csv by removing empty stuff
cleaned = []
with open('HEASEL-copy.csv') as csvfile:
      csvreader = csv.reader(csvfile, delimiter=',')
      for row in csvreader:
         # print("Row: ", row)
         for item in row:
            if item == '':
               row.remove(item)
         if row == ['']:
            continue
         else:
            cleaned.append(row)

# Remove the Site Description from the cleaned list
cleaned = cleaned[: len(cleaned) - 1]

# Figure out how many products there are if each product is 6 rows
numProds = len(cleaned) / 6

# Spilt the cleaned list into a list of lists to isolate products
rowList = []
rowList = np.array_split(cleaned, numProds)

# Get all the items from each sub-list in rowList into a single list
prodList = []
for row in rowList:
   tempList = []
   for prod in row:
      for item in prod:
         tempList.append(item)
   prodList.append(tempList)

# Copy out the items of the list that we do actually want
finalList = []
for prod in prodList:
   tempList = []
   for i in range(0, len(prod)):
      if i % 2:
         if i == 1:
            continue
         else:
            tempList.append(prod[i])
      else:
         if i == 0:
            tempList.insert(0, prod[i])
   finalList.append(tempList)

# Convert the lists into dictionaries and add to newCopy list
newCopy = []
headers = ['sku', 'bullet1', 'bullet2', 'bullet3', 'bullet4', 'bullet5']
for row in finalList:
   rowDict = {}
   for header in headers:
      item = row[headers.index(header)]
      rowDict[header] = item
   newCopy.append(rowDict)

# Convert the bullets to a list with HTML added
for rowDict in newCopy:
   bulletList = []
   for key in rowDict:
      if key != 'sku':
         bulletList.append(rowDict[key])
   rowDict['copy'] = bulletList

   # Combine the html and copy into one item
   body = '<ul>\n'
   for item in rowDict['copy']:
      # Add the bold tags around the item header
      splitItem = item.split("-")
      for chunk in splitItem:
         if splitItem.index(chunk) == 0:
            chunk = chunk.rstrip(chunk[-1])
            chunk = "<b>" + chunk + "</b>" + " -"
            item = chunk + splitItem[1]
      item = '<li>' + item + '</li>'
      body = body + item + '\n'
   body = body + '</ul>'
   rowDict['copy'] = body

# Read the current copy csv and make a list of dictionaries
currentCopy = []
with open('currentCopy.csv') as csvfile:
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

# Update the currentCopy with the newCopy
i = 0
for dictC in currentCopy:
   for dictN in newCopy:
      if dictC['Variant SKU'] == dictN['sku']:
         currentCopy[i]['Body (HTML)'] = dictN['copy']
   i += 1

# Write the currentCopy to a new csv for import
csv_cols = ['Handle', 'Title', 'Body (HTML)', 'Variant SKU']
csv_file = "newProductCopy.csv"
try:
   with open(csv_file, 'w', newline='') as csvfile:
      writer = csv.DictWriter(csvfile, fieldnames=csv_cols)
      writer.writeheader()
      for data in currentCopy:
         writer.writerow(data)
except IOError:
   print("I/O error")
