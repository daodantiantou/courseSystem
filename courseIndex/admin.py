from django.contrib import admin

# Register your models here.
from  .models import UekBasicStage,UekBasicTeacher,UekCourseStagePriority,UekCourseDayData,UekCourseOutClasses,UekCourseWeekData

from courseRelative.models import UekBasicDept,UekBasicStudent,UekInteriorLeave,UekAdminRole,UekAdminUser,UekBasicClass,UekBasicDirection,UekBasicRoom

# Register your models here.

admin.site.site_title = "MyDjango后台管理"
admin.site.site_header = "优逸客排课系统"


@admin.register(UekBasicDirection)
class UekBasicDirectionAdmin(admin.ModelAdmin):
    exclude = []

@admin.register(UekAdminRole)
class UekAdminRoleAdmin(admin.ModelAdmin):
    exclude = []
@admin.register(UekAdminUser)
class UekAdminUserAdmin(admin.ModelAdmin):
    exclude = []

@admin.register(UekInteriorLeave)
class UekInteriorLeaveAdmin(admin.ModelAdmin):
    exclude = []

@admin.register(UekBasicStudent)
class UekBasicStudentAdmin(admin.ModelAdmin):
    exclude = []

@admin.register(UekBasicDept)
class UekBasicDeptAdmin(admin.ModelAdmin):
    exclude = []

@admin.register(UekBasicClass)
class UekBasicClassAdmin(admin.ModelAdmin):
    exclude = []

@admin.register(UekBasicTeacher)
class UekBasicTeacherAdmin(admin.ModelAdmin):
    exclude = []

@admin.register(UekBasicStage)
class UekBasicStageAdmin(admin.ModelAdmin):
    exclude = []

@admin.register(UekBasicRoom)
class UekBasicRoomAdmin(admin.ModelAdmin):
    exclude = []


@admin.register(UekCourseOutClasses)
class UekCourseOutClassesAdmin(admin.ModelAdmin):
    exclude = []

@admin.register(UekCourseWeekData)
class UekCourseWeekDataAdmin(admin.ModelAdmin):
    exclude = []

@admin.register(UekCourseDayData)
class UekCourseDayDataAdmin(admin.ModelAdmin):
    exclude = []

@admin.register(UekCourseStagePriority)
class UekCourseStagePriorityAdmin(admin.ModelAdmin):
    exclude = []

