# from django.contrib import admin
from django.urls import path
from . import views

app_name='courseIndex'

urlpatterns = [
    path('', views.index,name='index'),
    path('nowCourseData/', views.nowCourseData,name='nowCourseData'),
    path('getbeforecourse/<week>',views.getbeforecourse,name='getbeforecourse' ),
    path('getnextcourse/<week>',views.getnextcourse,name='getnextcourse' ),
    path('getstage/<classname>',views.getstage,name='getstage' ),
    path('getteacher/<classname>/<stagename>/<sort>',views.getteacher,name='getteacher' ),
    path('changeTeacher/<teacherNamePre>/<teacherNameNex>/<sort>',views.changeTeacher,name='changeTeacher' ),
    path('updataCourse/<week>',views.updataCourse,name='updataCourse' ),
    path('savedata/', views.savedata, name='savedata'),
]