from django.shortcuts import render,render_to_response
from django.template import RequestContext
from django.http import JsonResponse
from .models import Lecturers,College,Subjects,Incharge, Students, Offerd_course, Section, Course, Attendence
import json
from django.db.models import F
import datetime
from django.views.decorators.csrf import requires_csrf_token, ensure_csrf_cookie, csrf_protect

db_tables = [{"id":1,"tables":'Students'},{"id": 2,"tables":'Course'},{"id": 3,"tables":'Subjects'},{"id": 4,"tables":'Teacher assignment'},{"id": 5,"tables": 'Attendence'},{"id": 6,"tables": 'Lecturers'}]

def excel_upload(request):
    return render_to_response("excel.html", {"tables":db_tables},RequestContext(request))

def _sectionHandler(request, id):
    #if request.method == 'POST':
    print('Section')
    #body_unicode = request.body.decode('utf-8')
    #body = json.loads(body_unicode)
    #in_id = body["id"]
    #collegeCode=body["collegeCode"]
    #lectureId = body["userID"]
    #subCode = body['subCode']
    sec = Incharge.objects.get(id = id)
    studentList = list(Students.objects.filter(sectionFK = sec.sectionFK).values('studentInfoFK_id', 'studentInfoFK__studentName'))
    print(studentList)
    return JsonResponse(json.dumps(studentList),safe=False)
@csrf_protect
def _openAttendance(request):
    if request.method == 'POST':
        print("_openAttendence")
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        ID = body["id"]
        date = datetime.datetime.strptime(body["Date"],"%d/%m/%Y").strftime("%Y-%m-%d")
        sesFrom = body["From"]
        sesTo = body["To"]
        print('Section')
        lecIncharge = Incharge.objects.get(id = int(ID))
        #need to add old data
        attUpdate = list(Attendence.objects.filter(subjectFK = lecIncharge.subjectFK, sessionfrom = sesFrom, sessionto = sesTo, sessionDate = date).annotate(studentID=F("studentFK_id")).values("studentID"))
        print("attUpdate",attUpdate)
        studentList = list(Students.objects.filter(collegeFK = lecIncharge.lecturerFK.collegeFK,sectionFK = lecIncharge.sectionFK).annotate(studentID=F("studentInfoFK_id"),studentName=F("studentInfoFK__studentName")).values('studentID','studentName'))
        if(len(studentList) == 0):
            raise Http404("Please Contact Pricipal for assigning classes")
        if len(attUpdate) == 0:
            print("studentList",studentList)
            #return JsonResponse(json.dumps(studentList),safe=False)
            return JsonResponse(json.dumps({"old":0,"studentList":studentList}),safe=False)    
        
        oldStatusEntry = []
        for student in studentList:
            if student.studentID in attUpdate:
                oldStatusEntry.append(1)
            else:
                oldStatusEntry.append(0)

        print("asdsa",studentList, "asdas",oldStatusEntry)
        

        #print(sec)
        #print(studentList)
        return JsonResponse(json.dumps({"old":1,"studentList":studentList, "StautsField":oldStatusEntry}),safe=False)

@csrf_protect
def subject_handeled_info(request):    
    if request.method == 'POST':
        print("_openAttendence")
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        collegeCode=body["collegeCode"]
        userid = body["userID"]
        
        subjectHandled = list(Incharge.objects.filter(lecturerFK__collegeFK = collegeCode,lecturerFK_id = userid).annotate(subCode = F('subjectFK__subjectCode'),subName = F('subjectFK__subjectName')).values('subCode', 'subName').distinct())
        
        listOfSubs = []
        for subjectInfo in subjectHandled:
            #print(subjectInfo['subCode'])
            listingSubs = list(Incharge.objects.filter(lecturerFK__collegeFK = collegeCode,lecturerFK_id = userid, subjectFK_id = subjectInfo['subCode']).annotate(subYear = F('subjectFK__subjectYear'),secName = F('sectionFK__sectionName'), year = F('sectionFK__year')).values('id','subYear','secName', 'year'))
            #print(listingSubs)
            dataAdd = {'subCode':subjectInfo['subCode'], 'subName':subjectInfo['subName'],'sections':listingSubs}
            listOfSubs.append(dataAdd)
            #lister.update
        print(listOfSubs)
        if(len(listOfSubs) == 0):
            raise JsonResponse("Please Contact Pricipal for assigning classes")
        return JsonResponse(listOfSubs,safe=False)


@csrf_protect
def _studentUnderSub(request):
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    collegeCode=body["collegeCode"]
    subject = body["subID"]
    lecture = body["userID"]
    section = body["sec"]
    year = body["year"]

    subjectObj = Subjects.objects.get(subjectCode = subject)
    print('subjectObj',subjectObj)

    courseObj = Offerd_course.objects.get(courseFK = subjectObj.courseFK_id)
    print('courseObj',courseObj)

    sectionObj = Section.objects.get(sectionName = sec, year = year)
    print('sectionObj',sectionObj)

    students = list(Students.objects.filter(collegeFK_id = collegeCode, sectionFK = sectionObj, courseFK = courseObj).values('StudentRollNo','studentName'))
    #students = list(Students.objects.filter(collegeFK_id = collegeCode,courseFK_id = subjectObj.courseFK).all())
    print(students)
    return JsonResponse({'students':students})


@csrf_protect
def _markingAttendance(request):
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)

    status = int(body["status"])
    
    #make code more efficent by search the id and delete
    if status == 0:
        return JsonResponse({'status':'success'})
    elif status == 2:
        #incID = body["id"]
        #subCode = body["subCode"]
        #sessionFrom = body["sessionfrom"]
        #sessionTo = body["sessionto"]
        #Date = body["date"]

        #lecIncharge = Incharge.objects.get(id = int(incID))
        #attUpdate = Attendence.objects.filter(subjectFK = lecIncharge.subjectFK, sessionfrom = sessionFrom, sessionto = sessionTo, sessionDate = Date)
        #print(attUpdate)
        #attUpdate.delete()
        pass
    else:
        incID = body["id"]
        subCode = body["subCode"]
        sessionFrom = body["sessionfrom"]
        sessionTo = body["sessionto"]
        Date = datetime.datetime.strptime(body["date"],"%d/%m/%Y").strftime("%Y-%m-%d")
        lecIncharge = Incharge.objects.get(id = int(incID))
        attendies = body["absenties"]
        for stuID in attendies:
            stu = Students.objects.get(studentInfoFK_id = int(stuID))
            attInsert = Attendence(subjectFK = lecIncharge.subjectFK, studentFK = stu,sessionfrom = "10:00", sessionto = "10:40", sessionDate = Date, studentstatus = 0)
            attInsert.save()
@csrf_protect    
def _studentUnderSub(request):
    if request.method == 'GET':
        body_unicode = request.body.decode('utf-8') 
        body = json.loads(body_unicode)
        collegeCode=body["collegeCode"]
        lectureId = body["userID"]
        subID = body['subID']

