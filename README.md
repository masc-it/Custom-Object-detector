# Tensorflow Object Detection with Tensorflow 2

## Dataset
- Get images (train, test)
- resize images
- LabelImg
- xml_to_csv
- Upload to Kaggle
	
## Installation, Training & export (Colab)

## Test 1

Live detection from local webcam

`python detect_from_webcam.py -m <path_to_model_dir> -l  <complete_pbtxt_path>`

## Test 2
Live detection from local webcam, with webserver (mobile, desktop)

`python server.py -m <path_to_model> -l  <complete_pbtxt_path>`