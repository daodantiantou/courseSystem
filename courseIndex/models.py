from django.db import models
from django.utils import timezone
# Create your models here.

class UekBasicStage(models.Model):
    stage_num = models.CharField(max_length=255, blank=True, null=True,verbose_name='阶段编号')
    stage_name = models.CharField(max_length=255,verbose_name='阶段名称')
    dir_id = models.IntegerField(verbose_name='所属方向id')
    stage_day = models.IntegerField(blank=True, null=True,verbose_name='阶段天数')
    order_num = models.IntegerField(blank=True, null=True,verbose_name='阶段顺序')
    stage_status = models.IntegerField(blank=True, null=True,verbose_name='阶段状态',help_text='0正常 1禁用')
    description = models.CharField(max_length=255, blank=True, null=True,verbose_name='描述')
    def __str__(self):
        return self.stage_name
    class Meta:
        verbose_name_plural='阶段表'
        managed = False
        db_table = 'uek_basic_stage'

class UekBasicTeacher(models.Model):
    teacher_name = models.CharField(max_length=255,verbose_name='教师姓名')
    teacher_num = models.CharField(max_length=255, blank=True, null=True,verbose_name='教师工号')
    dept_id = models.IntegerField(verbose_name='所属部门id')
    dir_id = models.IntegerField(blank=True, null=True,verbose_name='方向id')
    teacher_level = models.IntegerField(verbose_name='教师等级')
    teacher_priority = models.CharField(max_length=255, blank=True, null=True,verbose_name='带课优先级')
    teacher_status = models.IntegerField(blank=True, null=True,verbose_name='教师状态',help_text='0 正常 1 请假')
    teacher_week_status = models.CharField(max_length=255,verbose_name='教师下周临时状态',default='0000000')
    sex = models.IntegerField(verbose_name='性别',help_text='1 男 2 女')
    age = models.IntegerField(blank=True, null=True,verbose_name='年龄')
    phone = models.CharField(max_length=255,verbose_name='手机号')
    birthday = models.CharField(max_length=255, blank=True, null=True,verbose_name='出生年月')
    email = models.CharField(max_length=255, blank=True, null=True,verbose_name='教师邮箱')
    school = models.CharField(max_length=255, blank=True, null=True,verbose_name='毕业院校')
    department = models.CharField(max_length=255, blank=True, null=True,verbose_name='毕业院校院系')
    major = models.CharField(max_length=255, blank=True, null=True,verbose_name='毕业院校专业')
    education = models.CharField(max_length=255, blank=True, null=True,verbose_name='学历')
    def __str__(self):
        return self.teacher_name
    class Meta:
        verbose_name_plural='老师表'
        managed = False
        db_table = 'uek_basic_teacher'

# 班级信息记录表
class UekCourseDayData(models.Model):
    c_id=models.IntegerField(
        verbose_name='班级ID',
        blank=True,
        null=True
    )
    s_id = models.IntegerField(
        verbose_name='阶段',
        blank=True,
        null=True
    )
    long_time = models.IntegerField(
        verbose_name='阶段已上课时',
        default=0
    )
    week = models.IntegerField(
        verbose_name='第几周',
        default=0
    )
    teacher=models.IntegerField(
        verbose_name='教师id',
        blank=True,
        null=True
    )
    room=models.IntegerField(
        verbose_name='教室',
        blank=True,
        null=True
    )
    daytime=models.CharField(
        verbose_name='上课时间',
        max_length=50,
        blank=True,
        null=True
    )
    endstage=models.CharField(
        verbose_name='完成阶段',
        max_length=50,
        blank=True,
        null=True
    )
    def __str__(self):
        return str(self.week)
    class Meta:
        managed = False
        verbose_name_plural='班级每周信息'
        db_table='uek_course_daydata'

class UekCourseWeekData(models.Model):
    data = models.CharField(max_length=5000,verbose_name="课表数据")
    week = models.IntegerField(verbose_name="周数",default=0)
    def __str__(self):
        return self.week
    class Meta:
        verbose_name_plural='周课表数据'
        db_table='uek_course_weekdata'

class UekCourseStagePriority(models.Model):
    pre_course = models.ForeignKey(to=UekBasicStage,on_delete=models.CASCADE,blank=True, null=True, verbose_name="前导阶段",related_name='pre_course')
    next_course = models.ForeignKey(to=UekBasicStage,on_delete=models.CASCADE,blank=True, null=True, verbose_name="后续阶段",related_name='next_course')
    priority = models.IntegerField(default=100, verbose_name="优先级", choices=((100, 100), (90, 90), (80, 80), (70, 70), (60, 60), (50, 50), (40, 40), (30, 30), (20, 20),(10, 10), (0, 0)))
    class Meta:
        verbose_name_plural='阶段优先级'
        db_table='uek_course_stagepriority'

class UekCourseTSPriorty(models.Model):
    teacher=models.ForeignKey(to=UekBasicTeacher,on_delete=models.CASCADE,blank=True,null=True,verbose_name='布道师')
    stage=models.ForeignKey(to=UekBasicStage,on_delete=models.CASCADE,blank=True,null=True,verbose_name='阶段')
    priorty=models.IntegerField(verbose_name='优先级',blank=True,null=True)

    def __str__(self):
        return self.teacher.teacher_name
    class Meta:
        db_table='uek_course_tspriorty'

import time
# 获取下周周数
def getWeek():
    week=time.strftime("%W")
    week=int(week)+1
    return week
# 校外班级
class UekCourseOutClasses(models.Model):
    name=models.CharField(
        max_length=20,
        verbose_name='班名'
    )
    croom=models.CharField(
        max_length=20,
        verbose_name='上课地点'
    )
    data = models.CharField(
        max_length=200,
        verbose_name='课程数据',
        help_text='0代表该天无课',
        default='0|0|0|0|0|0|0'
    )
    teacher = models.CharField(
        verbose_name='上课老师',
        max_length=200,
        blank=True,
        help_text='0代表该天无老师',
        default='0|0|0|0|0|0|0'
    )
    start_time = models.DateTimeField('开班时间', default=timezone.now)
    def __str__(self):
        return self.name
    class Meta:
        verbose_name_plural='校外班级表'
        db_table='uek_course_outclasses'

