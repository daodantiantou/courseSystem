from django.shortcuts import render,HttpResponse
from django.http import JsonResponse
from orderClasses.order_classes import model
from courseRelative.models import UekBasicStudent,UekInteriorLeave,UekAdminUser,UekAdminRole,UekBasicClass,UekBasicRoom,UekBasicDirection
from .models import UekCourseDayData,UekBasicStage,UekCourseStagePriority,UekBasicTeacher,UekCourseTSPriorty,UekCourseWeekData,UekCourseOutClasses

import time,numpy as np,pandas as pd
import datetime,calendar,json

# 班级排序（根据学生信息，是否校外班级，当前阶段是否结束来进行排序）
def orderClass():
    class_order = []
    classes = UekBasicClass.objects.filter(class_cate=0) | UekBasicClass.objects.filter(class_cate=1)
    classes = classes.filter(class_status=0)
    for i in classes:
        # 判断班级成分
        class_students1 = UekBasicStudent.objects.filter(class_id=i.id).filter(student_status=0)
        class_students2 = UekBasicStudent.objects.filter(class_id=i.id).filter(student_status=1)
        class_students = class_students1 | class_students2
        student_num = class_students.count()
        boshi_num = class_students.filter(student_education='博士').count()
        shuoshi_num = class_students.filter(student_education='硕士').count()
        benke_num = class_students.filter(student_education='本科').count()
        dazhuan_num = class_students.filter(student_education='大专').count()
        gaozhong_num = class_students.filter(student_education='高中').count()
        zhongzhuan_num = class_students.filter(student_education='中专').count()
        qita_num = class_students.filter(student_education='其他').count()
        # 判断是否校外(是为1，不是为0)
        type = i.class_cate
        is_out = 1
        if type == 0 or type == 1:
            is_out = 0
        # 判断阶段是否完成
        is_stage_end = 1
        stageId = i.stage_id
        # 获取当前阶段已上天数
        # now_stage_days = UekCourseDayData.objects.filter(s_id=stageId).count()
        # 当前阶段对象
        now_stage_obj = UekBasicStage.objects.filter(id=i.stage_id)[0]
        # 当前阶段名称
        now_stage = now_stage_obj.stage_name
        is_None = UekCourseDayData.objects.filter(c_id=i.id).filter(s_id=i.stage_id)
        # 当前阶段已上天数(如果未上则为0)
        now_stage_days = is_None.order_by('-long_time')[0].long_time if is_None else 0
        # 查找对应阶段
        stage_obj=UekBasicStage.objects.filter(id=stageId)
        stage_days = stage_obj[0].stage_day
        # if not stage_obj:
            # initDayData(i)
            # print("查无此阶段，出错班级为%s"%(i.class_name))
            # continue
        # newStageId=UekBasicClass.objects.filter(class_name=i.class_name)[0].stage_id
        # stage_days = UekBasicStage.objects.filter(id=newStageId)[0].stage_day
        if now_stage_days == 0 or now_stage_days == stage_days:
            is_stage_end = 0
        # 计算班级优先级
        data = [[student_num, boshi_num, shuoshi_num, benke_num, dazhuan_num, gaozhong_num, zhongzhuan_num,
                              qita_num, is_out, is_stage_end]]
        res = model.predict(data)[0][0]
        class_order.append(res)
    class_order = list(reversed(np.argsort(np.array(class_order))))
    clas=[]
    for i in range(len(classes)):
        mark=int(class_order[i])
        clas.append(classes[mark])
    return clas

# 教师带课优先级初始化（根据教师方向阶段进行初始化，默认优先级都为0）
def setTeacherPriority():
    teachers=UekBasicTeacher.objects.all()
    for t in teachers:
        # 如果已有则不需要初始化
        if t.teacher_priority:
            continue
        did=t.dir_id
        # 如果没有方向id说明不是带课老师,不需要设置带课优先级
        if did == None:
            continue
        # 按顺序获取该方向下的所有阶段
        dirStages = UekBasicStage.objects.filter(dir_id=did).order_by("order_num")
        stageStr = '0|'
        for i in dirStages:
            stageStr += i.stage_name + ":0,"
        # 去掉最后一个逗号
        t.teacher_priority = stageStr[:-1]
        t.save()

# 录入教师阶段优先级（根据修改后的教师优先级，将数据录入表中）
def writeTeacherPriorty():
    # 过滤非带课老师
    teachers=UekBasicTeacher.objects.exclude(teacher_priority=0).all()
    stages=UekBasicStage.objects
    for t in teachers:
        if UekCourseTSPriorty.objects.filter(teacher=t):
            UekCourseTSPriorty.objects.filter(teacher=t).delete()
        priorty=t.teacher_priority
        priortys=priorty.split("|")[1].split(',')
        for s in priortys:
            record = UekCourseTSPriorty(teacher=t)
            stage_name=s.split(':')[0]
            stage_priorty=s.split   (':')[1]
            # 如果优先级为0，则不录入
            if stage_priorty=='0':
                continue
            stage_object=stages.filter(stage_name=stage_name).first()
            if stage_priorty == None:
                continue
            record.stage=stage_object
            record.priorty=stage_priorty
            record.save()

# 获取下周周数（）
def getNextWeek():
    week=time.strftime("%W")
    if int(week) == 53 or int(week) == 0:
        return 1
    else:
        return int(week)+1


# 考虑到每年最后一周也就是53周同时也是新年的第一周
def getNowWeek():
    week = time.strftime("%W")
    if int(week) == 0:
        return 53
    return int(week)


def getBeforeWeek():
    week = time.strftime("%W")
    if int(week)==0:
        return 52
    elif int(week) == 1:
        return 53
    else:
        return int(week)-1

# 获取日期列表，参数=预测周数-当前周数 返回预测周数对应的日期列表
def get_weekday_list(num=1):
    today1 = datetime.date.today()
    today2 = datetime.date.today()
    oneday = datetime.timedelta(days=1)
    oneweek = datetime.timedelta(days=7)
    m1 = calendar.MONDAY
    m2 = calendar.SUNDAY

    if num < 0:
        today1 -= oneweek * abs(num)
        today2 -= oneweek * abs(num)
        while today1.weekday() != m1:
            today1 -= oneday
        while today2.weekday() != m2:
            today2 += oneday
    elif num>0:
        today1 += oneweek * abs(num)
        today2 += oneweek * abs(num)
        while today1.weekday() != m1:
            today1 -= oneday
        while today2.weekday() != m2:
            today2 += oneday
    elif num == 0:
        while today1.weekday() != m1:
            today1 -= oneday
        while today2.weekday() != m2:
            today2 += oneday

    nextMonday = today1.strftime('%Y%m%d')
    nextSunday = today2.strftime('%Y%m%d')

    date_list = [d.strftime("%Y-%m-%d") for d in pd.date_range(nextMonday, nextSunday, freq="D")]
    date_list_changed = []
    for i in date_list:
        one = i.split('-')
        time = ['月', '日']
        time.insert(0, one[1])
        time.insert(2, one[2])
        time1 = ''.join(time)
        date_list_changed.append(time1)
    return date_list,date_list_changed

# 教师下周状态初始化
def setTeacherStatus():
    # 将所有老师状态初始化为0000000
    teachers=UekBasicTeacher.objects.all()
    for t in teachers:
        t.teacher_week_status='0000000'
        t.save()
    # 获取请假老师
    qingjiateachers = UekInteriorLeave.objects.filter(status=2)
    # 如果没有请假老师，则不操作
    if qingjiateachers:
        for qjt in qingjiateachers:
            teacherId = qjt.teacher_id
            teacherobj = UekBasicTeacher.objects.filter(id=teacherId)[0]
            # 请假开始时间
            start_time=qjt.start_time
            # 请假结束时间
            end_time=qjt.end_time
            status=qjt.status
            # 请假天数
            daynum=(end_time-start_time).days+1
            start_time=start_time.strftime('%Y-%m-%d')
            time_list,b=get_weekday_list()
            num=0
            for i in range(7):
                # 为0 则跳出
                if daynum==num:
                    break
                if start_time!=time_list[i]:
                    continue
                status_list=list(teacherobj.teacher_week_status)
                for j in range(daynum):
                    status_list[i+j]='1'
                    teacherobj.teacher_week_status="".join(status_list)
            teacherobj.save()

# 判断班级是否开班,如果to值为next则判断下周是否开班，如果为now则判断当前周是否开班
def isBegin(class0bj,to='next'):
    date=class0bj.start_time.strftime("%Y%m%d")
    week=datetime.datetime.strptime(date,"%Y%m%d").strftime("%W")
    week = int(week)
    if week < 20:
        week += 2000
    elif week > 20:
        week +=1900

    if to == 'next':
        if week <= getNextWeek()+2000:
            return True
        return False
    elif to == 'now':
        if week <= getNowWeek()+2000:
            return True
        return False

# 根据前置课程获取阶段优先级排序列表stages,sortarr
def bstageToAstage(nowstage):
    stages=UekCourseStagePriority.objects.filter(pre_course=nowstage).order_by('-priority')
    stageList=[i.next_course for i in stages]

    # nparr=np.array(levelarr)
    # sortarr=list(reversed(np.argsort(nparr)))
    return stageList

# 获取某阶段下的教师优先级
def orderTeacher(stage):

    # 根据优先级进行排序
    recore_list=UekCourseTSPriorty.objects.filter(stage=stage).order_by('-priorty')
    teacherList=[i.teacher for i in recore_list]
    return teacherList


# 根据阶段列表进行排课
def stages2course(stageList,d,class_data,date_list,week,c):
    stageId = c.stage_id
    for i in stageList:
        if (c.class_name[:5] == 'MUIF' and i.stage_name == "产品经理与测试") or (
                c.class_name[:5] == 'MUIF' and i.stage_name == "运营"):
            continue
        if (c.class_name[:5] == 'MUIDF' and i.stage_name == "c4d") or (
                c.class_name[:5] == 'MUIDF' and i.stage_name == "商业插画") or (
                c.class_name[:5] == 'MUIDF' and i.stage_name == "可用性原则与测试"):
            continue
        # 是否阶段启用
        if i.stage_status == 1:
            continue
        # 阶段是否已经完成
        end_stage = UekCourseDayData.objects.filter(c_id=c.id).order_by('-id')[0].endstage
        end_stage_list = end_stage.split('|') if end_stage else []
        # 如果已完成则进入下一个阶段
        if str(i.id) in end_stage_list:
            continue
        teacher_list = orderTeacher(i)
        # 如果阶段没有对应老师
        if not teacher_list:
            continue
        # 循环对应教师
        for t in teacher_list:
            t_status = list(t.teacher_week_status)
            # 该教师是否空闲
            if t_status[d] == '1':
                continue
            class_data['con'].append(i.stage_name)
            class_data['teacher'].append(t.teacher_name)
            # 修改布道师周状态
            teacher_week_status_list1 = list(t.teacher_week_status)
            teacher_week_status_list1[d] = '1'
            t.teacher_week_status = "".join(teacher_week_status_list1)
            t.save()
            # 添加数据到日记录表中
            if not UekCourseDayData.objects.filter(daytime=date_list[d]).filter(c_id=c.id):
                day_data = UekCourseDayData(s_id=i.id)
                # 如果是从未上过的阶段则从0 开始,如果是接着前面的阶段则加1
                obj = UekCourseDayData.objects.filter(s_id=i.id).filter(c_id=c.id)
                new_stage_time = 1 if not obj else obj.order_by('-long_time')[0].long_time + 1
                day_data.long_time = new_stage_time
                day_data.week = week
                day_data.teacher = t.id
                day_data.room = c.room_id
                day_data.c_id = c.id
                day_data.daytime = date_list[d]
                if not end_stage:
                    day_data.endstage = stageId
                else:
                    new_endStage = end_stage.split('|')
                    new_endStage.append(str(stageId))
                    day_data.endstage = '|'.join(new_endStage)
                day_data.save()
                c.stage_id = i.id
                c.save()
            else:
                print(2)
            break
        else:
            print("%s阶段没有空闲老师，进入下个阶段" % i.stage_name)
            continue
        break
    else:
        class_data['con'].append('')
        class_data['teacher'].append('')
        print("%s+没有同时合适的阶段和老师" % (c.class_name))

# 根据某一阶段排老师
def stages2teacher(i,d,class_data,date_list,week,c):
    stageId = c.stage_id
    end_stage = UekCourseDayData.objects.filter(c_id=c.id).order_by('-id')[0].endstage
    teacher_list = orderTeacher(i)
    # 循环对应教师
    for t in teacher_list:
        t_status = list(t.teacher_week_status)
        # 该教师是否空闲
        if t_status[d] == '1':
            continue
        class_data['con'].append(i.stage_name)
        class_data['teacher'].append(t.teacher_name)
        # 修改布道师周状态
        teacher_week_status_list1 = list(t.teacher_week_status)
        teacher_week_status_list1[d] = '1'
        t.teacher_week_status = "".join(teacher_week_status_list1)
        t.save()
        # 添加数据到日记录表中
        if not UekCourseDayData.objects.filter(daytime=date_list[d]).filter(c_id=c.id):
            day_data = UekCourseDayData(s_id=i.id)
            # 如果是从未上过的阶段则从0 开始,如果是接着前面的阶段则加1
            obj = UekCourseDayData.objects.filter(s_id=i.id).filter(c_id=c.id)
            new_stage_time = 1 if not obj else obj.order_by('-long_time')[0].long_time + 1
            day_data.long_time = new_stage_time
            day_data.week = week
            day_data.teacher = t.id
            day_data.room = c.room_id
            day_data.c_id = c.id
            day_data.daytime = date_list[d]
            if not end_stage:
                day_data.endstage = stageId
            else:
                new_endStage = end_stage.split('|')
                new_endStage.append(str(stageId))
                day_data.endstage = '|'.join(new_endStage)
            day_data.save()
            c.stage_id = i.id
            c.save()
        break
    else:
        print("%s阶段没有空闲老师，进入下个阶段" % i.stage_name)

# 整理显示时班级展现顺序
def classShow(class_data):
    # 对班级号进行排序 例如1907在1910之前
    class_data_sort = []
    for i in class_data:
        className=i['class']
        classNum = className[-4:]
        if classNum == '2/-3':
            classNum = int(className[-9:-5])
        else:
            try:
                classNum = int(classNum)
            except:
                continue
        class_data_sort.append(classNum)
    # 获取班号排序下标
    sortIndex = list(np.argsort(class_data_sort))
    # # 清空数组
    # class_data_sort.clear()
    # # 将班级数据重新排序
    # for i in sortIndex:
    #     class_data_sort.append(class_data[i])
    # UI,全栈，大数据，人工智能，跨境电商列表
    UIDlist,UIlist,QZlist,BDlist,AIlist,EClist=[],[],[],[],[],[]
    for i in sortIndex:
        className = class_data[i]['class']
        if className[:4]=='MUIF':
            UIlist.append(class_data[i])
        elif className[:4] == 'MUID':
            UIDlist.append(class_data[i])
        elif className[:3]=='WUI':
            QZlist.append(class_data[i])
        elif className[:3]=='UBD':
            BDlist.append(class_data[i])
        elif className[:3]=='UAI':
            AIlist.append(class_data[i])
        else:
            EClist.append(class_data[i])
    resList = UIDlist+UIlist+QZlist+BDlist+AIlist+EClist
    return resList

# 获取当前周数据
def nowCourseData(reequest):
    nowWeek = getNowWeek()
    nowWeekData = UekCourseWeekData.objects.filter(week=nowWeek)
    if nowWeekData:
        return JsonResponse(json.loads(nowWeekData[0].data))
    else:
        return HttpResponse("0")
# 排下周课表
def predictCourser(request):
    # 更新 教师带课优先级
    writeTeacherPriorty()
    # 判断是否已经排过课
    is_weekData=UekCourseWeekData.objects.filter(week=getNextWeek())
    if is_weekData:
        return JsonResponse(json.loads(is_weekData[0].data))
    # 遍历老师，初始化老师下周状态
    setTeacherStatus()
    # 对所有班级进行排序
    classes = orderClass()
    # print("classes",classes)
    # classes =UekBasicClass.objects.filter(class_name='测试-班级').filter(class_cate=0)
    cours_list = {}  # 周课表
    week = getNextWeek()  # 获取下周周数
    # 设置周数
    cours_list['num'] = week
    # 获取下周日期列表 date_list为2019-10-28   date_list_changed为10月28日
    date_list, date_list_changed = get_weekday_list()
    # 设置修改的时间
    cours_list['date'] = date_list_changed
    # 列表中存放每个班的数据
    cours_list['data'] = []
    for c in classes:
        # 判断是否结训
        # if c.class_status != 0:
        #     continue
        # 判断是否开班
        if not isBegin(c):
            continue
        # 存放班级数据
        class_data = {}
        class_data['class'] = c.class_name
        class_data['room'] = UekBasicRoom.objects.filter(id=c.room_id)[0].room_name
        class_data['con'] = []
        class_data['teacher'] = []
        # 循环生产七天数据
        for d in range(7):
            # 阶段应上时长
            stage_time = UekBasicStage.objects.filter(id=c.stage_id)[0].stage_day
            # 当前带课老师姓名
            now_teacher = UekBasicTeacher.objects.filter(id=c.preach_teacher_id)[0].teacher_name
            # 当前阶段id
            now_stage_id = c.stage_id
            # 当前阶段对象
            now_stage_obj=UekBasicStage.objects.filter(id=now_stage_id)[0]
            # 当前阶段名称
            now_stage =now_stage_obj .stage_name
            is_None=UekCourseDayData.objects.filter(c_id=c.id).filter(s_id=now_stage_id)
            # 当前阶段已上课时(如果未上则为0)
            now_stage_time = is_None.order_by('-long_time')[0].long_time if is_None else 0
            # 已结束阶段
            before_endStage =None if not is_None else is_None.last().endstage
            # 判断班级上课周期，将无课天的数据设为空
            if c.class_cate == 0 and d == 5:
                class_data['con'].append('')
                class_data['con'].append('')
                class_data['teacher'].append('')
                class_data['teacher'].append('')
                break
            if c.class_cate == 1 and d == 6:
                class_data['con'].append('')
                class_data['teacher'].append('')
                break
            # 如果阶段未完成
            if now_stage_time < stage_time:
                # 获取教师周状态列表
                teacher_week_status=list(UekBasicTeacher.objects.filter(id=c.preach_teacher_id)[0].teacher_week_status)
                # 如果阶段老师当天状态不为空闲，则设置空值
                if teacher_week_status[d]=='1':
                    # 如果阶段未完成且当前阶段时长为0 说明是新开班级
                    if now_stage_time==0:
                        # 如果新开班级指定教师不空闲则重新指定一位教师
                        # 获取当前阶段
                        stageStartId = c.stage_id
                        stageStartObj = UekBasicStage.objects.filter(id=stageStartId)[0]
                        teacher_list = orderTeacher(stageStartObj)
                        # 循环对应教师
                        for t in teacher_list:
                            t_status = list(t.teacher_week_status)
                            # 该教师是否空闲
                            if t_status[d] == '1':
                                continue
                            class_data['con'].append(stageStartObj.stage_name)
                            class_data['teacher'].append(t.teacher_name)
                            # 修改布道师周状态
                            teacher_week_status_list1 = list(t.teacher_week_status)
                            teacher_week_status_list1[d] = '1'
                            t.teacher_week_status = "".join(teacher_week_status_list1)
                            t.save()
                            # 添加数据到日记录表中
                            if not UekCourseDayData.objects.filter(daytime=date_list[d]).filter(c_id=c.id):
                                day_data = UekCourseDayData(s_id=stageStartObj.id)
                                # 如果是从未上过的阶段则从0 开始,如果是接着前面的阶段则加1
                                # obj = UekCourseDayData.objects.filter(s_id=stageStartObj.id).filter(c_id=c.id)
                                # new_stage_time = 1 if not obj else obj.order_by('-long_time')[0].long_time + 1
                                # day_data.long_time = new_stage_time
                                day_data.long_time = 1
                                day_data.week = week
                                day_data.teacher = t.id
                                day_data.room = c.room_id
                                day_data.c_id = c.id
                                day_data.daytime = date_list[d]
                                # if not end_stage:
                                #     day_data.endstage = stageStartObj.id
                                # else:
                                #     new_endStage = end_stage.split('|')
                                #     new_endStage.append(str(i.id))
                                #     day_data.endstage = '|'.join(new_endStage)
                                day_data.save()
                                c.stage_id = stageStartObj.id
                                c.preach_teacher_id=t.id
                                c.save()
                            break
                        else:
                            print("%s开班阶段没有合适教师，请重新分配" % stageStartObj.stage_name)
                            class_data['con'].append('')
                            class_data['teacher'].append('')
                            continue
                        continue
                    else:
                        class_data['con'].append('')
                        class_data['teacher'].append('')
                        continue
                class_data['teacher'].append(now_teacher)
                # 将老师当天的状态调整为1
                now_teacher_obj=UekBasicTeacher.objects.filter(teacher_name=now_teacher)[0]
                teacher_week_status_list=list(now_teacher_obj.teacher_week_status)
                teacher_week_status_list[d]='1'
                now_teacher_obj.teacher_week_status="".join(teacher_week_status_list)
                now_teacher_obj.save()
                class_data['con'].append(now_stage)
                # 添加数据到日记录表中
                if not UekCourseDayData.objects.filter(daytime=date_list[d]).filter(c_id=c.id):
                    day_data = UekCourseDayData(s_id=now_stage_id)
                    day_data.long_time = now_stage_time+1
                    day_data.week = week
                    day_data.teacher = c.preach_teacher_id
                    day_data.room = c.room_id
                    day_data.c_id = c.id
                    day_data.daytime = date_list[d]
                    day_data.endstage=before_endStage
                    day_data.save()
            # 如果当前阶段已完成
            if now_stage_time >= stage_time:
                # 先找是否有未完成的前置阶段
                # 获取方向id
                did = now_stage_obj.dir_id
                # 获取阶段默认顺序
                orderNum = now_stage_obj.order_num
                # 获取已完成的阶段id组成的集合
                if not before_endStage:
                    before_endStage_id = set()
                else:
                    before_endStage_id = set(before_endStage.split("|"))
                # 获取当前阶段之前的阶段id
                before_Stage_id = set([i.id for i in UekBasicStage.objects.filter(dir_id=did).filter(stage_status=0).filter(order_num__lt=orderNum)])
                # 获取当前阶段之前还没上阶段id
                notend_stage_id = before_Stage_id-before_endStage_id
                # 如果存在未上阶段
                if len(notend_stage_id):
                    for i in notend_stage_id:
                        stageobj = UekBasicStage.objects.filter(id=i)[0]
                        if (c.class_name[:5]=='MUIF' and stageobj.stage_name=="产品经理与测试") or (c.class_name[:5]=='MUIF' and stageobj.stage_name=="运营") :
                            continue
                        if (c.class_name[:5]=='MUIDF' and stageobj.stage_name=="c4d") or (c.class_name[:5]=='MUIDF' and stageobj.stage_name=="商业插画") or (c.class_name[:5]=='MUIDF' and stageobj.stage_name=="可用性原则与测试") :
                            continue
                        stages2teacher(stageobj, d, class_data, date_list, week, c)
                    else:
                        stageList = bstageToAstage(now_stage_obj)
                        stages2course(stageList, d, class_data, date_list, week, c)
                else:
                    stageList = bstageToAstage(now_stage_obj)
                    # 如果没有后置阶段，有则进入,没有则结训并退出
                    if not len(stageList):
                        c.class_status = 1
                        c.save()
                        break
                    else:
                        stages2course(stageList,d,class_data,date_list,week,c)
                        # 将一个班一周的数据添加到总数据中
        cours_list["data"].append(class_data)
    # 将排课后的班级进行归类
    cours_list["data"] = classShow(cours_list["data"])
    # 组合校外班级
    outClass = UekCourseOutClasses.objects.filter().all()
    for c in outClass:
        if not isBegin(c):
            continue
        class_data = {}
        class_data['class'] = c.name
        class_data['room'] = c.croom
        class_data['con'] = ['' if i == '0' else i for i in c.data.split("|")]
        class_data['teacher'] = ['' if i =='0' else i for i in c.teacher.split("|")]
        cours_list['data'].append(class_data)
    cours_week_data=json.dumps(cours_list)
    week_data=UekCourseWeekData(data=cours_week_data)
    week_data.week=week
    week_data.save()
    return JsonResponse(cours_list)

# 排下周课表（方法）
def nextWeekCourser():
    # 判断是否已经排过课
    is_weekData=UekCourseWeekData.objects.filter(week=getNextWeek())
    if is_weekData:
        return json.loads(is_weekData[0].data)
    # 更新 教师带课优先级
    writeTeacherPriorty()
    # 遍历老师，初始化老师下周状态
    setTeacherStatus()
    # 对所有班级进行排序
    classes = orderClass()
    # print("classes",classes)
    # classes =UekBasicClass.objects.filter(class_name='测试-班级').filter(class_cate=0)
    cours_list = {}  # 周课表
    week = getNextWeek()  # 获取下周周数
    # 设置周数
    cours_list['num'] = week
    # 获取下周日期列表 date_list为2019-10-28   date_list_changed为10月28日
    date_list, date_list_changed = get_weekday_list()
    # 设置修改的时间
    cours_list['date'] = date_list_changed
    # 列表中存放每个班的数据
    cours_list['data'] = []
    for c in classes:
        # 判断是否结训
        # if c.class_status != 0:
        #     continue
        # 判断是否开班
        if not isBegin(c):
            continue
        # 存放班级数据
        class_data = {}
        class_data['class'] = c.class_name
        class_data['room'] = UekBasicRoom.objects.filter(id=c.room_id)[0].room_name
        class_data['con'] = []
        class_data['teacher'] = []
        # 循环生产七天数据
        for d in range(7):
            # 阶段应上时长
            stage_time = UekBasicStage.objects.filter(id=c.stage_id)[0].stage_day
            # 当前带课老师姓名
            now_teacher = UekBasicTeacher.objects.filter(id=c.preach_teacher_id)[0].teacher_name
            # 当前阶段id
            now_stage_id = c.stage_id
            # 当前阶段对象
            now_stage_obj=UekBasicStage.objects.filter(id=now_stage_id)[0]
            # 当前阶段名称
            now_stage =now_stage_obj .stage_name
            is_None=UekCourseDayData.objects.filter(c_id=c.id).filter(s_id=now_stage_id)
            # 当前阶段已上课时(如果未上则为0)
            now_stage_time = is_None.order_by('-long_time')[0].long_time if is_None else 0
            # 已结束阶段
            before_endStage =None if not is_None else is_None.last().endstage
            # 判断班级上课周期，将无课天的数据设为空
            if c.class_cate == 0 and d == 5:
                class_data['con'].append('')
                class_data['con'].append('')
                class_data['teacher'].append('')
                class_data['teacher'].append('')
                break
            if c.class_cate == 1 and d == 6:
                class_data['con'].append('')
                class_data['teacher'] .append('')
                break
            # 如果阶段未完成
            if now_stage_time < stage_time:
                # 获取教师周状态列表
                teacher_week_status=list(UekBasicTeacher.objects.filter(id=c.preach_teacher_id)[0].teacher_week_status)
                # 如果阶段老师当天状态不为空闲，则设置空值
                if teacher_week_status[d]=='1':
                    # 如果阶段未完成且当前阶段时长为0 说明是新开班级
                    if now_stage_time==0:
                        # 如果新开班级指定教师不空闲则重新指定一位教师
                        # 获取当前阶段
                        stageStartId = c.stage_id
                        stageStartObj = UekBasicStage.objects.filter(id=stageStartId)[0]
                        teacher_list = orderTeacher(stageStartObj)
                        # 循环对应教师
                        for t in teacher_list:
                            t_status = list(t.teacher_week_status)
                            # 该教师是否空闲
                            if t_status[d] == '1':
                                continue
                            class_data['con'].append(stageStartObj.stage_name)
                            class_data['teacher'].append(t.teacher_name)
                            # 修改布道师周状态
                            teacher_week_status_list1 = list(t.teacher_week_status)
                            teacher_week_status_list1[d] = '1'
                            t.teacher_week_status = "".join(teacher_week_status_list1)
                            t.save()
                            # 添加数据到日记录表中
                            if not UekCourseDayData.objects.filter(daytime=date_list[d]).filter(c_id=c.id):
                                day_data = UekCourseDayData(s_id=stageStartObj.id)
                                # 如果是从未上过的阶段则从0 开始,如果是接着前面的阶段则加1
                                # obj = UekCourseDayData.objects.filter(s_id=stageStartObj.id).filter(c_id=c.id)
                                # new_stage_time = 1 if not obj else obj.order_by('-long_time')[0].long_time + 1
                                # day_data.long_time = new_stage_time
                                day_data.long_time = 1
                                day_data.week = week
                                day_data.teacher = t.id
                                day_data.room = c.room_id
                                day_data.c_id = c.id
                                day_data.daytime = date_list[d]
                                # if not end_stage:
                                #     day_data.endstage = stageStartObj.id
                                # else:
                                #     new_endStage = end_stage.split('|')
                                #     new_endStage.append(str(i.id))
                                #     day_data.endstage = '|'.join(new_endStage)
                                day_data.save()
                                c.stage_id = stageStartObj.id
                                c.preach_teacher_id=t.id
                                c.save()
                            break
                        else:
                            print("%s开班阶段没有合适教师，请重新分配" % stageStartObj.stage_name)
                            class_data['con'].append('')
                            class_data['teacher'].append('')
                            continue
                        continue
                    else:
                        class_data['con'].append('')
                        class_data['teacher'].append('')
                        continue
                else:
                    class_data['teacher'].append(now_teacher)
                    # 将老师当天的状态调整为1
                    now_teacher_obj=UekBasicTeacher.objects.filter(teacher_name=now_teacher)[0]
                    teacher_week_status_list=list(now_teacher_obj.teacher_week_status)
                    teacher_week_status_list[d]='1'
                    now_teacher_obj.teacher_week_status="".join(teacher_week_status_list)
                    now_teacher_obj.save()
                    class_data['con'].append(now_stage)
                    # 添加数据到日记录表中
                    if not UekCourseDayData.objects.filter(daytime=date_list[d]).filter(c_id=c.id):
                        day_data = UekCourseDayData(s_id=now_stage_id)
                        day_data.long_time = now_stage_time+1
                        day_data.week = week
                        day_data.teacher = c.preach_teacher_id
                        day_data.room = c.room_id
                        day_data.c_id = c.id
                        day_data.daytime = date_list[d]
                        day_data.endstage=before_endStage
                        day_data.save()
            # 如果当前阶段已完成
            if now_stage_time >= stage_time:
                # 先找是否有未完成的前置阶段
                # 获取方向id
                did = now_stage_obj.dir_id
                # 获取阶段默认顺序
                orderNum = now_stage_obj.order_num
                # 获取已完成的阶段id组成的集合
                if not before_endStage:
                    before_endStage_id = set()
                else:
                    before_endStage_id = set(before_endStage.split("|"))
                # 获取当前阶段之前的阶段id
                before_Stage_id = set([i.id for i in UekBasicStage.objects.filter(dir_id=did).filter(stage_status=0).filter(order_num__lt=orderNum)])
                # 获取当前阶段之前还没上阶段id
                notend_stage_id = before_Stage_id-before_endStage_id
                # 如果存在未上阶段
                if len(notend_stage_id):
                    for i in notend_stage_id:
                        stageobj = UekBasicStage.objects.filter(id=i)[0]
                        if (c.class_name[:5]=='MUIF' and stageobj.stage_name=="产品经理与测试") or (c.class_name[:5]=='MUIF' and stageobj.stage_name=="运营") :
                            continue
                        if (c.class_name[:5]=='MUIDF' and stageobj.stage_name=="c4d") or (c.class_name[:5]=='MUIDF' and stageobj.stage_name=="商业插画") or (c.class_name[:5]=='MUIDF' and stageobj.stage_name=="可用性原则与测试") :
                            continue
                        stages2teacher(stageobj, d, class_data, date_list, week, c)
                    else:
                        stageList = bstageToAstage(now_stage_obj)
                        stages2course(stageList, d, class_data, date_list, week, c)
                else:
                    stageList = bstageToAstage(now_stage_obj)
                    # 如果没有后置阶段，有则进入,没有则结训并退出
                    if not len(stageList):
                        c.class_status = 1
                        c.save()
                        break
                    else:
                        stages2course(stageList,d,class_data,date_list,week,c)
                        # 将一个班一周的数据添加到总数据中
        cours_list["data"].append(class_data)
    # 将排课后的班级进行归类
    cours_list["data"] = classShow(cours_list["data"])
    # 组合校外班级
    outClass = UekCourseOutClasses.objects.filter().all()
    for c in outClass:
        nexWeek = getNextWeek()
        # 获取班级开班时间是第几周
        date = c.start_time.strftime("%Y%m%d")
        week = datetime.datetime.strptime(date, "%Y%m%d").strftime("%W")
        week = int(week)
        if week != nexWeek:
            continue
        class_data = {}
        class_data['class'] = c.name
        class_data['room'] = c.croom
        class_data['con'] = ['' if i == '0' else i for i in c.data.split("|")]
        class_data['teacher'] = ['' if i =='0' else i for i in c.teacher.split("|")]
        cours_list['data'].append(class_data)
    cours_week_data=json.dumps(cours_list)
    week_data=UekCourseWeekData(data=cours_week_data)
    week_data.week=getNextWeek()
    week_data.save()
    return cours_list

# 更新课表函数
def updataCourse(request,week):
    # 需要更新的周数
    week = int(week)
    if week == getNowWeek():
        nowWeek = getNowWeek()
        nowWeekData = UekCourseWeekData.objects.filter(week=nowWeek)[0].data
        nowWeekData = json.loads(nowWeekData)
        className = []
        for i in nowWeekData["data"]:
            className.append(i["class"])
        classes = UekBasicClass.objects.filter(class_cate=0) | UekBasicClass.objects.filter(class_cate=1)
        classes = classes.filter(class_status=0)
        for c1 in classes:
            # 判断本周是否开班
            if not isBegin(c1,to='now'):
                continue
            if c1.class_name in className:
                continue
            else:
                # 存放班级数据
                class_data = {}
                class_data['class'] = c1.class_name
                class_data['room'] = UekBasicRoom.objects.filter(id=c1.room_id)[0].room_name
                class_data['con'] = []
                class_data['teacher'] = []
                date_list,b = get_weekday_list(0)
                # 循环生产七天数据
                for d in range(7):
                    # 阶段应上时长
                    stage_time = UekBasicStage.objects.filter(id=c1.stage_id)[0].stage_day
                    # 当前带课老师姓名
                    now_teacher = UekBasicTeacher.objects.filter(id=c1.preach_teacher_id)[0].teacher_name
                    # 当前阶段id
                    now_stage_id = c1.stage_id
                    # 当前阶段对象
                    now_stage_obj = UekBasicStage.objects.filter(id=now_stage_id)[0]
                    # 当前阶段名称
                    now_stage = now_stage_obj.stage_name
                    is_None = UekCourseDayData.objects.filter(c_id=c1.id).filter(s_id=now_stage_id)
                    # 当前阶段已上课时(如果未上则为0)
                    now_stage_time = is_None.order_by('-long_time')[0].long_time if is_None else 0
                    # 已结束阶段
                    before_endStage = None if not is_None else is_None.last().endstage
                    # 判断班级上课周期，将无课天的数据设为空
                    if c1.class_cate == 0 and d == 5:
                        class_data['con'].append('')
                        class_data['con'].append('')
                        class_data['teacher'].append('')
                        class_data['teacher'].append('')
                        break
                    if c1.class_cate == 1 and d == 6:
                        class_data['con'].append('')
                        class_data['teacher'].append('')
                        break
                    # 如果阶段未完成
                    if now_stage_time < stage_time:
                        # 获取教师周状态列表
                        teacher_week_status = list(UekBasicTeacher.objects.filter(id=c1.preach_teacher_id)[0].teacher_week_status)
                        # 如果阶段老师当天状态不为空闲，则设置空值
                        if teacher_week_status[d] == '1':
                            # 如果阶段未完成且当前阶段时长为0 说明是新开班级
                            if now_stage_time == 0:
                                # 如果新开班级指定教师不空闲则重新指定一位教师
                                # 获取当前阶段
                                stageStartId = c1.stage_id
                                stageStartObj = UekBasicStage.objects.filter(id=stageStartId)[0]
                                teacher_list = orderTeacher(stageStartObj)
                                # 循环对应教师
                                for t in teacher_list:
                                    t_status = list(t.teacher_week_status)
                                    # 该教师是否空闲
                                    if t_status[d] == '1':
                                        continue
                                    class_data['con'].append(stageStartObj.stage_name)
                                    class_data['teacher'].append(t.teacher_name)
                                    # 修改布道师周状态
                                    teacher_week_status_list1 = list(t.teacher_week_status)
                                    teacher_week_status_list1[d] = '1'
                                    t.teacher_week_status = "".join(teacher_week_status_list1)
                                    t.save()
                                    # 添加数据到日记录表中
                                    if not UekCourseDayData.objects.filter(daytime=date_list[d]).filter(c_id=c1.id):
                                        day_data = UekCourseDayData(s_id=stageStartObj.id)
                                        # 如果是从未上过的阶段则从0 开始,如果是接着前面的阶段则加1
                                        # obj = UekCourseDayData.objects.filter(s_id=stageStartObj.id).filter(c_id=c.id)
                                        # new_stage_time = 1 if not obj else obj.order_by('-long_time')[0].long_time + 1
                                        # day_data.long_time = new_stage_time
                                        day_data.long_time = 1
                                        day_data.week = getNowWeek()
                                        day_data.teacher = t.id
                                        day_data.room = c1.room_id
                                        day_data.c_id = c1.id
                                        day_data.daytime = date_list[d]
                                        # if not end_stage:
                                        #     day_data.endstage = stageStartObj.id
                                        # else:
                                        #     new_endStage = end_stage.split('|')
                                        #     new_endStage.append(str(i.id))
                                        #     day_data.endstage = '|'.join(new_endStage)
                                        day_data.save()
                                        c1.stage_id = stageStartObj.id
                                        c1.preach_teacher_id = t.id
                                        c1.save()
                                    break
                                else:
                                    print("%s开班阶段没有合适教师，请重新分配" % stageStartObj.stage_name)
                                    class_data['con'].append('')
                                    class_data['teacher'].append('')
                                    continue
                                continue
                            else:
                                class_data['con'].append('')
                                class_data['teacher'].append('')
                                continue
                        else:
                            class_data['teacher'].append(now_teacher)
                            # 将老师当天的状态调整为1
                            now_teacher_obj = UekBasicTeacher.objects.filter(teacher_name=now_teacher)[0]
                            teacher_week_status_list = list(now_teacher_obj.teacher_week_status)
                            teacher_week_status_list[d] = '1'
                            now_teacher_obj.teacher_week_status = "".join(teacher_week_status_list)
                            now_teacher_obj.save()
                            class_data['con'].append(now_stage)
                            # 添加数据到日记录表中
                            if not UekCourseDayData.objects.filter(daytime=date_list[d]).filter(c_id=c1.id):
                                day_data = UekCourseDayData(s_id=now_stage_id)
                                day_data.long_time = now_stage_time + 1
                                day_data.week = getNowWeek()
                                day_data.teacher = c1.preach_teacher_id
                                day_data.room = c1.room_id
                                day_data.c_id = c1.id
                                day_data.daytime = date_list[d]
                                day_data.endstage = before_endStage
                                day_data.save()
                nowWeekData['data'].insert(0,class_data)

        # 将班级重新排序
        nowWeekData["data"] = classShow(nowWeekData["data"])
        # 更新新数据
        newData = json.dumps(nowWeekData)
        UekCourseWeekData.objects.filter(week=getNowWeek()).update(data=newData)

        # 检查校外课程更新
        outClasses = UekCourseOutClasses.objects.all()

        # 校外班级列表集合
        outClassesName = [i.name for i in outClasses]
        # 重新加载数据
        nowWeekData = UekCourseWeekData.objects.filter(week=nowWeek)[0].data
        nowWeekData = json.loads(nowWeekData)
        className = []
        for i in nowWeekData["data"]:
            className.append(i["class"])
        num = 0
        for i in range(len(className)):
            if className[i] in outClassesName:
                nowWeekData['data'].pop(i-num)
                num+=1

        # 重新更新本周校外班级
        outClass = UekCourseOutClasses.objects.filter().all()
        for c in outClass:
            # 获取班级开班时间是第几周
            date = c.start_time.strftime("%Y%m%d")
            week = datetime.datetime.strptime(date, "%Y%m%d").strftime("%W")
            week = int(week)
            if week != getNowWeek():
                continue
            class_data = {}
            class_data['class'] = c.name
            class_data['room'] = c.croom
            class_data['con'] = ['' if i == '0' else i for i in c.data.split("|")]
            class_data['teacher'] = ['' if i == '0' else i for i in c.teacher.split("|")]
            nowWeekData['data'].append(class_data)

        newData = json.dumps(nowWeekData)
        UekCourseWeekData.objects.filter(week=getNowWeek()).update(data=newData)
        return JsonResponse(nowWeekData)
    elif week == getNextWeek():
        nextWeek = getNextWeek()
        nextWeekData = UekCourseWeekData.objects.filter(week=nextWeek)[0].data
        nextWeekData = json.loads(nextWeekData)
        className = []
        # 获取已经排好班级的班级名称
        for i in nextWeekData["data"]:
            className.append(i["class"])
        classes = UekBasicClass.objects.filter(class_cate=0) | UekBasicClass.objects.filter(class_cate=1)
        classes = classes.filter(class_status=0)
        for c1 in classes:
            # 判断本周是否开班
            if not isBegin(c1):
                continue
            if c1.class_name in className:
                continue
            else:
                # 存放班级数据
                class_data = {}
                class_data['class'] = c1.class_name
                class_data['room'] = UekBasicRoom.objects.filter(id=c1.room_id)[0].room_name
                class_data['con'] = []
                class_data['teacher'] = []
                date_list, b = get_weekday_list(1)
                # 循环生产七天数据
                for d in range(7):
                    # 阶段应上时长
                    stage_time = UekBasicStage.objects.filter(id=c1.stage_id)[0].stage_day
                    # 当前带课老师姓名
                    now_teacher = UekBasicTeacher.objects.filter(id=c1.preach_teacher_id)[0].teacher_name
                    # 当前阶段id
                    now_stage_id = c1.stage_id
                    # 当前阶段对象
                    now_stage_obj = UekBasicStage.objects.filter(id=now_stage_id)[0]
                    # 当前阶段名称
                    now_stage = now_stage_obj.stage_name
                    is_None = UekCourseDayData.objects.filter(c_id=c1.id).filter(s_id=now_stage_id)
                    # 当前阶段已上课时(如果未上则为0)
                    now_stage_time = is_None.order_by('-long_time')[0].long_time if is_None else 0
                    # 已结束阶段
                    before_endStage = None if not is_None else is_None.last().endstage
                    # 判断班级上课周期，将无课天的数据设为空
                    if c1.class_cate == 0 and d == 5:
                        class_data['con'].append('')
                        class_data['con'].append('')
                        class_data['teacher'].append('')
                        class_data['teacher'].append('')
                        break
                    if c1.class_cate == 1 and d == 6:
                        class_data['con'].append('')
                        class_data['teacher'].append('')
                        break
                    # 如果阶段未完成
                    if now_stage_time < stage_time:
                        # 获取教师周状态列表
                        teacher_week_status = list(
                            UekBasicTeacher.objects.filter(id=c1.preach_teacher_id)[0].teacher_week_status)
                        # 如果阶段老师当天状态不为空闲，则设置空值
                        if teacher_week_status[d] == '1':
                            # 如果阶段未完成且当前阶段时长为0 说明是新开班级
                            if now_stage_time == 0:
                                # 如果新开班级指定教师不空闲则重新指定一位教师
                                # 获取当前阶段
                                stageStartId = c1.stage_id
                                stageStartObj = UekBasicStage.objects.filter(id=stageStartId)[0]
                                teacher_list = orderTeacher(stageStartObj)
                                # 循环对应教师
                                for t in teacher_list:
                                    t_status = list(t.teacher_week_status)
                                    # 该教师是否空闲
                                    if t_status[d] == '1':
                                        continue
                                    class_data['con'].append(stageStartObj.stage_name)
                                    class_data['teacher'].append(t.teacher_name)
                                    # 修改布道师周状态
                                    teacher_week_status_list1 = list(t.teacher_week_status)
                                    teacher_week_status_list1[d] = '1'
                                    t.teacher_week_status = "".join(teacher_week_status_list1)
                                    t.save()
                                    # 添加数据到日记录表中
                                    if not UekCourseDayData.objects.filter(daytime=date_list[d]).filter(c_id=c1.id):
                                        day_data = UekCourseDayData(s_id=stageStartObj.id)
                                        # 如果是从未上过的阶段则从0 开始,如果是接着前面的阶段则加1
                                        # obj = UekCourseDayData.objects.filter(s_id=stageStartObj.id).filter(c_id=c.id)
                                        # new_stage_time = 1 if not obj else obj.order_by('-long_time')[0].long_time + 1
                                        # day_data.long_time = new_stage_time
                                        day_data.long_time = 1
                                        day_data.week = getNowWeek()
                                        day_data.teacher = t.id
                                        day_data.room = c1.room_id
                                        day_data.c_id = c1.id
                                        day_data.daytime = date_list[d]
                                        # if not end_stage:
                                        #     day_data.endstage = stageStartObj.id
                                        # else:
                                        #     new_endStage = end_stage.split('|')
                                        #     new_endStage.append(str(i.id))
                                        #     day_data.endstage = '|'.join(new_endStage)
                                        day_data.save()
                                        c1.stage_id = stageStartObj.id
                                        c1.preach_teacher_id = t.id
                                        c1.save()
                                    break
                                else:
                                    print("%s开班阶段没有合适教师，请重新分配" % stageStartObj.stage_name)
                                    class_data['con'].append('')
                                    class_data['teacher'].append('')
                                    continue
                                continue
                            else:
                                class_data['con'].append('')
                                class_data['teacher'].append('')
                                continue
                        else:
                            class_data['teacher'].append(now_teacher)
                            # 将老师当天的状态调整为1
                            now_teacher_obj = UekBasicTeacher.objects.filter(teacher_name=now_teacher)[0]
                            teacher_week_status_list = list(now_teacher_obj.teacher_week_status)
                            teacher_week_status_list[d] = '1'
                            now_teacher_obj.teacher_week_status = "".join(teacher_week_status_list)
                            now_teacher_obj.save()
                            class_data['con'].append(now_stage)
                            # 添加数据到日记录表中
                            if not UekCourseDayData.objects.filter(daytime=date_list[d]).filter(c_id=c1.id):
                                day_data = UekCourseDayData(s_id=now_stage_id)
                                day_data.long_time = now_stage_time + 1
                                day_data.week = getNowWeek()
                                day_data.teacher = c1.preach_teacher_id
                                day_data.room = c1.room_id
                                day_data.c_id = c1.id
                                day_data.daytime = date_list[d]
                                day_data.endstage = before_endStage
                                day_data.save()
                nextWeekData['data'].insert(0, class_data)

        # 将班级重新排序
        nextWeekData["data"] = classShow(nextWeekData["data"])
        # 更新新数据
        newData = json.dumps(nextWeekData)
        UekCourseWeekData.objects.filter(week=getNextWeek()).update(data=newData)

        # 检查校外课程更新
        outClasses = UekCourseOutClasses.objects.all()

        # 校外班级列表集合
        outClassesName = [i.name for i in outClasses]
        # 重新加载数据
        nextWeekData = UekCourseWeekData.objects.filter(week=nextWeek)[0].data
        nextWeekData = json.loads(nextWeekData)
        className = []
        for i in nextWeekData["data"]:
            className.append(i["class"])
        num = 0
        for i in range(len(className)):
            if className[i] in outClassesName:
                nextWeekData['data'].pop(i - num)
                num += 1

        # 重新更新本周校外班级
        outClass = UekCourseOutClasses.objects.filter().all()
        for c in outClass:
            # 获取班级开班时间是第几周
            date = c.start_time.strftime("%Y%m%d")
            week = datetime.datetime.strptime(date, "%Y%m%d").strftime("%W")
            week = int(week)
            if week != getNextWeek():
                continue
            class_data = {}
            class_data['class'] = c.name
            class_data['room'] = c.croom
            class_data['con'] = ['' if i == '0' else i for i in c.data.split("|")]
            class_data['teacher'] = ['' if i == '0' else i for i in c.teacher.split("|")]
            nextWeekData['data'].append(class_data)

        newData = json.dumps(nextWeekData)
        UekCourseWeekData.objects.filter(week=getNextWeek()).update(data=newData)
        return JsonResponse(nextWeekData)
    else:
        week_data = UekCourseWeekData.objects.filter(week=week)
        if week_data:
            return JsonResponse(json.loads(week_data[0].data))
# 获取上周数据
def getbeforecourse(request,week):
    week=int(week)
    week_data=UekCourseWeekData.objects.filter(week=week)
    if week_data:
        return JsonResponse(json.loads(week_data[0].data))
    return HttpResponse("0")

# 获取下周数据
def getnextcourse(request,week):
    week=int(week)
    if week==getNextWeek():
        return JsonResponse(nextWeekCourser())
    week_data = UekCourseWeekData.objects.filter(week=week)
    if week_data:
        return JsonResponse(json.loads(week_data[0].data))
    return HttpResponse("0")

# 获取可上阶段
def getstage(request,classname):
    classname = "/".join(classname.split("@"))
    # 班级id
    class_id=UekBasicClass.objects.filter(class_name=classname)[0].id
    # 方向id
    d_id=UekBasicClass.objects.filter(class_name=classname)[0].dir_id
    # 已完成阶段
    end_stage=UekCourseDayData.objects.filter(c_id=class_id).order_by("-id")[0].endstage
    # 课程所有阶段对象
    stages=UekBasicStage.objects.filter(dir_id=d_id).all()
    # 用来放还没上的阶段
    useable_stage=[]
    # 如果未完成阶段为空，则返回所有阶段
    if not end_stage:
        useable_stage=[st.stage_name for st in stages]
        stage_list = {"stage_list": useable_stage}
        return JsonResponse(stage_list)
    # 如果有未完成阶段，则返回正在上的阶段和未上阶段
    stage_id=UekBasicClass.objects.filter(class_name=classname)[0].stage_id
    stage_name=UekBasicStage.objects.filter(id=stage_id)[0].stage_name
    useable_stage.append(stage_name)
    # 添加未完成阶段
    for i in stages:
        if i.id in end_stage.split("|"):
            continue
        useable_stage.append(i.stage_name)
    stage_list = {"stage_list": useable_stage}
    return JsonResponse(stage_list)

# 获取可带课教师
def getteacher(request,classname,stagename,sort):
    sort = int(sort)
    if stagename == '0':
        teacherlist = {"teacherlist": []}
        return JsonResponse(teacherlist)
    classname = '/'.join(classname.split('@'))
    teachers = UekBasicTeacher.objects.exclude(dir_id=0)
    teacherList = []
    for i in teachers:
        if i.teacher_name=="严武军":
            teacherList.append(i.teacher_name)
            continue
        if i.teacher_week_status[sort]=='0':
            teacherList.append(i.teacher_name)
            continue
    # # 将当前教师也加入到可选列表当中
    nowTeacherId = UekBasicClass.objects.filter(class_name=classname)[0].preach_teacher_id
    nowTeacher = UekBasicTeacher.objects.filter(id=nowTeacherId)[0]
    # # 将当前教师的状态置0
    # SList = list(nowTeacher.teacher_week_status)
    # SList[sort]='0'
    # nowTeacher.teacher_week_status=''.join(SList)
    # nowTeacher.save()
    teacherList.append(nowTeacher.teacher_name)
    teacherlist = {"teacherlist": teacherList}
    return JsonResponse(teacherlist)

# 修改课表老师状态
def changeTeacher(request,teacherNamePre,teacherNameNex,sort):
    sort = int(sort)
    # 将将之前前教师的状态置0
    preTeacher = UekBasicTeacher.objects.filter(teacher_name=teacherNamePre)[0]
    SList = list(preTeacher.teacher_week_status)
    SList[sort] = '0'
    preTeacher.teacher_week_status = ''.join(SList)
    preTeacher.save()

    # 修改改变后的教师状态
    nextTeacher = UekBasicTeacher.objects.filter(teacher_name=teacherNameNex)[0]
    statusList = list(nextTeacher.teacher_week_status)
    statusList[sort] = '1'
    nextTeacher.teacher_week_status = ''.join(statusList)
    nextTeacher.save()
    return HttpResponse(123)

def savedata(request):
    # 修改后的数据
    after_data = request.POST.get('data')
    after_data = json.loads(after_data)
    # 修改后的班级数据
    after_week_data = after_data["data"]
    # 获取当前周数
    nowWeek = getNowWeek()
    # 获取周数
    befor_week = after_data["num"]
    # 获取时间列表
    # if befor_week == 53:
    #     befor_week =0
    date_list, date_list_changed = get_weekday_list(befor_week-nowWeek)

    # 获取下周日期列表 date_list为2019-10-28   date_list_changed为10月28日
    # date_list, date_list_changed = get_weekday_list()
    befor_datetime = date_list
    # 未修改的数据对象
    befor_data=json.loads(UekCourseWeekData.objects.filter(week=befor_week).first().data)
    record = UekCourseDayData.objects.filter(week=befor_week)
    # 如果数据没有变化，则返回ok
    if after_data==befor_data and record:
        return HttpResponse("ok")
    # 删除原来数据
    UekCourseDayData.objects.filter(week=befor_week).delete()
    # 如果保存的是下周课表，初始化教师状态
    # 此处应该是除了下周课表不能进行保存，为了测试开放
    if befor_week == getNextWeek():
        setTeacherStatus()
    # 添加新数据
    for j in after_week_data:
        for e in range(7):
            if j["teacher"][e]=='' or j["con"][e]=='':
                continue
            # 添加周数
            class_record = UekCourseDayData(week=befor_week)
            # 添加上课时间
            class_record.daytime=befor_datetime[e]
            # 如果是校外班级，则跳过
            class_obj=UekBasicClass.objects.filter(class_name=j["class"])
            if not class_obj:
                break
            # 添加班级id
            class_id=UekBasicClass.objects.filter(class_name=j["class"])[0].id
            class_record.c_id = class_id
            # 添加班级教室id
            roomid=UekBasicRoom.objects.filter(room_name=j["room"]).first().id
            class_record.room = roomid
            # 添加教师id
            teacherObj = UekBasicTeacher.objects.filter(teacher_name=j["teacher"][e]).first()
            # 需要考虑有阶段没教师
            teacherid = teacherObj.id
            class_record.teacher = teacherid
            # 修改布道师周状态
            if befor_week == getNextWeek():
                teacher_week_status_list1 = list(teacherObj.teacher_week_status)
                teacher_week_status_list1[e] = '1'
                teacherObj.teacher_week_status = "".join(teacher_week_status_list1)
                teacherObj.save()

            # 添加阶段id
            stageid = UekBasicStage.objects.filter(stage_name=j["con"][e]).first().id
            class_record.s_id = stageid
            # 添加完成阶段
            daydata_obj=UekCourseDayData.objects.filter(c_id=class_id)
            # 如果没有历史数据则把完成阶段设置为空
            if not daydata_obj:
                class_record.endstage=None
                class_record.long_time=1
                class_record.save()
            else:
                # 完成阶段
                endstage = daydata_obj.order_by("id").last().endstage
                # 上次上课阶段id
                before_stageid=daydata_obj.order_by("id").last().s_id
                #上次上课阶段时长
                before_longtime=daydata_obj.order_by("id").last().long_time
                # 如果阶段相同，则只加上课天数
                if before_stageid==stageid:
                    class_record.endstage=endstage
                    class_record.long_time=before_longtime+1
                    class_record.save()
                else:
                    # 如果阶段不同则判断上次阶段是否完成，完成则加入完成阶段
                    stage_days=UekBasicStage.objects.filter(id=before_stageid)[0].stage_day
                    # 如果阶段未完成
                    if stage_days>before_longtime:
                        class_record.endstage=endstage
                    else:
                        # 如果阶段完成，但是完成阶段为空，则直接添加
                        if not endstage:
                            class_record.endstage = str(before_stageid)
                        else:
                            stage_list=endstage.split('|')
                            # 如果阶段完成，判断完成阶段中是否已经存在，不存在则添加
                            if before_stageid in stage_list:
                                class_record.endstage=endstage
                            else:
                                stage_list.append(str(before_stageid))
                                class_record.endstage="|".join(stage_list)
                    class_record.long_time = 1
                    class_record.save()
            if befor_week == getNextWeek():
                UekBasicClass.objects.filter(id=class_id).update(stage_id=stageid)
                UekBasicClass.objects.filter(id=class_id).update(preach_teacher_id=teacherid)
            # 更新周课表数据
            UekCourseWeekData.objects.filter(week=befor_week).update(data=json.dumps(after_data))
    return HttpResponse("ok")



def index(request):
    # 班级排序测试
    # classes = UekBasicClass.objects.all()
    # print(classes)
    # print(orderClass())
    # 教师带课优先级初始化测试
    # stages = UekBasicStage.objects.all()
    # setTeacherPriority()
    # 教师带课优先级录入测试
    # writeTeacherPriorty()
    # 教师下周状态初始化测试
    # setTeacherStatus()
    # 后置阶段优先级测试
    # stage = UekBasicStage.objects.filter(id__lt=5)
    # print(stage)
    # 排课测试
    setTeacherPriority()
    return render(request,'uekClasses/index.html')
