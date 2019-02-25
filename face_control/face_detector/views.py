from django.shortcuts import render
import face_recognition
import cv2
import numpy as np
import os
import io
from django.utils import timezone
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.http.response import JsonResponse, HttpResponse, HttpResponseRedirect
from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from .forms import PersonForm
from .models import PersonFoto, Person, Similarity
from PIL import Image
import base64
import ast
from .utils import foto_combine
import datetime



@csrf_exempt
def detect(request):
    data = {'URL': None}

    face_from_db = Person.objects.all()

    print("DB", face_from_db)

    foto_path = [item.main_foto.foto.path for item in face_from_db]

    known_face_encodings = [np.fromstring(item.main_foto.face_descriptor) for item in face_from_db]
    id_s = [item.id for item in face_from_db]

    if request.method == "POST":
        if request.FILES.get("img", None) is not None:

            frame = request.FILES["img"]
            frame.seek(0,0)
            buf = frame.read()
            sd = np.frombuffer(buf, dtype=np.uint8)
            np_img = cv2.imdecode(sd, cv2.IMREAD_UNCHANGED)

            # A list of tuples of found face locations in css (top, right, bottom, left) order
            if settings.USE_CNN_MODEL:
                face_locations = face_recognition.face_locations(np_img, model='cnn')
            else:
                face_locations = face_recognition.face_locations(np_img)


            face_encodings = face_recognition.face_encodings(np_img, face_locations)

            for number, face in enumerate(face_encodings):
                # if known_face_encodings:
                matches = face_recognition.compare_faces(known_face_encodings, face, tolerance=settings.EUCLIDEAN_DISTANCE)
                # print('MATCHES', matches)
                if True in matches:
                    first_match_index = matches.index(True)

                    # foto_path_list.append(foto_path[first_match_index])
                    # foto_loc.append(face_locations[number])
                    # person_id.append(id_s[first_match_index])

                    person = Person.objects.get(pk=id_s[first_match_index])

                    foto, name_foto = foto_combine(np_img, foto_path[first_match_index], face_locations[number])
                    buff = io.BytesIO()
                    foto.save(buff, format='PNG')
                    django_file = ContentFile(buff.getvalue())

                    similar = Similarity()
                    similar.foto.save(name_foto, django_file, False)
                    similar.save()
                    similar.person.add(person)

                    check_period = timezone.now() - datetime.timedelta(minutes=settings.FACE_COMPARE_PERIOD)
                    if not Similarity.objects.filter(person=person, is_send=True, date__gte=check_period).exists():
                        print('Check in last 10 minutes')
                        similar.is_send = True
                        similar.save()
                        data['URL'] = request.build_absolute_uri(reverse('face_detector:identity', kwargs={'uuid': similar.uuid.hex}))

                    break


            print('DATA', data)
    return JsonResponse(data)


def simple_upload(request):
    if request.method == 'POST' and request.FILES['myfile']:
        faces = []
        myfile = request.FILES['myfile']
        image = face_recognition.load_image_file(myfile)
        if settings.USE_CNN_MODEL:
            face_locations = face_recognition.face_locations(image, model='cnn')
        else:
            face_locations = face_recognition.face_locations(image)
        myfile.seek(0,0)

        if not face_locations:
            return render(request, 'face_detector/add_to_db.html', {'mess': ' IMAGE BROKEN'})

        fs = FileSystemStorage()
        main_filename = fs.save(os.path.join(settings.TEMP_FOLDER_FOR_IMAGE, myfile.name), myfile)
        main_path = fs.path(main_filename)

        for number, (top, right, bottom, left) in enumerate(face_locations):
            crop_img = image[top:bottom, left:right]
            path = os.path.join(os.path.dirname(main_path), "human{}.jpg".format(number))

            data = Image.fromarray(crop_img, 'RGB')
            buffer = io.BytesIO()
            data.save(buffer, format='PNG')
            buffer.seek(0)

            b64_img = base64.b64encode(buffer.read()).decode('ascii')
            faces.append((number, b64_img, (top, right, bottom, left)))
        form = PersonForm()
        return render(request, 'face_detector/simple_upload.html', {'thumbs': faces, 'form': form, 'main_foto': main_path})
    return render(request, "face_detector/simple_upload.html")



@csrf_exempt
def fill_base(request, *args, **kwargs):
    # faces = kwargs
    if request.method == 'POST':
        form = PersonForm(request.POST)
        coord = [ast.literal_eval(request.POST['file'])]
        path = request.POST['path']
        face_img = face_recognition.load_image_file(path)

        face_encodings = face_recognition.face_encodings(face_img, coord)
        if not face_encodings:
            return render(request, 'face_detector/add_to_db.html', {'mess': 'IMAGE BROKEN'})
        face_descriptor = face_encodings[0].tostring()

        crop_img = face_img[coord[0][0]:coord[0][2], coord[0][3]:coord[0][1]]
        data = Image.fromarray(crop_img, 'RGB')
        buff = io.BytesIO()
        data.save(buff, format='PNG')
        django_file = ContentFile(buff.getvalue())

        img_name = str(os.path.splitext(os.path.basename(path))[0])+'.png'
        if form.is_valid():
            person = form.save()
            person_img = PersonFoto(face_descriptor=face_descriptor, person=person)
            person_img.foto.save(img_name, django_file, False)
            person_img.save()
            person.main_foto = person_img
            person.save()

        if os.path.exists(path):
            os.remove(path)

        return render(request, 'face_detector/add_to_db.html', {'person': person, 'foto': person_img.foto.url})
    return render(request, 'face_detector/add_to_db.html')


def identity(request, uuid):
    similar = Similarity.objects.get(pk = uuid)
    response = HttpResponse(similar.foto, content_type="image/png")
    return response