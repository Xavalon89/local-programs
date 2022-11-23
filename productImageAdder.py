# Reads a csv to find products that have at most 1 image, searches our product image folder
# for the product, checks to see if we have images to upload. (Have to decide at what number of
# images we should add. Currently it would be at least those with more than 1.) For the products
# that have images, urls are created for each image using their file names. The SKU and image
# urls are added to a csv to be uploaded to Shopify.

import csv
from datetime import date
import glob
import os

# Creates a list of lists that contain SKU, handle, and title for each product that needs images
needs_images = []
with open('currentCopy.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    current_sku = ''
    current_title = ''
    current_handle = ''
    second_image = False
    for row in reader:
        # print(row, '\n')
        if row[2]:
            if not second_image and current_sku:
                needs_images.append(
                    [current_sku, current_title, current_handle])
            current_sku = row[14]
            current_title = row[1]
            current_handle = row[0]
            second_image = False
        else:
            second_image = True

# for item in needs_images:
#    print(item, '\n')

# Creates a dictionary for products which have images ready to be added where
# the keys are the SKUs and the values are lists containing the product SKU,
# handle, and image file names.
sku_with_images = {}
for sku in needs_images:
    images = []
    root = 'D:/Software/Dropbox (Royal Brush Mfg Inc)/Pubfiles - Web/art.royalbrush.com/_2021 Shopify/assets/Product Images/**/' + \
        sku[0] + '/*.jpg'
    #  print(root)
    files = glob.glob(root, recursive=True)
    for file in files:
        images.append(os.path.basename(file))
    if images:
        images.append(sku[1])
        images.append(sku[2])
        sku_with_images[sku[0]] = images

# Writes a new CSV using the dictionary from the last step that can be uploaded to Shopify.
current_date_time = date.today()
file_title = "productsWithImages-" + str(current_date_time) + ".csv"
with open(file_title, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Handle', 'Title', 'Variant SKU',
                    'Image Src', 'Image Alt Text'])
    for sku, images in sku_with_images.items():
        writer.writerow([images[-1], images[-2], sku,
                        'https://cdn.shopify.com/s/files/1/0577/0035/2197/files/' + images[0], sku + " - " + images[-2]])
        for image in images[1:-2]:
            writer.writerow(
                [images[-1], '', '', 'https://cdn.shopify.com/s/files/1/0577/0035/2197/files/' + image, sku + " - " + images[-2]])

# print(sku_with_images)
# print(needs_images)
