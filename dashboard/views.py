from models import *
from utils import *
from django.shortcuts import render, redirect
from .models import Category, Photo, Config
import os, sys, time, datetime, random, torch, pandas
from django.core.exceptions import ObjectDoesNotExist
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
from torch.autograd import Variable

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image
from django.http import FileResponse, HttpResponse
# Create your views here.


def dashboard(request):
    category = request.GET.get('category')
    if category == None:
        photos = Photo.objects.all()
        config = Config.objects.all()
    else:
        photos = Photo.objects.filter(category__name__contains=category)
        config = Config.objects.filter(category__name__contains=category)

    categories = Category.objects.all()
    context = {'categories':categories, 'photos': photos, 'config':config}
    return render(request, 'dashboard/main.html', context)

def viewPhoto(request, pk):
    photo = Photo.objects.get(id=pk)
    return render(request, 'dashboard/photo.html', {'photo':photo})

def viewConfig(request, pk):
    config = Config.objects.get(id=pk)
    return render(request, 'dashboard/config.html', {'config':config})

def deletephoto(request):
    photos = Photo.objects.all()
    if request.method == 'POST':
        images = request.FILES.getlist('image')
        
        images.delete()
    context = {'photos':photos}
    return render(request, 'dashboard/deletephoto.html', context)

def deleteconfig(request):
    config = Config.objects.all()
    return render(request, 'dashboard/config.html', {'config':config})

def addPhoto(request):
    categories = Category.objects.all()
    if request.method == 'POST':
        data = request.POST
        images = request.FILES.getlist('image')
        category=Category.objects.get(id=data['category'])

        for image in images:
            photo = Photo.objects.create(
                category = category,
                description = data['description'],
                image=image,
            )
        return redirect('detection')

    context = {'categories':categories}
    return render(request, 'dashboard/addphoto.html', context)

def addConfig(request):
    categories = Category.objects.all()
    if request.method == 'POST':
        data = request.POST
        files = request.FILES.getlist('file')
        category=Category.objects.get(id=data['category'])

        for file in files:
                config = Config.objects.create(
                    category = category,
                    description = data['description'],
                    file=file,
                )
        return redirect('detection')
    context = {'categories':categories}
    return render(request, 'dashboard/addconfig.html', context)

def detection(request):
    category = request.GET.get('category')
    if category == None:
        photos = Photo.objects.all()
        configs = Config.objects.all()
    else:
        photos = Photo.objects.filter(category__name__contains=category)
        configs = Config.objects.filter(category__name__contains=category)

    categories = Category.objects.all()
    context = {'categories':categories, 'photos': photos, 'configs': configs}
    return render(request, 'dashboard/detection.html', context)

def selectFiles(request):
    categories = Category.objects.all()
    photos = Photo.objects.all()
    configs = Config.objects.all()

    if request.method == 'POST':
        images = request.POST.getlist('image')
        category = request.POST.get('category')
        files = request.POST.getlist('file')

        for file in files:
            if file.endswith("names"):
                names = "static/images/"+file
            elif file.endswith("cfg"):
                cfg = "static/images/"+file
            elif file.endswith("weights"):
                weights = "static/images/"+file

        IMG_SIZE=416
        CONF_THRES=0.8
        NMS_THRES=0.4
        model = Darknet(cfg, img_size=IMG_SIZE)
        model.load_weights(weights)
        model.cuda()
        model.eval()
        classes = utils.load_classes(names)
        Tensor = torch.cuda.FloatTensor
        columns = classes.copy()
        columns.insert(0, 'photoID')
        df = pandas.DataFrame(columns = columns,
                index = [])
        for image in images:
            img_path = "static/images/"+image
            img = Image.open(img_path)
            ratio = min(IMG_SIZE/img.size[0], IMG_SIZE/img.size[1])
            imw = round(img.size[0] * ratio)
            imh = round(img.size[1] * ratio)
            img_transforms = transforms.Compose([ transforms.Resize((imh, imw)),
                transforms.Pad((max(int((imh-imw)/2),0), max(int((imw-imh)/2),0), max(int((imh-imw)/2),0), max(int((imw-imh)/2),0)),
                                (128,128,128)),
                transforms.ToTensor(),
                ])
            image_tensor = img_transforms(img).float()
            image_tensor = image_tensor.unsqueeze_(0)
            input_img = Variable(image_tensor.type(Tensor))
            with torch.no_grad():
                detections = model(input_img)
                detections = utils.non_max_suppression(detections, 80, CONF_THRES, NMS_THRES)
            counts = [None] * len(columns)
            counts[0] = image.rsplit('.', maxsplit=1)[0]
            for i in range(len(classes)):
                try:
                    detections = detections[0].cpu()
                    counts[i+1] = detections[:, -1].tolist().count(i)
                except:
                    counts[i+1] = 0
            df.loc[len(df)] = counts
            plt.axis('off')
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=output.csv'
        df.to_csv(response)  # with other applicable parameters
        return response
        
    context = {'categories':categories, 'photos':photos, 'configs':configs}
    return render(request, 'dashboard/selectFiles.html', context)