import cv2
import numpy as np
from flask import Response
from config import AppState  
import dlib
import threading
import time


# i combined two diffrent models to take whats best from each one.
# Dlib models for short mode
dlib_detector = dlib.get_frontal_face_detector()
dlib_shape = dlib.shape_predictor("/home/jonahrpi/Desktop/idcamproject/shape_predictor_68_face_landmarks.dat")
dlib_recog = dlib.face_recognition_model_v1("/home/jonahrpi/Desktop/idcamproject/dlib_face_recognition_resnet_model_v1.dat")

# SSD+Caffe models for long mode
PROTO_PATH = "deploy.prototxt"
MODEL_PATH = "res10_300x300_ssd_iter_140000_fp16.caffemodel"
ssd_net = cv2.dnn.readNetFromCaffe(PROTO_PATH, MODEL_PATH)


class FrameBG:

    #this function is here and not in cam_init because it runs more smoothly here
    #function thaat captures the frames from the camera
    def capture_frames():
        state = AppState()
        while state.running: #i have a var called running for when camera active
            framethere, frame = state.camera.read()
            if not framethere: #if not frame
                continue
            with state.lock:
                state.global_frame = frame.copy()


    def generate_regular_frames():
        """Raw stream without detection"""
        from classes.cam_init import CamInit
        state = AppState()
        CamInit.reset_state()
        CamInit.start_camera(640, 480)
        # start capture thread
        threading.Thread(target=FrameBG.capture_frames, daemon=True).start()

        while state.running:
            with state.lock:
                if state.global_frame is None:
                    continue
                frame = state.global_frame.copy()
            jpg = cv2.imencode('.jpg', frame)[1].tobytes()
            yield (b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + jpg + b"\r\n")


    def generate_frames(mode):
        from classes.cam_init import CamInit
        state = AppState()

        # Regular: no detection
        if mode == 'regular':
            return Response(
                FrameBG.generate_regular_frames(),
                mimetype='multipart/x-mixed-replace; boundary=frame'
            )

        # Face-detection modes: reset and start camera
        CamInit.reset_state()
        if mode == 'short':
            CamInit.start_camera(320, 240)
        else:  # long
            CamInit.start_camera(640, 480)

        # launch capture thread
        state.running = True
        threading.Thread(target=FrameBG.capture_frames, daemon=True).start()

        frame_count = 0
        SKIP = state.PROCESS_EVERY_N_FRAMES

        while state.running:
            with state.lock:
                if state.global_frame is None:
                    continue
                frame = state.global_frame.copy()

            frame_count += 1

            if mode == 'short':
                # skip frames
                if frame_count % SKIP != 0:
                    out = cv2.resize(frame, (640, 480), interpolation=cv2.INTER_LINEAR)
                    jpg = cv2.imencode('.jpg', out)[1].tobytes()
                    yield (b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + jpg + b"\r\n")
                    continue

                # dlib HOG detection
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                faces = dlib_detector(rgb, 0)
                for f in faces:
                    shape = dlib_shape(rgb, f)
                    enc = np.array(dlib_recog.compute_face_descriptor(rgb, shape))
                    if state.known_face_encodings:
                        dists = np.linalg.norm(state.known_face_encodings - enc, axis=1)
                        idx = np.argmin(dists)
                        label = state.known_face_labels[idx] if dists[idx] < 0.6 else 'Unknown'
                    else:
                        label = 'Unknown'

                    if state.last_label != label:
                        print("here1")
                        state.identnames.append(label)
                        if label == "Unknown":
                            state.identclass.append(0)
                            state.identid.append(0)
                        else:
                            print(idx)
                            print(state.known_face_labels[idx])
                            print(state.known_face_id[idx])
                            state.identclass.append(state.known_class_of_face[idx])
                            state.identid.append(state.known_face_id[idx])
                        state.last_label = label
                    elif label == "Unknown" and state.last_label != "Unknown":
                        print("here2")
                        state.unknowns_fc += 1
                        state.identnames.append(label + "." + str(state.unknowns_fc))
                        state.identclass.append(0)
                        state.identid.append(0)
                     
                    x, y, w, h = f.left(), f.top(), f.width(), f.height()
                    cv2.rectangle(frame, (x,y),(x+w,y+h),(0,255,0),1)
                    cv2.putText(frame, label, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0),1)
                # resize and stream
                frame = cv2.resize(frame, (640,480), interpolation=cv2.INTER_LINEAR)
                jpg = cv2.imencode('.jpg', frame)[1].tobytes()
                yield (b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + jpg + b"\r\n")

            else:  # long mode
                (h, w) = frame.shape[:2]
                blob = cv2.dnn.blobFromImage(cv2.resize(frame,(300,300)),1.0,(300,300),(104.0,177.0,123.0))
                ssd_net.setInput(blob)
                detections = ssd_net.forward()
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                for i in range(detections.shape[2]):
                    conf = detections[0,0,i,2]
                    if conf < 0.5: continue
                    box = (detections[0,0,i,3:7]*np.array([w,h,w,h])).astype(int)
                    x1,y1,x2,y2 = box
                    rect = dlib.rectangle(x1,y1,x2,y2)
                    shape = dlib_shape(rgb, rect)
                    enc = np.array(dlib_recog.compute_face_descriptor(rgb, shape))
                    if state.known_face_encodings:
                        dists = np.linalg.norm(state.known_face_encodings - enc, axis=1)
                        idx = np.argmin(dists)
                        label = state.known_face_labels[idx] if dists[idx]<0.6 else 'Unknown'
                    else:
                        label = 'Unknown'

                    if state.last_label != label:
                        print("here1")
                        state.identnames.append(label)
                        if label == "Unknown":
                            state.identclass.append(0)
                            state.identid.append(0)
                        else:
                            print(idx)
                            print(state.known_face_labels[idx])
                            print(state.known_face_id[idx])
                            state.identclass.append(state.known_class_of_face[idx])
                            state.identid.append(state.known_face_id[idx])
                        state.last_label = label
                    elif label == "Unknown" and state.last_label != "Unknown":
                        print("here2")
                        state.unknowns_fc += 1
                        state.identnames.append(label + "." + str(state.unknowns_fc))
                        state.identclass.append(0)
                        state.identid.append(0)
                        
                    cv2.rectangle(frame,(x1,y1),(x2,y2),(0,255,0),1)
                    cv2.putText(frame, label, (x1,y1-10), cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,255,0),1)
                # resize and stream
                out = cv2.resize(frame,(640,480), interpolation=cv2.INTER_LINEAR)
                jpg = cv2.imencode('.jpg',out)[1].tobytes()
                yield (b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + jpg + b"\r\n")
