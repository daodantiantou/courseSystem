# Generated by Django 2.2.4 on 2019-12-12 01:21

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='UekAdminRole',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role_name', models.CharField(blank=True, max_length=255, null=True)),
                ('description', models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                'verbose_name_plural': '角色表',
                'db_table': 'uek_admin_role',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='UekAdminUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=255, unique=True)),
                ('password', models.CharField(max_length=255)),
                ('role_id', models.IntegerField()),
                ('status', models.IntegerField(help_text='0 正常 1禁用 ', verbose_name='状态')),
                ('token', models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                'verbose_name_plural': '用户表',
                'db_table': 'uek_admin_user',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='UekBasicClass',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('class_name', models.CharField(max_length=255, verbose_name='班级名')),
                ('class_cate', models.IntegerField(blank=True, help_text='0 五天全日制 1 六天全日制 2预科班 3 周末班', null=True, verbose_name='班级分类')),
                ('master_teacher_id', models.IntegerField(verbose_name='督导师id')),
                ('preach_teacher_id', models.IntegerField(blank=True, null=True, verbose_name='布道师id')),
                ('employ_teacher_id', models.IntegerField(blank=True, null=True, verbose_name='就业教师id')),
                ('dir_id', models.IntegerField(verbose_name='所属方向id')),
                ('stage_id', models.IntegerField(blank=True, null=True, verbose_name='目前阶段id')),
                ('start_time', models.DateTimeField(verbose_name='开班时间')),
                ('pre_end_time', models.DateTimeField(blank=True, null=True, verbose_name='预计结训时间')),
                ('real_end_time', models.DateTimeField(blank=True, null=True, verbose_name='实际结训时间')),
                ('room_id', models.IntegerField(verbose_name='实训室id')),
                ('class_status', models.IntegerField(blank=True, help_text='0 正常 1结训 2合班保留', null=True, verbose_name='班级状态')),
                ('description', models.CharField(blank=True, max_length=255, null=True, verbose_name='备注')),
            ],
            options={
                'verbose_name_plural': '班级表',
                'db_table': 'uek_basic_class',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='UekBasicDept',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pid', models.IntegerField(help_text='最顶级为0', verbose_name='父部门id')),
                ('dept_name', models.CharField(max_length=255, verbose_name='部门名称')),
                ('dept_status', models.IntegerField(blank=True, help_text='0启用 1禁用', null=True, verbose_name='部门状态')),
                ('description', models.CharField(blank=True, max_length=255, null=True, verbose_name='部门描述')),
            ],
            options={
                'verbose_name_plural': '部门表',
                'db_table': 'uek_basic_dept',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='UekBasicDirection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dir_num', models.CharField(blank=True, max_length=255, null=True, verbose_name='方向编号')),
                ('dir_name', models.CharField(max_length=255, verbose_name='方向名')),
                ('price', models.IntegerField(verbose_name='方向价格')),
                ('dir_day', models.IntegerField(verbose_name='实训天数')),
                ('dir_status', models.IntegerField(blank=True, help_text='0正常 1禁用', null=True, verbose_name='方向状态')),
                ('description', models.CharField(blank=True, max_length=255, null=True, verbose_name='描述')),
            ],
            options={
                'verbose_name_plural': '方向表',
                'db_table': 'uek_basic_direction',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='UekBasicRoom',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('room_name', models.CharField(max_length=255, verbose_name='实训室名')),
                ('room_count', models.IntegerField(blank=True, null=True, verbose_name='实训室容量')),
                ('room_status', models.IntegerField(blank=True, help_text='0教师空闲 1教室不空闲 2教室禁用', null=True, verbose_name='实训室状态')),
                ('description', models.CharField(blank=True, max_length=255, null=True, verbose_name='描述')),
            ],
            options={
                'verbose_name_plural': '教室表',
                'db_table': 'uek_basic_room',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='UekBasicStudent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('student_name', models.CharField(max_length=255, verbose_name='学生姓名')),
                ('class_id', models.IntegerField(verbose_name='班级id')),
                ('dept_id', models.IntegerField(verbose_name='所属部门')),
                ('dir_id', models.IntegerField(verbose_name='方向id')),
                ('add_time', models.DateTimeField(verbose_name='加入班级时间')),
                ('student_status', models.IntegerField(help_text='0正常 1 请假 2 休学 3 退学 4结训 5提前结训 6劝退', verbose_name='学生状态')),
                ('sex', models.IntegerField(blank=True, null=True, verbose_name='性别')),
                ('age', models.IntegerField(blank=True, null=True, verbose_name='年龄')),
                ('birthday', models.CharField(blank=True, max_length=255, null=True, verbose_name='出生年月日')),
                ('student_email', models.CharField(blank=True, max_length=255, null=True, verbose_name='邮箱')),
                ('student_school', models.CharField(blank=True, max_length=255, null=True, verbose_name='院校')),
                ('student_department', models.CharField(blank=True, max_length=255, null=True, verbose_name='院系')),
                ('student_major', models.CharField(blank=True, max_length=255, null=True, verbose_name='专业')),
                ('student_school_class', models.CharField(blank=True, max_length=255, null=True, verbose_name='在校班级')),
                ('student_education', models.CharField(blank=True, max_length=255, null=True, verbose_name='学历')),
                ('phone', models.CharField(max_length=255, verbose_name='手机号')),
                ('qq_number', models.CharField(blank=True, max_length=255, null=True, verbose_name='qq号')),
                ('wechart_number', models.CharField(blank=True, max_length=255, null=True, verbose_name='微信号')),
                ('idcard', models.CharField(blank=True, max_length=255, null=True, verbose_name='身份证号')),
                ('emergency_name', models.CharField(blank=True, max_length=255, null=True, verbose_name='紧急联系人姓名')),
                ('emergency_phone', models.CharField(blank=True, max_length=255, null=True, verbose_name='紧急联系人电话')),
                ('family_address', models.CharField(blank=True, max_length=255, null=True, verbose_name='家庭住址')),
                ('now_address', models.CharField(blank=True, max_length=255, null=True, verbose_name='现在住址')),
                ('guarder', models.CharField(blank=True, max_length=255, null=True, verbose_name='监护人')),
                ('guarder_phone', models.CharField(blank=True, max_length=255, null=True, verbose_name='监护人电话')),
                ('description', models.CharField(blank=True, max_length=255, null=True, verbose_name='备注')),
            ],
            options={
                'verbose_name_plural': '学生表',
                'db_table': 'uek_basic_student',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='UekInteriorLeave',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('teacher_id', models.IntegerField(verbose_name='教师id')),
                ('teacher_dep_id', models.IntegerField(verbose_name='教师部门id')),
                ('leave_reason', models.CharField(max_length=255, verbose_name='请假原因')),
                ('start_time', models.DateTimeField(blank=True, null=True, verbose_name='请假开始时间')),
                ('end_time', models.DateTimeField(blank=True, null=True, verbose_name='请假结束时间')),
                ('status', models.IntegerField(blank=True, help_text='0未审核 1组长审核通过 2管理员审核通过 3审核失败', null=True, verbose_name='审核状态')),
            ],
            options={
                'db_table': 'uek_interior_leave',
                'managed': False,
            },
        ),
    ]
