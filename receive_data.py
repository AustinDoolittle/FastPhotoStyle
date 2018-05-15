import os
import threading
import subprocess
import time


def receive_data():
  storage_list = os.popen('sudo gsutil ls -l gs://pulse9-camera.appspot.com/Images/').read()
  tmp = storage_list.split()
  for k in tmp:
    if k.find("gs") != -1 and k.find("REALISTIC") != -1:
      os.system("sudo gsutil cp " + k + " ./get_data/")
      os.system("sudo gsutil mv " + k + " gs://pulse9-camera.appspot.com/Save/")
      k = k.split("/")[-1]
      if ".jpg" not in k:
        k_ = k + ".jpg"
        subprocess.call("mv ./get_data/" + k + " ./get_data/" + k_,
                       shell=True)
      else:
        k_ = k
      
  outfiles = os.listdir("./out_data/")
  for file in outfiles:
    print(file)
    file_ = file.replace("@", ".")
    splits = file_.split("_")[1]
    dirname = file_[file_.rfind("_")-1:]
    j=file_.split("_")[-1]
    os.system("sudo gsutil cp ./out_data/"+file +" gs://pulse9-camera.appspot.com/Result/"+splits+"/"+j)
    os.remove("./out_data/"+file)

  threading.Timer(5, receive_data).start()

if not os.path.exists("./get_data"):
  os.makedirs("./get_data")
receive_data()

