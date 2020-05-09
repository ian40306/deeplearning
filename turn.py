import tensorflow as tf

graph_def_file="/usr/local/lib/python3.6/dist-packages/tensorflow/models/research/object_detection/training/tflite_graph.pb"
input_arrays=["normalized_input_image_tensor"]
output_arrays=['TFLite_Detection_PostProcess','TFLite_Detection_PostProcess:1','TFLite_Detection_PostProcess:2','TFLite_Detection_PostProcess:3']
input_tensor={"normalized_input_image_tensor":[1,300,300,3]}

converter = tf.lite.TFLiteConverter.from_frozen_graph(graph_def_file, input_arrays, output_arrays,input_tensor)
converter.allow_custom_ops=True
tflite_model = converter.convert()
open("detect.tflite", "wb").write(tflite_model)
