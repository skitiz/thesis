import sys
import tensorflow as tf
# from tensorflow.platform import gfile
from tqdm import tqdm
import argparse
import time
import numpy as np
import pickle


def load_graph(model_file):
    graph = tf.Graph()
    graph_def = tf.GraphDef()

    with open(model_file, "rb") as f:
        graph_def.ParseFromString(f.read())
    with graph.as_default():
        tf.import_graph_def(graph_def)

    return graph


def load_labels(label_file):
    with open(label_file, "r") as fin:
        labels = [line.rstrip('\n') for line in fin]

    return labels


def read_tensor(file_name):
    input_height = 299
    input_width = 299
    input_mean = 0
    input_std = 255

    input_name = "file_reader"
    output_name = "normalized"
    file_reader = tf.read_file(file_name, input_name)
    image_reader = tf.image.decode_jpeg(file_reader, channels=3, name='jpeg_reader')
    float_caster = tf.cast(image_reader, tf.float32)
    dims_expander = tf.expand_dims(float_caster, 0)
    resized = tf.image.resize_bilinear(dims_expander, [input_height, input_width])
    normalized = tf.divide(tf.subtract(resized, [input_mean]), [input_std])
    sess = tf.Session()
    result = sess.run(normalized)

    return result


def get_accuracy(predictions, label_file):
    correct = 0


def main():
    batch = '1'
    # batch = '2'
    with open('data/test-labels' + '.pkl', 'rb') as fin:
        frames = pickle.load(fin)

    model_file = "retrained_graph.pb"
    label_file = "retrained_labels.txt"
    input_height = 299
    input_width = 299
    input_mean = 0
    input_std = 255
    input_layer = "Placeholder"
    output_layer = "final_result"
    # output_layer = "module_apply_default/InceptionV3/Logits/GlobalPool"

    graph = load_graph(model_file)
    input_name = "import/" + input_layer
    output_name = "import/" + output_layer
    #
    # print(graph.get_operations())

    with tf.Session() as sess:

        input_operation = sess.graph.get_tensor_by_name(input_name)
        output_operation = sess.graph.get_tensor_by_name('final_result:0')

        frame_predictions = []
        correct = 0

        pqbar = tqdm(total = len(frames))
        for i, frame in enumerate(frames):
            image = frame[0]
            label = frame[1]
            frameCount = frame[2]
            t = tf.gfile.FastGFile(image, 'rb').read()
            try:
                start = time.time()
                results = sess.run(output_operation, {'decodeJpeg/contents:0': t})
                prediction = results[0]
            except KeyboardInterrupt:
                print('Error making predictions!')
                continue

            frame_predictions.append([prediction, label])
            if i > 0 and i % 10 == 0:
                pqbar.update(10)


        pqbar.close()

        print("Correct :", correct, len(frame_predictions))
        accuracy = correct / float(len(frame_predictions))
        print("Accuracy:", accuracy)

    with open('data/test-results' + '.pkl', 'wb') as fout:
        pickle.dump(frame_predictions, fout)


if __name__ == '__main__':
    main()
