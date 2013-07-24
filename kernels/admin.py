from django.contrib import admin
from kernels.models import Kernel


class KernelAdmin(admin.ModelAdmin):
    pass
admin.site.register(Kernel, KernelAdmin)
