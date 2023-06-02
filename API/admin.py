from django.contrib import admin
from API.models import Results, Messages, Token, Users, Codes, UserInfo, Tariffs, FBids, Bill, Diary


@admin.register(Results)
class ResultsAdmin(admin.ModelAdmin):
    search_fields = ["user"]
    list_display = ["user", "percent", "create_time"]
    readonly_fields = ("create_time", "update_time")
    date_hierarchy = "create_time"


@admin.register(Token)
class TokenAdmin(admin.ModelAdmin):
    search_fields = ["user"]
    list_display = ["user", "token", "create_time"]
    readonly_fields = ("create_time", "update_time")
    date_hierarchy = "create_time"


@admin.register(Users)
class UsersAdmin(admin.ModelAdmin):
    search_fields = ["number", "role"]
    list_display = ["number", "role", "subscription_end", "create_time"]
    readonly_fields = ("create_time", "update_time")
    date_hierarchy = "create_time"


@admin.register(UserInfo)
class UserInfoAdmin(admin.ModelAdmin):
    search_fields = ["user"]
    list_display = ["user", "weight", "age"]
    readonly_fields = ("create_time", "update_time")
    date_hierarchy = "create_time"


@admin.register(Codes)
class CodesAdmin(admin.ModelAdmin):
    search_fields = ["phone"]
    list_display = ["phone", "code", "create_time"]
    readonly_fields = ("create_time", "update_time")
    date_hierarchy = "create_time"


@admin.register(Tariffs)
class TariffsAdmin(admin.ModelAdmin):
    search_fields = ["days", "title"]
    list_display = ["days", "title", "price", "currency", "create_time"]
    readonly_fields = ("create_time", "update_time")
    date_hierarchy = "create_time"


@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    search_fields = ["user", "product", "amount"]
    list_display = ["user", "product", "amount", "status", "create_time"]
    readonly_fields = ("create_time", "update_time")
    date_hierarchy = "create_time"


@admin.register(Messages)
class MessagesAdmin(admin.ModelAdmin):
    search_fields = ["user"]
    list_display = ["user", "text", "private", "create_time"]
    readonly_fields = ("create_time", "update_time")
    date_hierarchy = "create_time"


@admin.register(Diary)
class MessagesAdmin(admin.ModelAdmin):
    search_fields = ["type"]
    list_display = ["text", "type", "create_time"]
    readonly_fields = ("create_time", "update_time")
    date_hierarchy = "create_time"
