# 使用預訓練model -> ssdlite_mobilenet_v1_coco
## 前提
### 環境安裝
建議使用docker，可以參照<a href="https://github.com/ian40306/docker">docker/</a>  
EX: sudo docker run --gpus all -it --name ian -p 50000:22 -p 50001:8888 ian40306/u18-n10.0-c7.6.5-tf1.15.0-x11  
  
若使用上述作法，可以參照下列做法:  
移動至tensorflow資料夾  
$cd /usr/local/lib/python3.6/dist-packages/tensorflow  
安裝model  
$git clone https://github.com/tensorflow/models.git  
安裝protobuf  
wget -O protobuf.zip https://github.com/google/protobuf/releases/download/v3.0.0/protoc-3.0.0-linux-x86_64.zip unzip protobuf.zip  
移動至research  
$cd models/research/  
進行相關環境設定  
$python setup.py install  
$apt-get install python3-gdbm -y  
$apt install protobuf-compiler -y  
protoc object_detection/protos/*.proto --python_out=.  
### 資料處理:  
照片必須符合下列規則:  
1.有照片(jpg)  
2.有label(xml或csv都可以)  
