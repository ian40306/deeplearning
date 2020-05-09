# 使用預訓練model -> ssdlite_mobilenet_v1_coco
## 前提
### 環境安裝
建議使用docker，可以參照<a href="https://github.com/ian40306/docker">docker</a>  
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
  
移動至object_detection資料夾  
$cd /usr/local/lib/python3.6/dist-packages/tensorflow/models/research/object_detection/  
創建存放照片、lable的資料夾、放置資料處理過後的資料夾以及工作資料夾
$mkdir images labels training_model training work  
下載轉檔程式:  
$git clone https://github.com/ian40306/deeplearning.git  
  
將資料轉成tfrecord  
$cp deeplearning/make_dataset.py .  
修改make_dataset.py裡面的參數:  
第20行修改為所要執行的label  
第21、22行修改為所要儲存的位置(若參照本做法則不用修改)  
### 處理model包
$wget http://download.tensorflow.org/models/object_detection/ssd_mobilenet_v1_coco_2018_01_28.tar.gz  
$tar -xzvf ssd_mobilenet_v1_coco_2018_01_28.tar.gz  
$cp sample/config/
## 訓練
移動py檔案  
$cp legacy/train.py .  
開始訓練  
$CUDA_VISIBLE_DEVICES=0,1,2 python train.py \\  
  --logtostderr \\  
  --pipeline_config_path=ssd_mobilenet_v1_coco.config \\  
  --train_dir=training_model \\  
  --num_clones=3
### 說明:
pipeline_config_path為所使用的model  
train_dir為所放置dataset  
num_clones為使用GPU數目  
CUDA_VISIBLE_DEVICES為限制哪幾張GPU可以被使用  
## 轉成tflite
$python export_tflite_ssd_graph.py \\  
--pipeline_config_path=/usr/local/lib/python3.6/dist-packages/tensorflow/models/research/object_detection/training_model/pipeline.config \\  
--trained_checkpoint_prefix=/usr/local/lib/python3.6/dist-packages/tensorflow/models/research/object_detection/training_model/model.ckpt-69914 \\  
--output_directory=/usr/local/lib/python3.6/dist-packages/tensorflow/models/research/object_detection/training \\  
--add_postprocessing_op=true  
