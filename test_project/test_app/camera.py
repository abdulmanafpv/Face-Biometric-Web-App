import cv2,os,urllib.request
from imutils.video import VideoStream
import imutils
from django.shortcuts import redirect
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
import imutils
from django.utils import timezone
from django.conf import settings
from django.views.decorators import gzip
from .facerec.click_photos import click
from .facerec.train_faces import trainer
from .models import Employee, Detected
from .forms import EmployeeForm
from django.http import StreamingHttpResponse
from imutils.video import VideoStream
from imutils.video import FPS
import cv2
import pickle
import face_recognition
import datetime, time
import datetime
import sys
from cachetools import TTLCache
import xlwt
from django.db.models import Q

cache = TTLCache(maxsize=20, ttl=60)


#
def unknown():
    print('unknown people')




def identify1(frame, name, buf, buf_length, known_conf):
    if name in cache:
        return
    count = 0
    for ele in buf:
        count += ele.count(name)

    if count >= known_conf:
        # timestamp = datetime.datetime.now(tz=timezone.utc)
        timestamp = datetime.datetime.today()
        print(name, timestamp)
        cache[name] = 'detected'
        path = 'detected/{}_{}.jpg'.format(name, timestamp)
        write_path = 'media/' + path
        cv2.imwrite(path, frame)
        try:
            emp = Employee.objects.get(name=name)
            emp.detected_set.create(time_stamp=timestamp, photo=path)
        except:
            pass






# def identify1(frame, name, buf, buf_length, known_conf):
#     if name in cache:
#         return
#     count = 0
#     for ele in buf:
#         count += ele.count(name)
#
#     if count >= known_conf:
#         # timestamp = datetime.datetime.now(tz=timezone.utc)
#         timestamp = datetime.datetime.today()
#         print(name, timestamp)
#         cache[name] = 'detected'
#         path = 'detected/{}_{}.jpg'.format(name, timestamp)
#         write_path = 'media/' + path
#         cv2.imwrite(path, frame)
#         try:
#             emp = Employee.objects.get(name=name)
#             emp.detected_set.create(time_stamp=timestamp, photo=path)
#         except:
#             pass






def predict(rgb_frame, knn_clf=None, model_path=None, distance_threshold=0.5):
	if knn_clf is None and model_path is None:
		raise Exception("Must supply knn classifier either thourgh knn_clf or model_path")

	# Load a trained KNN model (if one was passed in)
	if knn_clf is None:
		with open(model_path, 'rb') as f:
			knn_clf = pickle.load(f)

	# Load image file and find face locations
	# X_img = face_recognition.load_image_file(X_img_path)
	X_face_locations = face_recognition.face_locations(rgb_frame, number_of_times_to_upsample=2)

	# If no faces are found in the image, return an empty result.
	if len(X_face_locations) == 0:
		return []

	# Find encodings for faces in the test iamge
	faces_encodings = face_recognition.face_encodings(rgb_frame, known_face_locations=X_face_locations)

	# Use the KNN model to find the best matches for the test face
	closest_distances = knn_clf.kneighbors(faces_encodings, n_neighbors=1)
	are_matches = [closest_distances[0][i][0] <= distance_threshold for i in range(len(X_face_locations))]
	# print(closest_distances)
	# Predict classes and remove classifications that aren't within the threshold
	return [(pred, loc) if rec else ("unknown", loc) for pred, loc, rec in
			zip(knn_clf.predict(faces_encodings), X_face_locations, are_matches)]






global buf_length, known_conf ,i
buf_length = 10
known_conf = 6

i = 0

model_save_path=os.path.join(
    settings.BASE_DIR, "test_app/facerec/models/trained_model.clf")

unknown_counter = 0


class VideoCamera(object):
	def __init__(self):
		self.video = cv2.VideoCapture(0)
		self.buf= [[]] * buf_length
		self.buf_length=10
		self.known_conf=6
		self.i=0
		self.process_this_frame=True
		self.imagePath = sys.argv[1]
		self.face=0



	def __del__(self):
		self.video.release()



	def get_frame(self):
		global buf_length,known_conf,i
		buf = [[]] * buf_length
		# success, image = self.video.read()
		#
		# buf_length = 10
		# known_conf = 6
		# buf = [[]] * buf_length
		# i = 0

		# process_this_frame = True


		# success, image = self.video.read()

		# buf_length = 10
		# known_conf = 6
		# buf = [[]] * buf_length
		# i = 0
		# process_this_frame = True
		# Grab a single frame of video
		ret, frame = self.video.read()



		# Resize frame of video to 1/4 size for faster face recognition processing
		small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

		# Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
		rgb_frame = small_frame[:, :, ::-1]

		if self.process_this_frame:
			# predictions = predict(rgb_frame, model_path="test_app/facerec/models/trained_model.clf")
			predictions = predict(rgb_frame, model_path=model_save_path)

		# print(predictions)

		process_this_frame = not self.process_this_frame

		face_names = []

		for name, (top, right, bottom, left) in predictions:
			top *= 4
			right *= 4
			bottom *= 4
			left *= 4

			# Draw a box around the face
			cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

			# Draw a label with a name below the face
			cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
			font = cv2.FONT_HERSHEY_DUPLEX
			cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
			cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
			cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
			cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
			cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

			identify1(frame, name, self.buf, self.buf_length, self.known_conf)
			# identify1(frame, name, unknown,self.buf, self.buf_length, self.known_conf)


			face_names.append(name)
			# if name=='unknown':
			# 	time.sleep(5)
				# unknown()
				# time.sleep(30)
				# self.video.release()

		# 	now = datetime.datetime.today()
			# 	# roi_color = frame[right:right+ left, top:top + bottom]
			# 	# cv2.imwrite(str(bottom) + str(left) + '_faces.jpg', roi_color)
			# 	p = os.path.sep.join(['test_app/facerec/new', "shot_{}.png".format(str(now).replace(":", ''))])
			# 	# reverse('registration')
			#
			# 	cv2.imwrite(p , frame)

		# cv2.imwrite('faces_detected.jpg{now}', frame)
			# print("[INFO] Image faces_detected.jpg written to filesystem: ", status)


		self.buf[self.i] = face_names
		self.i = (self.i + 1) % self.buf_length
		# frame_flip = cv2.flip(frame,1)
		ret, frame = cv2.imencode('.jpg', frame)

		return frame.tobytes()



















# class VideoCamera(object):
# 	def __init__(self):
# 		self.video = cv2.VideoCapture(0)
# 		self.buf= [[]] * buf_length
# 		self.buf_length=10
# 		self.known_conf=6
# 		self.i=0
# 		self.process_this_frame=True
#
#
#
# 	def __del__(self):
# 		self.video.release()
#
#
#
# 	def get_frame(self):
# 		global buf_length,known_conf,i
# 		buf = [[]] * buf_length
# 		# success, image = self.video.read()
# 		#
# 		# buf_length = 10
# 		# known_conf = 6
# 		# buf = [[]] * buf_length
# 		# i = 0
#
# 		# process_this_frame = True
#
#
# 		# success, image = self.video.read()
#
# 		# buf_length = 10
# 		# known_conf = 6
# 		# buf = [[]] * buf_length
# 		# i = 0
# 		# process_this_frame = True
# 		# Grab a single frame of video
# 		ret, frame = self.video.read()
#
# 		# Resize frame of video to 1/4 size for faster face recognition processing
# 		small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
#
# 		# Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
# 		rgb_frame = small_frame[:, :, ::-1]
#
# 		if self.process_this_frame:
# 			# predictions = predict(rgb_frame, model_path="test_app/facerec/models/trained_model.clf")
# 			predictions = predict(rgb_frame, model_path=model_save_path)
#
# 		# print(predictions)
#
# 		process_this_frame = not self.process_this_frame
#
# 		face_names = []
#
# 		for name, (top, right, bottom, left) in predictions:
# 			top *= 4
# 			right *= 4
# 			bottom *= 4
# 			left *= 4
#
# 			# Draw a box around the face
# 			cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
#
# 			# Draw a label with a name below the face
# 			cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
# 			font = cv2.FONT_HERSHEY_DUPLEX
# 			cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
# 			cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
# 			cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
# 			cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
# 			cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
#
#
#
#
#
# 			identify1(frame, name, self.buf, self.buf_length, self.known_conf)
# 			# identify1(frame, name, unknown,self.buf, self.buf_length, self.known_conf)
#
#
# 			face_names.append(name)
#
# 		self.buf[self.i] = face_names
# 		self.i = (self.i + 1) % self.buf_length
# 		# frame_flip = cv2.flip(frame,1)
# 		ret, frame = cv2.imencode('.jpg', frame)
# 		return frame.tobytes()




