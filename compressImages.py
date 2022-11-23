# Compress images using Python like a smart person
# Must run inside the folder with images at the moment

# Import required libraries
import os
from PIL import Image

# Function to compress images and save them in a folder
def compressMe(file):
   filepath = os.path.join(os.getcwd(), file)
   picture = Image.open(filepath)

   # Hop into the folder to save and hop back out again
   os.chdir("compressedImages")
   picture.save("Compressed-"+file, "JPEG", optimize = True, quality = 60)
   os.chdir('..')
   return

def main():
   # See if the special folder exists and create it if not
   if os.path.exists("compressedImages") != True:
      os.mkdir("compressedImages")

   # Iterate through the files in the directory
   cwd = os.getcwd()
   for file in os.listdir(cwd):
      filepath = os.path.join(os.getcwd(), file)
      filesize = os.path.getsize(filepath) / 1000

      # Only save images less than 900 kb
      if filesize > 900:
         compressMe(file)
   print("Done")

main()