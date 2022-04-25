
from django.shortcuts import render
from test_app.camera import VideoCamera
from .models import Employee, Detected
from .forms import EmployeeForm
from django.http import StreamingHttpResponse
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.shortcuts import render, get_object_or_404
from .facerec.click_photos import click
from .facerec.train_faces import trainer
import datetime
from django.utils import timezone
from django.db.models import Q
from cachetools import TTLCache
import cv2,os,urllib.request
cache = TTLCache(maxsize=20, ttl=60)
# Create your views here.






def identify1(frame, name, buf, buf_length, known_conf):
	if name in cache:
		return
	count = 0
	for ele in buf:
		count += ele.count(name)

	if count >= known_conf:
		timestamp = datetime.datetime.now(tz=timezone.utc)
		print(name, timestamp)
		cache[name] = 'detected'
		path = 'detected/{}_{}.jpg'.format(name, timestamp)
		write_path = 'media/' + path
		cv2.imwrite(write_path, frame)
		try:
			emp = Employee.objects.get(name=name)
			emp.detected_set.create(time_stamp=timestamp, photo=path)
		except:
			pass







def index(request):
    date_formatted = datetime.datetime.today().date()
    date = request.GET.get('search_box', None)
    if date is not None:
        date_formatted = datetime.datetime.strptime(date, "%Y-%m-%d-%s").date()
    det_list = Detected.objects.filter(time_stamp__date=date_formatted).order_by('time_stamp').reverse()
    print(det_list)

    # date_formatted = datetime.datetime.today().date()
    det_list = Detected.objects.filter(time_stamp__date=date_formatted).order_by('time_stamp').reverse()
    return render(request, 'home.html',{'det_list':det_list,'date': date_formatted})



def registration(request):
    emp_list = Employee.objects.all()
    if request.method == "POST":
        form = EmployeeForm(request.POST, request.FILES)
        if form.is_valid():
            emp = form.save()
            print(emp)
            return HttpResponseRedirect(reverse('index'))
    else:
        form = EmployeeForm()
    return render(request, 'registration.html', {'emp_list': emp_list,'form':form})


# def edit(request,emp_id):
#     form =  EmployeeForm
#     if request.method == 'POST':
#         emp = Employee.objects.filter(id=emp_id)
#         form = EmployeeForm(request.POST, request.FILES, instance=emp)
#         if form.is_valid():
#             form.save()
#             return redirect('index')
#     else:
#         emp = Employee.objects.filter(id=emp_id)
#         form = EmployeeForm()
#     return render(request,'edit.html',{})



def add_photos(request):
	emp_list = Employee.objects.all()
	return render(request, 'add_photos.html', {'emp_list': emp_list})

def capturing_photos(request, emp_id):
    cam = cv2.VideoCapture(0)
    emp = get_object_or_404(Employee, id=emp_id)
    click(emp.name, emp.id, cam)

    # k = cv2.waitKey(1)
    #
    # if k % 256 == 27:
    #     # ESC pressed
    #     print("Escape hit, closing...")
    #     cam.release()
    #     cv2.destroyAllWindows()

    return HttpResponseRedirect(reverse('add_photos'))



def train_data(request):
    return render(request,'train_data.html')



def train_model(request):
    trainer()
    return HttpResponseRedirect(reverse('index'))

# def detected(request):
#     if request.method == 'GET':
#         date_formatted = datetime.datetime.today().date()
#         date = request.GET.get('search_box', None)
#         if date is not None:
#             date_formatted = datetime.datetime.strptime(date, "%Y-%m-%d").date()
#         det_list = Detected.objects.filter(time_stamp__date=date_formatted).order_by('time_stamp').reverse()
#         print(det_list)


    # if request.method == "POST":
    #     form = EmployeeForm(request.POST,request.FILES)
    #     if form.is_valid():
    #         emp = form.save()
    #         print(emp)
    #         return HttpResponseRedirect(reverse('index'))
    # else:
    #     form = EmployeeForm()
    #
    #
    # # det_list = Detected.objects.all().order_by('time_stamp').reverse()
    # return render(request, 'home.html', {'det_list': det_list, 'date': date_formatted,'form':form})


def gen(camera):
	while True:
		frame = camera.get_frame()
		yield (b'--frame\r\n'
				b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


# def video_feed(request):
#     return StreamingHttpResponse(VideoCamera.get_frame(),
#                     content_type='multipart/x-mixed-replace; boundary=frame')
    # except:
    #     return render(request, 'home.html')



def video_feed(request):
	return StreamingHttpResponse(gen(VideoCamera()),
					content_type='multipart/x-mixed-replace; boundary=frame')


def search_result(request):
    result = None
    Query = None
    if 'q' in request.GET:
        Query = request.GET.get('q')
        result = Detected.objects.all().filter(Q(time_stamp__icontains=Query))

    if request.method == "POST":
        form = EmployeeForm(request.POST, request.FILES)
        if form.is_valid():
            emp = form.save()
            print(emp)
            return HttpResponseRedirect(reverse('index'))
    else:
        form = EmployeeForm()
    return render(request,'serch-result.html',{'result':result,'form':form})





