import cv2
import face_recognition
# ----------------------
from keras.preprocessing import image as image_utils
from keras.applications.imagenet_utils import decode_predictions
from keras.applications.imagenet_utils import preprocess_input
from keras.applications import VGG16
import numpy as np
import argparse
# ----------------------
process_this_frame = True

# load the VGG16 network pre-trained on the ImageNet dataset
print("[INFO] loading network...")
model = VGG16(weights="imagenet")

def read_frames():
    cap = cv2.VideoCapture(0)
    while(True):
        # Capture frame-by-frame
        ret, frame = cap.read()
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = small_frame[:, :, ::-1]
        if process_this_frame:
            # Find all the faces and face encodings in the current frame of video
            face_locations = face_recognition.face_locations(rgb_small_frame)
            if len(face_locations)>0 or len(face_locations)==0:
                for face in face_locations:
                    top, right, bottom, left = face
                    # Scale back up face locations since the frame we detected in was scaled to 1/4 size
                    top *= 4
                    right *= 4
                    bottom *= 4
                    left *= 4
                    # Draw a box around the face
                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                    print("[INFO] loading and preprocessing image...")
                    # image = image_utils.load_img(frame, target_size=(224, 224))
                    image = image_utils.img_to_array(frame)
                    # our image is now represented by a NumPy array of shape (224, 224, 3),
                    # assuming TensorFlow "channels last" ordering of course, but we need
                    # to expand the dimensions to be (1, 3, 224, 224) so we can pass it
                    # through the network -- we'll also preprocess the image by subtracting
                    # the mean RGB pixel intensity from the ImageNet dataset
                    image = cv2.resize(image, (224, 224))
                    image = np.expand_dims(image, axis=0)
                    image = preprocess_input(image)

                    # classify the image
                    print("[INFO] classifying image...")
                    preds = model.predict(image)
                    P = decode_predictions(preds)
                    print(P)
        # Display the resulting frame
        cv2.imshow('frame',frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()

def main():
    read_frames()
if __name__== "__main__":
  main()