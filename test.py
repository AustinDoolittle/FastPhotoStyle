import os
import threading
import numpy as np
import subprocess
import time
import skimage.io
import cv2
from PIL import Image


received_dir = "./get_data/"


def test():
  files = os.listdir(received_dir)
  for file in files:
    if ".jpg" in file:
      print("file name: {}".format(file))
      people = skimage.io.imread(received_dir+file)
      people = cv2.imread(received_dir+file)
      skimage.io.imsave(received_dir+file, people)
      subprocess.call("sudo rm ./images/contents/*.jpg", shell=True)
      subprocess.call("sudo rm ./results/*", shell=True)
      img = Image.open("./get_data/"+file)
      if img.size[1]>1200 or img.size[0]>600:
          subprocess.call("sudo convert -resize 50% ./get_data/"+file+" ./get_data/"+file, shell=True)
      elif img.size[1]>800 and img.size[1]<1200:
          subprocess.call("sudo convert -resize 25% ./get_data/"+file+" ./get_data/"+file, shell=True)
      else:
          pass
	
      #img = img.resize((406,722), Image.ANTIALIAS)
      img.save("./get_data/"+file)
      subprocess.call("cp ./get_data/"+file+" ./images/contents/", shell=True)
      subprocess.check_call("python demo.py --content_image_path ./images/contents/"+file+" --style_image_path ./images/styles/"+file.split('_')[0] + ".jpg --output_image_path ./results/" + file , shell=True)
      img=skimage.io.imread("./results/"+file)
      skimage.io.imsave("./out_data/"+file,img)
      subprocess.call("rm ./get_data/"+file, shell=True)
    
  threading.Timer(5, test).start()
test()
