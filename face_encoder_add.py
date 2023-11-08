
import face_recognition
from sklearn import svm
import os
import joblib
import pickle
import numpy as np
# Load a sample picture and learn how to recognize it.
def add_face_encodeding(dir):
    
    global all_face_encodings
    with open('dataset_faces.dat', 'rb') as f:
        all_face_encodings = pickle.load(f)
    # known_face_names = list(all_face_encodings.keys())
    # known_face_encodings = np.array(list(all_face_encodings.values()))
    # Training directory
    if dir[-1]!='/':
        dir += '/'
    train_dir = os.listdir(dir)
  
    # Loop through each person in the training directory
    for person in train_dir:
        pix = os.listdir(dir + person)
        print(f"encoding:{person}")
        # Loop through each training image for the current person
        for person_img in pix:
            # Get the face encodings for the face in each image file
            face = face_recognition.load_image_file(dir + person + "/" + person_img)
            face_bounding_boxes = face_recognition.face_locations(face)
  
            # If training image contains exactly one face
            if len(face_bounding_boxes) == 1:
                face_enc = face_recognition.face_encodings(face)[0]
                # Add face encoding for current image 
                # with corresponding label (name) to the training data
                print(f"encoding:{person}-{person_img}")
                all_face_encodings[person] = face_enc
               
            else:
                print(person + "/" + person_img + " can't be used for training")
    with open('dataset_faces.dat', 'wb') as f:
        pickle.dump(all_face_encodings, f)
directory = 'learn'
all_face_encodings ={}

add_face_encodeding(directory)
