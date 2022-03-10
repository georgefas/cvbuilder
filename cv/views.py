#from contextlib import nullcontext
#from json import JSONDecoder
from django.shortcuts import render,redirect
from rest_framework.decorators import api_view
#from rest_framework.response import Response

from django.http.response import HttpResponse
from django.http import FileResponse

from io import BytesIO,StringIO
import io
from xhtml2pdf import pisa
from django.template.loader import get_template

from django.http import HttpResponse
import requests
import json
import docx2txt
import PyPDF2

from .resumeparse import get_resume_data

def home(request):
    return render(request,'cv/home.html')


def cvdata(request):
    if request.method == 'POST':
        data =  request.POST['data_dict_json']
        print(type(data))        
  
    return render(request,'cv/resume-data.html')


def cvdata2(request):
    my_text = request.session.get('my_text')         
  
    return render(request,'cv/resume-data2.html',{'resume_data':my_text})



@api_view(['POST', 'GET'])
def docxprocess(request):
    data_dict = request.data['data_dict']
    
    
    return docxview(request)

@api_view(['POST', 'GET'])
def cvprocess(request):
    data_dict = request.data['data_dict']
    

    return render_to_pdf(
            'cv/resume.html',            {
                'pagesize':'A4',
                'data_dict': data_dict,
                
            }
        )



def render_to_pdf(template_src, context_dict):
    template = get_template(template_src)
    context = context_dict
    html  = template.render(context)
    result = io.BytesIO()

    pdf = pisa.pisaDocument(StringIO(html), result, encoding='UTF-8')
    if not pdf.err:
        response  = HttpResponse(result.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="resume.pdf"'        
        return response
    return HttpResponse('We had some errors<pre>%s</pre>' % html)

def docxview(request,data_dict):    
    data_raw= requests.utils.unquote(data_dict)
    data = json.loads(data_raw)
    data_dict= data['data_dict']
    return render(request,'cv/resume-doc-test.html',{'data_dict':data_dict})

def resume_upload(request):
    if request.method == 'POST' and request.FILES['myfile']:
        myfile = request.FILES['myfile']
        print(myfile.content_type)
        try:
            my_text = docx2txt.process(myfile)
            
        except Exception as e:        
            pdfReader = PyPDF2.PdfFileReader(myfile)        
            #pageObj = pdfReader.getPage(0)
            my_text = ""
            for i in range(pdfReader.numPages):
                pageObj = pdfReader.getPage(i)
                my_text += pageObj.extractText()
        request.session['my_text'] = str(get_resume_data(my_text))

        return redirect('cvdata2')
        #print(get_resume_data(my_text))

            #print(pageObj.extractText())
        

        #return redirect('second')

        # filename = fs.save(myfile.name, myfile)
        # uploaded_file_url = fs.url(filename)
        # return render(request, 'cv/resume-upload.html', {
        #     'extracted_text': get_resume_data(my_text)
        # })
    return render(request, 'cv/resume-upload.html')

