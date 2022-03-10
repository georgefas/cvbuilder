from django.urls import path
from .views import cvdata,cvprocess,docxview,docxprocess,resume_upload,cvdata2,home

urlpatterns = [
   path('',home,name='home'),
   path('resume/',cvdata,name='cvdata'),
   path('resume/resumepdf/',cvprocess ,name='cvprocess'),
   path('resume/docxprocess/',docxprocess,name='docxprocess'),
   path('resume/docx/<str:data_dict>/',docxview,name='docxview'),
   path('resume/upload/',resume_upload,name='resume_upload'),
   path('old-cv/',cvdata2,name='cvdata2'),
]