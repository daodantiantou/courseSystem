from django.db import models

# Create your models here.

class UekBasicClass(models.Model):
    class_name = models.CharField(max_length=255,verbose_name='班级名')
    class_cate = models.IntegerField(blank=True, null=True,verbose_name='班级分类',help_text='0 五天全日制 1 六天全日制 2预科班 3 周末班')
    master_teacher_id = models.IntegerField(verbose_name='督导师id')
    preach_teacher_id = models.IntegerField(blank=True, null=True,verbose_name='布道师id')
    employ_teacher_id = models.IntegerField(blank=True, null=True,verbose_name='就业教师id')
    dir_id = models.IntegerField(verbose_name='所属方向id')
    stage_id = models.IntegerField(blank=True, null=True,verbose_name='目前阶段id')
    start_time = models.DateTimeField(verbose_name='开班时间')
    pre_end_time = models.DateTimeField(blank=True, null=True,verbose_name='预计结训时间')
    real_end_time = models.DateTimeField(blank=True, null=True,verbose_name='实际结训时间')
    room_id = models.IntegerField(verbose_name='实训室id')
    class_status = models.IntegerField(blank=True, null=True,verbose_name='班级状态',help_text='0 正常 1结训 2合班保留')
    description = models.CharField(max_length=255, blank=True, null=True,verbose_name='备注')
    def __str__(self):
        return self.class_name
    class Meta:
        verbose_name_plural='班级表'
        managed = False
        db_table = 'uek_basic_class'


class UekBasicDirection(models.Model):
    dir_num = models.CharField(max_length=255, blank=True, null=True,verbose_name='方向编号')
    dir_name = models.CharField(max_length=255,verbose_name='方向名')
    price = models.IntegerField(verbose_name='方向价格')
    dir_day = models.IntegerField(verbose_name='实训天数')
    dir_status = models.IntegerField(blank=True, null=True,verbose_name='方向状态',help_text='0正常 1禁用')
    description = models.CharField(max_length=255, blank=True, null=True,verbose_name='描述')

    def __str__(self):
        return self.dir_name
    class Meta:
        verbose_name_plural='方向表'
        managed = False
        db_table = 'uek_basic_direction'


class UekBasicRoom(models.Model):
    room_name = models.CharField(max_length=255,verbose_name='实训室名')
    room_count = models.IntegerField(blank=True, null=True,verbose_name='实训室容量')
    room_status = models.IntegerField(blank=True, null=True,verbose_name='实训室状态',help_text='0教师空闲 1教室不空闲 2教室禁用')
    description = models.CharField(max_length=255, blank=True, null=True,verbose_name='描述')
    def __str__(self):
        return self.room_name
    class Meta:
        verbose_name_plural='教室表'
        managed = False
        db_table = 'uek_basic_room'

class UekBasicDept(models.Model):
    pid = models.IntegerField(verbose_name='父部门id',help_text='最顶级为0')
    dept_name = models.CharField(max_length=255,verbose_name='部门名称')
    dept_status = models.IntegerField(blank=True, null=True,verbose_name='部门状态',help_text='0启用 1禁用')
    description = models.CharField(max_length=255, blank=True, null=True,verbose_name='部门描述')
    def __str__(self):
        return self.dept_name
    class Meta:
        managed = False
        verbose_name_plural='部门表'
        db_table='uek_basic_dept'

class UekBasicStudent(models.Model):
    student_name = models.CharField(max_length=255,verbose_name='学生姓名')
    class_id = models.IntegerField(verbose_name='班级id')
    dept_id = models.IntegerField(verbose_name='所属部门')
    dir_id = models.IntegerField(verbose_name='方向id')
    add_time = models.DateTimeField(verbose_name='加入班级时间')
    student_status = models.IntegerField(verbose_name='学生状态',help_text='0正常 1 请假 2 休学 3 退学 4结训 5提前结训 6劝退')
    sex = models.IntegerField(blank=True, null=True,verbose_name='性别')
    age = models.IntegerField(blank=True, null=True,verbose_name='年龄')
    birthday = models.CharField(max_length=255, blank=True, null=True,verbose_name='出生年月日')
    student_email = models.CharField(max_length=255, blank=True, null=True,verbose_name='邮箱')
    student_school = models.CharField(max_length=255, blank=True, null=True,verbose_name='院校')
    student_department = models.CharField(max_length=255, blank=True, null=True,verbose_name='院系')
    student_major = models.CharField(max_length=255, blank=True, null=True,verbose_name='专业')
    student_school_class = models.CharField(max_length=255, blank=True, null=True,verbose_name='在校班级')
    student_education = models.CharField(max_length=255, blank=True, null=True,verbose_name='学历')
    phone = models.CharField(max_length=255,verbose_name='手机号')
    qq_number = models.CharField(max_length=255, blank=True, null=True,verbose_name='qq号')
    wechart_number = models.CharField(max_length=255, blank=True, null=True,verbose_name='微信号')
    idcard = models.CharField(max_length=255, blank=True, null=True,verbose_name='身份证号')
    emergency_name = models.CharField(max_length=255, blank=True, null=True,verbose_name='紧急联系人姓名')
    emergency_phone = models.CharField(max_length=255, blank=True, null=True,verbose_name='紧急联系人电话')
    family_address = models.CharField(max_length=255, blank=True, null=True,verbose_name='家庭住址')
    now_address = models.CharField(max_length=255, blank=True, null=True,verbose_name='现在住址')
    guarder = models.CharField(max_length=255, blank=True, null=True,verbose_name='监护人')
    guarder_phone = models.CharField(max_length=255, blank=True, null=True,verbose_name='监护人电话')
    description = models.CharField(max_length=255, blank=True, null=True,verbose_name='备注')
    def __str__(self):
        return self.student_name
    class Meta:
        verbose_name_plural='学生表'
        managed = False
        db_table = 'uek_basic_student'

class UekInteriorLeave(models.Model):
    teacher_id = models.IntegerField(verbose_name='教师id')
    teacher_dep_id = models.IntegerField(verbose_name='教师部门id')
    leave_reason = models.CharField(max_length=255,verbose_name='请假原因')
    start_time = models.DateTimeField(blank=True, null=True,verbose_name='请假开始时间')
    end_time = models.DateTimeField(blank=True, null=True,verbose_name='请假结束时间')
    status = models.IntegerField(blank=True, null=True,verbose_name='审核状态',help_text='0未审核 1组长审核通过 2管理员审核通过 3审核失败')

    class Meta:
        managed = False
        db_table = 'uek_interior_leave'
        verbose_name_plural = '请假表'


class UekAdminRole(models.Model):
    role_name = models.CharField(max_length=255, blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        verbose_name_plural='角色表'
        managed = False
        db_table = 'uek_admin_role'

class UekAdminUser(models.Model):
    username = models.CharField(unique=True, max_length=255)
    password = models.CharField(max_length=255)
    role_id = models.IntegerField()
    status = models.IntegerField(verbose_name='状态',help_text='0 正常 1禁用 ')
    token = models.CharField(max_length=255, blank=True, null=True)
    def __str__(self):
        return self.username
    class Meta:
        verbose_name_plural='用户表'
        managed = False
        db_table = 'uek_admin_user'






