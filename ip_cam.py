import cv2
import face_recognition
# from ultralytics import YOLO
from cam_process import *
import datetime 
import numpy as np
import os,sys,shutil
import pickle
from tracker import Tracker
import os.path
import subprocess

directory = 'faces'
tracker = Tracker()

id_count = 0
face_locations = []
face_encodings = []
face_names = []

if not os.path.exists("learn"):
    os.makedirs("learn")

# vidcap = cv2.VideoCapture('outpy_2.avi')
# success,frame = vidcap.read()
font = cv2.FONT_HERSHEY_DUPLEX
CAP = Camera('rtsp://admin:admin@10.61.42.208')
def Load_face_data():
    global known_face_names
    global known_face_encodings
    with open('dataset_faces.dat', 'rb') as f:
        all_face_encodings = pickle.load(f)

    known_face_names = list(all_face_encodings.keys())
    known_face_encodings = np.array(list(all_face_encodings.values()))

def calculate_delta(x,y):
    result = int(abs(x-y))
    if result < 5:
        return True
    else:
        return False
def clear_folder(folder):
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))


known_face_names = []
known_face_encodings = []
clear_folder("unknown_temp")
clear_folder("learn")
Load_face_data()
learning = False
finish_learning = True
# Run the Event Loop
while True:
    try:
        # success,OG_frame = vidcap.read()
        OG_frame =CAP.getFrame()
        # if np.shape(frame) != ():
        #     cv2.imwrite("now.jpg",frame)
        
        # predict = model.predict(source=frame,conf=0.2,iou=0.2)
        frame = np.array(OG_frame)
        
        back_up_OG = OG_frame

        OG_frame = cv2.resize(OG_frame, (0, 0), fx=0.5, fy=0.5)
        small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
        face_locations = face_recognition.face_locations(small_frame,1,model = "hog")
        
        face_encodings = face_recognition.face_encodings(small_frame, face_locations)
        face_names = []
        track_data = []
        dectect_result =[] 
        for index,face_encoding in enumerate(face_encodings):
            # See if the face is a match for the known face(s)
            name = "Unknown"
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding, 0.3)
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            score = 0

            # print(f"dst:{face_distances}")
            if  matches[best_match_index]:
                name = known_face_names[best_match_index]
                score = round(min(face_distances),2)
              
            face_names.append(name)
            (top, right, bottom, left) = face_locations[index]
            x1 = int(left)
            y1 = int(top)
            x2 = int(right)
            y2 = int(bottom)
            print(f"score:{score}")
            track_data.append([x1, y1, x2, y2, score])
            dectect_result.append([x1, y1, x2, y2, name])

        for (top, right, bottom, left), name in zip(face_locations, face_names):
            for filename in os.listdir(directory):
                # file_name = filename.split("_")[0]
                if name == filename:
                    f = os.path.join(directory, filename)
                    for root, dirs, files in os.walk(f, topdown=False):
                        for img_name in files:
                            img = cv2.imread(os.path.join(root, img_name))
                            break
                        height, width, channels = img.shape
                        width = int((width*(bottom-top))/height)
                        height = int(bottom - top)
                        img = cv2.resize(img, (width, height))
                        x,y = right,top
                        OG_frame[y:y+height, x:x+width] = img
                        cv2.rectangle(OG_frame, (x, y), (x+width, y+height), (0, 0, 255), 1)
                        # Draw a label with a name below the face
                        cv2.rectangle(OG_frame, (right, bottom +10), (right + width, bottom), (0, 0, 255), cv2.FILLED)
                        cv2.putText(OG_frame, f"{name}", (right, bottom + 10), font, 0.5, (255, 255, 255), 1)
                        break
            # Draw a box around the faceq
            cv2.rectangle(OG_frame, (left, top), (right, bottom), (0, 255, 0), 1)
        
        tracker.update(OG_frame, track_data)
        print(f"-------")

        result=[]
        for track in tracker.tracks:
            bbox = track.bbox
            x1, y1, x2, y2 = bbox
            track_id = track.track_id
            for face in dectect_result:
                x_1 = face[0]
                y_1 = face[1]
                x_2 = face[2]
                y_2 = face[3]
                name = face[4]
                if calculate_delta(x1,x_1) and calculate_delta(y1,y_1) and calculate_delta(x2,x_2) and calculate_delta(y2,y_2):
                    result.append([track_id,name])
                    # print("yes")
                    if name ==  "Unknown":
                        new_ID_path = f"unknown_temp/{track_id}"
                        if not os.path.exists(new_ID_path):
                            os.makedirs(new_ID_path)
                        
                        file_list = os.listdir(new_ID_path)

                        scaling = round(100/(x2-x1),2)
                        unkown_img= OG_frame[int(y1):int(y2),int(x1):int(x2)]
                        spacer = int(abs(y2-y1)/5)
                        unkown_img_HD= back_up_OG[int(y1*2-spacer):int(y2*2+spacer),int(x1*2-spacer):int(x2*2+spacer)]
                        # land_mark = face_recognition.face_landmarks(unkown_img)[0]
                        # print(land_mark)
                        # for k in land_mark.values():
                        #     for (x, y) in k:
                        #         cv2.circle(unkown_img, (x, y), 1, (0, 0, 255), -1)
                        unkown_img = cv2.resize(unkown_img, (0, 0), fx=scaling, fy=scaling)
                        U_height, U_width, U_channels = unkown_img.shape
                        OG_frame[10:10 + U_height,10:10 + U_width] = unkown_img
                        cv2.rectangle(OG_frame, (10, 10), (10+U_width, 10+U_height), (0, 0, 255), 1)
                        cv2.rectangle(OG_frame, (10,10+U_height), (10+U_width, 20+U_height), (0, 0, 255), cv2.FILLED)
                        now = datetime.datetime.now()
                        date_str = now.strftime("%H_%M_%S")
                        if len(file_list) < 5:
                            newimg_path = f"unknown_temp/{track_id}/{date_str}.png"
                            cv2.imwrite(newimg_path,unkown_img_HD)
                            cv2.putText(OG_frame, f"Learn in :{int(5 -len(file_list))}", (10, 20+U_height), font, 0.5, (255, 255, 255), 1)
                        elif(len(file_list) >= 5):
                            new_learn_path = f"learn/{track_id}"
                            if not os.path.exists(new_learn_path):
                                os.makedirs(new_learn_path)
                                learn_face_path = f"learn/{track_id}/{date_str}.png"
                                cv2.imwrite(learn_face_path,unkown_img_HD)
                            new_detect_path = f"faces/{track_id}"
                            if not os.path.exists(new_detect_path):
                                os.makedirs(new_detect_path)
                                detect_face_path = f"faces/{track_id}/{date_str}.png"
                                cv2.imwrite(detect_face_path,unkown_img_HD)
                            learning = True   
                            cv2.putText(OG_frame, f"Learning", (10, 20+U_height), font, 0.5, (255, 255, 255), 1)
                    else:
                        new_ID_path = f"unknown_temp/{track_id}"
                        if os.path.exists(new_ID_path):
                            clear_folder(new_ID_path)
                        
            cv2.rectangle(OG_frame, (int(x1), int(y1-10)), (int(x2), int(y1)), (0, 0, 255), cv2.FILLED)
            cv2.putText(OG_frame, f"ID:{track_id}", (int(x1), int(y1)), font, 0.5, (255, 255, 255), 1)
        print(result)

        if learning  == True:
            p = subprocess.Popen(['python', 'face_encoder_add.py'])
            poll = p.poll()
            finish_learning = False
            learning = False
        if finish_learning == False and learning == False:
            if poll is None:
                Load_face_data()
                clear_folder("learn")
                finish_learning = True
        cv2.imshow('frame',OG_frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    except Exception as e:
        print(f"error: {e}")
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"type:{exc_type}, name: {fname}, line: {exc_tb.tb_lineno}")
        # time.sleep(0.5)
