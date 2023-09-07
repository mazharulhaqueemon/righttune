from django.contrib import admin

from livestream.models import ActiveCall, ActiveCalls, StreamComment,LiveStreaming

admin.site.register(ActiveCall)
admin.site.register(ActiveCalls)
admin.site.register(StreamComment)
admin.site.register(LiveStreaming)
# Register your models here.
