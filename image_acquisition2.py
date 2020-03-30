# Importing Libraries

import sys
import json
import os
import numpy as np

# Default video frame dimensions

img_height = 240
img_width = 320

offset = 25  # amount of shift in extreme points (in pixels)



def getExtrmCoords(points_list):
    '''

    :param points_list: list of x and y coordinates of joints along with their confidence scores
    :return: extreme coordinates in x and y directions

    '''

    x_coord = []
    y_coord = []

    points_max_x = 0
    points_min_x = 1000
    points_min_y = 1000

    # print("points_list: {}".format(points_list))
    for ptr in range(0, len(points_list), 3):

        # print("ptr is {} and len(points_list) is {}".format(ptr, len(points_list)))
        curr_x = points_list[ptr]
        curr_y = points_list[ptr + 1]

        if curr_x >= 0 and curr_x <= img_width:
            x_coord.append(curr_x)
            points_min_x = min(curr_x, points_min_x)
            points_max_x = max(curr_x, points_max_x)

        if curr_y >= 0 and curr_y <= img_height:
            y_coord.append(curr_y)
            points_min_y = min(curr_y, points_min_y)

    # print("x_coord: {}".format(x_coord))
    # print("y_coord: {}".format(y_coord))

    return 0 if points_min_x == 1000 else points_min_x, 0 if points_max_x == 0 else points_max_x, 0 if points_min_y == 1000 else points_min_y


    # if len(x_coord) > 0 and len(y_coord) > 0:
    #
    #
    #     points_min_x = min(i for i in x_coord if i >= 0)
    #     points_max_x = max(i for i in x_coord if i >= 0)
    #
    #     points_min_y = min(i for i in y_coord if i >= 0)




def getBoundingBox(json_path, global_val, start_frame, end_frame):
    '''

    :param json_path: path of directory containing all the json files of the respective video
    :param global_val: list of variables storing extreme coordinates
    :return: bounding box around the person in the given video
    '''

    try:
        global_min_x, global_max_x, global_min_y, global_max_y = global_val

        file_list = os.listdir(json_path)

        for json_file in file_list[start_frame - 1: end_frame]:

            arr = json_file.split('.')
            if arr[-1] != "json":
                continue

            # print("{} json started!".format(json_file))

            json_file_path = os.path.join(json_path, json_file)

            try:
                with open(json_file_path, 'r') as myfile:
                    data = myfile.read()
            except Exception as e:
                print("type error: {}".format(str(e)))
                continue

            # text = open(json_file_path, 'r')
            # data = text.read()
            try:
                obj = json.loads(data)
            except Exception as e:
                print("type error: {}".format(str(e)))
                continue

            if len(obj['people']) == 0:
                continue

            main_dict = obj['people'][0]

            # print("main_dict.keys() is {}".format(main_dict.keys()))
            pose = main_dict['pose_keypoints']
            hand_left = main_dict['hand_left_keypoints']
            hand_right = main_dict['hand_right_keypoints']

            # face = main_dict['face_keypoints']

            pose_min_x, pose_max_x, pose_min_y = getExtrmCoords(pose)
            hand_left_min_x, hand_left_max_x, hand_left_min_y = getExtrmCoords(hand_left)
            hand_right_min_x, hand_right_max_x, hand_right_min_y = getExtrmCoords(hand_right)
            # face_min_x, face_max_x, face_min_y = getExtrmCoords(face)

            global_min_x = min(global_min_x, pose_min_x, hand_left_min_x, hand_right_min_x)
            global_max_x = max(global_max_x, pose_max_x, hand_left_max_x, hand_right_max_x)

            global_min_y = min(global_min_y, pose_min_y, hand_left_min_y, hand_right_min_y)

        print("global_min_x is {} and global_max_x is {}".format(global_min_x, global_max_x))

        global_max_x = img_width if 0 else global_max_x
        global_min_x = 0 if 100000 else global_min_x
        global_min_y = 0 if 100000 else global_min_y

        if global_min_x - offset <= 0:
            global_min_x = 0
        else:
            global_min_x -= offset

        if global_max_x + offset > img_width:
            global_max_x = img_width
        else:
            global_max_x += offset

        if global_min_y - offset <= 0:
            global_min_y = 0
        else:
            global_min_y -= offset

        bounding_box = [
            global_min_x,  # top_left
            global_max_x,  # top_right
            global_min_y,  # bottom_left
            global_max_y  # bottom_right
        ]

        return bounding_box
    except Exception as e:
        print("json_path {}".format(json_path))
        print("type error: {}".format(str(e)))




def main(global_val):
    '''

    :param global_val: list of variables storing extreme coordinates
    :return: bounding box for each of the video of ChaLearn Dataset
    '''

    store_json = "/home/axp798/axp798gallinahome/store/json/"

    dir_list = os.listdir(store_json)
    for dir_name in dir_list:
        video_list = os.listdir(os.path.join(store_json, dir_name))

        for video_name in video_list:
            json_path = os.path.join(store_json, "{}/{}/".format(dir_name, video_name))

            bounding_box = getBoundingBox(json_path, global_val)

            return bounding_box

    # print("started!")
    # bounding_box = getBoundingBox(store_json, global_val)
    #
    # print(bounding_box)


if __name__ == '__main__':
    global_min_x = 100000
    global_max_x = 0

    global_min_y = 0
    global_max_y = img_height

    global_val = [global_min_x, global_max_x, global_min_y, global_max_y]

    main(global_val)


