import glob, os, io
import random
import os.path
import time
from shutil import copyfile
import cv2
import imutils
from xml.dom import minidom
from os.path import basename
from PIL import Image
from object_detection.utils import dataset_util
from collections import namedtuple, OrderedDict
import pandas as pd
import tensorflow as tf
#from keras.preprocessing.image import ImageDataGenerator, array_to_img, img_to_array, load_img

#--------------------------------------------------------------------
folderCharacter = "/"  # \\ is for windows
#classList = { "b01a":0, "b01b":1, "b01c":2, "b02":3, "b03":4, "b04":5, "b05":6, "b06":7, "b07": 8, "b08": 9, "b09": 10, "b10": 11, "b11": 12 }
classList = { "pedestrian":0,"vehicle":1,"rider":2}
xmlFolder = "work/labels"
imgFolder = "work/images"
savePath = "save"
testRatio = 0.2
recordTF_out = ("train.record", "test.record")
recordTF_in = ("train.csv", "test.csv")

resizeImage = False
resize_width = 1920
imgResizedFolder = imgFolder + "_" + str(resize_width)
#---------------------------------------------------------------------

fileList = []
outputTrainFile = savePath + folderCharacter + recordTF_in[0]
outputTestFile = savePath + folderCharacter + recordTF_in[1]

if not os.path.exists(savePath):
    os.makedirs(savePath)

if not os.path.exists(imgResizedFolder):
    os.makedirs(imgResizedFolder)

def transferTF( xmlFilepath, imgFilepath, labelGrep=""):
    #print("TEST:", xmlFilepath, imgFilepath)
    if(os.path.exists(xmlFilepath) and os.path.exists(imgFilepath)):

        img_file, img_file_extension = os.path.splitext(imgFilepath)
        img_filename = basename(img_file)

        img = cv2.imread(imgFilepath)
        org_width = img.shape[1]
        org_height = img.shape[0]

        if(resizeImage==True):
            if(img.shape[1]>=img.shape[0]):
                img = imutils.resize(img, width = resize_width)
                size_ratio_w = img.shape[1] / org_width
                size_ratio_h = img.shape[0] / org_height
            else:
                img = imutils.resize(img, height = resize_width)
                size_ratio_w = img.shape[1] / org_width
                size_ratio_h = img.shape[0] / org_height

            cv2.imwrite(imgResizedFolder + folderCharacter + img_filename + img_file_extension, img)
        else:
            cv2.imwrite(imgResizedFolder + folderCharacter + img_filename + img_file_extension, img)
            size_ratio_w = 1
            size_ratio_h = 1

        imgShape = img.shape
        img_h = imgShape[0]
        img_w = imgShape[1]


        labelXML = minidom.parse(xmlFilepath)
        labelName = []
        labelXmin = []
        labelYmin = []
        labelXmax = []
        labelYmax = []
        countLabels = 0

        tmpArrays = labelXML.getElementsByTagName("filename")
        for elem in tmpArrays:
            filenameImage = elem.firstChild.data

        tmpArrays = labelXML.getElementsByTagName("name")
        for elem in tmpArrays:
            labelName.append(str(elem.firstChild.data))

        tmpArrays = labelXML.getElementsByTagName("xmin")
        for elem in tmpArrays:
            labelXmin.append(int(int(elem.firstChild.data) * size_ratio_w))

        tmpArrays = labelXML.getElementsByTagName("ymin")
        for elem in tmpArrays:
            labelYmin.append(int(int(elem.firstChild.data) * size_ratio_h))

        tmpArrays = labelXML.getElementsByTagName("xmax")
        for elem in tmpArrays:
            labelXmax.append(int(int(elem.firstChild.data) * size_ratio_w))

        tmpArrays = labelXML.getElementsByTagName("ymax")
        for elem in tmpArrays:
            labelYmax.append(int(int(elem.firstChild.data) * size_ratio_h))

        return (img_filename+img_file_extension , img_w, img_h, labelName, labelXmin, labelYmin, labelXmax, labelYmax)

    else:
        return (None, None, None, None, None, None, None, None)

def class_text_to_int(row_label):
    #tmp = row_label.split('_')
    return classList[row_label]

def split(df, group):
    data = namedtuple('data', ['filename', 'object'])
    gb = df.groupby(group)
    return [data(filename, gb.get_group(x)) for filename, x in zip(gb.groups.keys(), gb.groups)]


def create_tf_example(group, path):
    with tf.gfile.GFile(os.path.join(path, '{}'.format(group.filename)), 'rb') as fid:
        encoded_jpg = fid.read()
    encoded_jpg_io = io.BytesIO(encoded_jpg)
    image = Image.open(encoded_jpg_io)
    width, height = image.size

    filename = group.filename.encode('utf8')
    image_format = b'jpg'
    xmins = []
    xmaxs = []
    ymins = []
    ymaxs = []
    classes_text = []
    classes = []

    for index, row in group.object.iterrows():
        xmins.append(int(row['xmin']) / width)
        xmaxs.append(int(row['xmax']) / width)
        ymins.append(int(row['ymin']) / height)
        ymaxs.append(int(row['ymax']) / height)
        classes_text.append(row['class'].encode('utf8'))
        classes.append(class_text_to_int(row['class']))

    tf_example = tf.train.Example(features=tf.train.Features(feature={
        'image/height': dataset_util.int64_feature(height),
        'image/width': dataset_util.int64_feature(width),
        'image/filename': dataset_util.bytes_feature(filename),
        'image/source_id': dataset_util.bytes_feature(filename),
        'image/encoded': dataset_util.bytes_feature(encoded_jpg),
        'image/format': dataset_util.bytes_feature(image_format),
        'image/object/bbox/xmin': dataset_util.float_list_feature(xmins),
        'image/object/bbox/xmax': dataset_util.float_list_feature(xmaxs),
        'image/object/bbox/ymin': dataset_util.float_list_feature(ymins),
        'image/object/bbox/ymax': dataset_util.float_list_feature(ymaxs),
        'image/object/class/text': dataset_util.bytes_list_feature(classes_text),
        'image/object/class/label': dataset_util.int64_list_feature(classes),
    }))
    return tf_example

#-------------------------------------------------
#step 1: make train.csv / test.csv
'''
for file in os.listdir(imgFolder):
    filename, file_extension = os.path.splitext(file)
    file_extension = file_extension.lower()

    if(file_extension == ".jpg" or file_extension==".jpeg" or file_extension==".png" or file_extension==".bmp"):
        imgFile = basename(filename) + file_extension
        xmlFile = basename(filename) + ".xml"
        #print("XML:"+xmlFile, "IMG:"+imgFile)

        if(os.path.exists(xmlFolder+folderCharacter+xmlFile)):
            fileList.append(imgFile)

print("total image files: ", len(fileList))

testCount = int(len(fileList) * testRatio)
trainCount = len(fileList) - testCount

a = range(len(fileList))
test_data = random.sample(a, testCount)
#train_data = random.sample(a, trainCount)
train_data = [x for x in a if x not in test_data]
print ("Train:{} images".format(len(train_data)))
print("Test:{} images".format(len(test_data)))


csvFilename = savePath + folderCharacter + recordTF_in[0]
print("writeing to {}".format(csvFilename))

with open(csvFilename, 'a') as the_file:
    i = 0
    the_file.write("filename,width,height,class,xmin,ymin,xmax,ymax" + '\n')

    for id in train_data:
        base_filename = os.path.splitext(fileList[id])[0]
        xmlpath = xmlFolder + folderCharacter + base_filename + ".xml"
        imgpath = imgFolder + folderCharacter + fileList[id]

        (imgfile , w, h, labels, Xmin, Ymin, Xmax, Ymax) = transferTF( xmlpath, imgpath, "")
        #print(imgfile , w, h, labels, Xmin, Ymin, Xmax, Ymax)
        if(imgfile is not None):
            for id2, label in enumerate(labels):
                the_file.write(imgfile + ',' + str(w) + ',' + str(h) + ',' + labels[id2] + ',' + str(Xmin[id2]) + ',' + str(Ymin[id2]) \
                    + ',' + str(Xmax[id2]) + ',' + str(Ymax[id2]) + '\n')

            i += 1

the_file.close()
print("Total {} train records to {}".format(i, recordTF_in[0]))


csvFilename = savePath + folderCharacter + recordTF_in[1]
print("writeing to {}".format(csvFilename))

with open(csvFilename, 'a') as the_file:
    i = 0
    the_file.write("filename,width,height,class,xmin,ymin,xmax,ymax" + '\n')

    for id in test_data:
        base_filename = os.path.splitext(fileList[id])[0]
        xmlpath = xmlFolder + folderCharacter + base_filename + ".xml"
        imgpath = imgFolder + folderCharacter + fileList[id]

        (imgfile , w, h, labels, Xmin, Ymin, Xmax, Ymax) = transferTF( xmlpath, imgpath, "")
        if(imgfile is not None):
            print("TEST_labels:", labels)
            print("TEST_Xmin:", Xmin)
            print("TEST_Xmax:", Xmax)
            print("TEST_Ymin:", Ymin)
            print("TEST_Ymax:", Ymax)

            for id2, label in enumerate(labels):
                the_file.write(imgfile + ',' + str(w) + ',' + str(h) + ',' + labels[id2] + ',' + str(Xmin[id2]) + ',' + str(Ymin[id2]) \
                    + ',' + str(Xmax[id2]) + ',' + str(Ymax[id2]) + '\n')

            i += 1

the_file.close()
print("Total {} test records to {}".format(i, recordTF_in[1]))
'''
#----------------------------------------------------------
#step 2: make TFRecords: train.record / test.record

print("----------- Transfer to TF Record ---------------")

for i in (0, 1):
    output_path = savePath + folderCharacter + recordTF_out[i]
    writer = tf.io.TFRecordWriter(output_path)
    examples = pd.read_csv(savePath + folderCharacter + recordTF_in[i])
    grouped = split(examples, 'filename')

    for group in grouped:
        if group.filename !='filename':
            print(group)
            tf_example = create_tf_example(group, imgResizedFolder)
            writer.write(tf_example.SerializeToString())

    writer.close()
    print('Successfully created the TFRecords: {}'.format(output_path))

#-----------------------------------------

print("-----------make object_detection.pbtxt -----------")

filename = savePath + folderCharacter + 'object_detection.pbtxt'
print("writeing to {}".format(filename))

inv_classList = {v: k for k, v in classList.items()}
print(inv_classList)

with open(filename, 'a') as the_file:

    for i in range(1, len(classList)+1):
        print("i=", i)
        the_file.write("item {" + '\n')
        the_file.write("  id: " + str(i) + '\n')
        the_file.write("  name: '" + inv_classList[i-1] + "'" + '\n')
        the_file.write("}" + '\n\n')

the_file.close()
