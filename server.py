import json
from time import time

from PIL import Image
from flask import Flask, request, Response

# assuming that script is run from `server` dir
import sys, os
sys.path.append(os.path.realpath('..'))

import numpy as np
import argparse
import tensorflow as tf
import cv2
import pathlib

from object_detection.utils import ops as utils_ops
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as vis_util


# patch tf1 into `utils.ops`
utils_ops.tf = tf.compat.v1

# Patch the location of gfile
tf.gfile = tf.io.gfile


# For test examples acquisition
SAVE_DETECT_FILES = False
SAVE_TRAIN_FILES = False

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

model = []
category_index = []

class Rect:
    # face bounding boxes
    def __init__(self, x, y, w, h, name, predict_proba):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.name = name
        self.predict_proba = str(predict_proba)

    def data(self):
        return { k:v for k, v in self.__dict__.items() if k != 'img'}


def load_model(model_path):
    model = tf.saved_model.load(model_path)
    # model = tf.io.gfile.FastGFile(model_path, 'rb').read()
    return model


def run_inference_for_single_image(model, image):
    image = np.asarray(image)
    # The input needs to be a tensor, convert it using `tf.convert_to_tensor`.
    input_tensor = tf.convert_to_tensor(image)
    # The model expects a batch of images, so add an axis with `tf.newaxis`.
    input_tensor = input_tensor[tf.newaxis,...]
    
    # Run inference
    output_dict = model(input_tensor)

    # All outputs are batches tensors.
    # Convert to numpy arrays, and take index [0] to remove the batch dimension.
    # We're only interested in the first num_detections.
    num_detections = int(output_dict.pop('num_detections'))
    output_dict = {key: value[0, :num_detections].numpy()
                   for key, value in output_dict.items()}
    output_dict['num_detections'] = num_detections

    # detection_classes should be ints.
    output_dict['detection_classes'] = output_dict['detection_classes'].astype(np.int64)
   
    # Handle models with masks:
    if 'detection_masks' in output_dict:
        # Reframe the the bbox mask to the image size.
        detection_masks_reframed = utils_ops.reframe_box_masks_to_image_masks(
                                    output_dict['detection_masks'], output_dict['detection_boxes'],
                                    image.shape[0], image.shape[1])      
        detection_masks_reframed = tf.cast(detection_masks_reframed > 0.5, tf.uint8)
        output_dict['detection_masks_reframed'] = detection_masks_reframed.numpy()
    
    return output_dict



# for CORS
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST')  # Put any other methods you need here
    return response


@app.route('/')
def index():
    return Response(open('./static/detect.html').read(), mimetype="text/html")


im_width  = 800.0
im_height = 600.0

is_model_loaded = False

@app.route('/detect', methods=['POST'])
def detect():
    try:
        image_stream = request.files['image']  # get the image
        image = Image.open(image_stream)
        # im_width, im_height = image.size
        # Set an image confidence threshold value to limit returned data
        threshold = request.form.get('threshold')
        if threshold is None:
            threshold = 0.5
        else:
            threshold = float(threshold)
        
        image_np = np.array(image)
        image_np = cv2.resize(image_np, (800, 600))
        output_dict = run_inference_for_single_image(model, image_np)
        # Visualization of the results of a detection.
        # vis_util.visualize_boxes_and_labels_on_image_array(
            # image_np,
            # output_dict['detection_boxes'],
            # output_dict['detection_classes'],
            # output_dict['detection_scores'],
            # category_index,
            # instance_masks=output_dict.get('detection_masks_reframed', None),
            # use_normalized_coordinates=True,
            # line_thickness=8)
        
        boxes = output_dict['detection_boxes']
        max_boxes_to_draw = boxes.shape[0]
        # get scores to get a threshold
        scores = output_dict['detection_scores']
        # this is set as a default but feel free to adjust it to your needs
        min_score_thresh=.5
        
        boxess = []
        
        for i in range(min(max_boxes_to_draw, boxes.shape[0])):
            b = output_dict['detection_boxes'][i]
            xmin = b[1] * im_width
            ymin = b[0] * im_height
            xmax = b[3] * im_width
            ymax = b[2] * im_height
            class_name = "unknown"
            if scores is not None and scores[i] > min_score_thresh:
                class_name = category_index[output_dict['detection_classes'][i]]['name']
            else:
                continue
            f = Rect(xmin,ymin, xmax-xmin, ymax-ymin, class_name, scores[i])
            boxess.append(f)
            print(f.data())
            
        # faces = recognize(detection.get_faces(image, threshold))

        j = json.dumps([b.data() for b in boxess])
        print("Result:", j)

        # save files
        # if SAVE_DETECT_FILES and len(faces):
        #    id = time()
        #    with open('test_{}.json'.format(id), 'w') as f:
        #        f.write(j)

        #    image.save('test_{}.png'.format(id))
        #    for i, f in enumerate(faces):
        #        f.img.save('face_{}_{}.png'.format(id, i))

        return j

    except Exception as e:
        import traceback
        traceback.print_exc()
        print('POST /detect error: %e' % e)
        return e



if __name__ == '__main__':

    if not is_model_loaded:
        parser = argparse.ArgumentParser(description='Detect objects inside webcam videostream')
        parser.add_argument('-m', '--model', type=str, required=True, help='Model Path')
        parser.add_argument('-l', '--labelmap', type=str, required=True, help='Path to Labelmap')
        args = parser.parse_args()
        model = load_model(args.model)
        category_index = label_map_util.create_category_index_from_labelmap(args.labelmap, use_display_name=True)
        is_model_loaded = True
    
    print("starting server...")
    app.run(debug=True, host='0.0.0.0', ssl_context='adhoc')
    # app.run(host='0.0.0.0')
