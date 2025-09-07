from django import forms
from django.contrib import admin
from django.contrib.auth.hashers import make_password
from django.db import transaction
from . import models


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = models.Employee
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "data_licenziamento" in self.fields:
            self.fields["data_licenziamento"].required = False


class UserForm(forms.ModelForm):
    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(render_value=False),
        help_text="Enter a password. Leave empty when editing to keep the current password.",
    )

    class Meta:
        model = models.User
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not getattr(self.instance, "username", None):
            self.fields["password"].required = True


@admin.register(models.Person)
class Person(admin.ModelAdmin):
    list_display = ("cf", "name", "surname", "phone", "city")
    search_fields = ("cf", "name", "surname")


@admin.register(models.User)
class User(admin.ModelAdmin):
    form = UserForm
    list_display = ("username", "cf", "email")
    search_fields = ("username",)

    def save_model(self, request, obj, form, change):
        pwd = form.cleaned_data.get("password")
        if change:
            if not pwd:
                try:
                    existing = models.User.objects.get(username=obj.username)
                    obj.password = existing.password
                except models.User.DoesNotExist:
                    raise ValueError("Existing user not found; password required.")
            else:
                obj.password = make_password(pwd)
        else:
            obj.password = make_password(pwd)
        with transaction.atomic():
            obj.save()


@admin.register(models.Hosts)
class Hosts(admin.ModelAdmin):
    list_display = ("cf", "username", "hosting_date")
    search_fields = ("cf", "username")


@admin.register(models.Package)
class Package(admin.ModelAdmin):
    list_display = ("id", "name", "description")
    search_fields = ("id",)


@admin.register(models.Service)
class Service(admin.ModelAdmin):
    list_display = ("id", "type", "price", "status")
    search_fields = ("id",)


@admin.register(models.Compound)
class Compound(admin.ModelAdmin):
    list_display = ("id", "package", "service")
    search_fields = ("id",)


@admin.register(models.Purchase)
class Purchase(admin.ModelAdmin):
    list_display = ("id", "package", "username", "purchase_date")
    search_fields = ("id",)


@admin.register(models.Restaurant)
class Restaurant(admin.ModelAdmin):
    list_display = ("id", "table_code", "max_capacity")
    search_fields = ("id",)


@admin.register(models.Pool)
class Pool(admin.ModelAdmin):
    list_display = ("id", "sunbed_code")
    search_fields = ("id",)


@admin.register(models.Playground)
class Playground(admin.ModelAdmin):
    list_display = ("id", "playground_code", "max_capacity")
    search_fields = ("id",)


@admin.register(models.Room)
class Room(admin.ModelAdmin):
    list_display = ("id", "room_code", "max_capacity")
    search_fields = ("id",)


@admin.register(models.AnimalActivity)
class AnimalActivity(admin.ModelAdmin):
    list_display = ("id", "activity_code", "description")
    search_fields = ("id",)


@admin.register(models.Booking)
class Booking(admin.ModelAdmin):
    list_display = ("id", "username", "booking_date")
    search_fields = ("id",)


@admin.register(models.BookingDetail)
class BookingDetails(admin.ModelAdmin):
    list_display = ("booking", "service", "start_date", "end_date")
    search_fields = (
        "booking",
        "service",
    )


@admin.register(models.Review)
class Review(admin.ModelAdmin):
    list_display = (
        "id",
        "service_type",
        "vote",
        "description",
        "username",
        "id_booking",
        "review_date",
    )
    search_fields = ("id",)


@admin.register(models.Employee)
class Employee(admin.ModelAdmin):
    form = EmployeeForm
    list_display = ("username", "hire_date", "termination_date")
    search_fields = ("username",)


@admin.register(models.Event)
class Event(admin.ModelAdmin):
    list_display = ("id", "seats", "title", "description", "date", "username")
    search_fields = ("id",)


@admin.register(models.Enrolls)
class Enrolls(admin.ModelAdmin):
    list_display = ("id", "event", "username", "enroll_date", "participants")
    search_fields = ("id",)


@admin.register(models.Product)
class Product(admin.ModelAdmin):
    list_display = ("id", "name", "price")
    search_fields = ("id",)


@admin.register(models.Order)
class Order(admin.ModelAdmin):
    list_display = ("id", "username", "date")
    search_fields = ("id",)


@admin.register(models.OrderDetail)
class OrderDetail(admin.ModelAdmin):
    list_display = ("id", "order", "product", "quantity", "unit_price")
    search_fields = ("id",)


@admin.register(models.EmployeeRoleHistory)
class EmployeeRoleHistory(admin.ModelAdmin):
    list_display = ("username", "role", "start_date", "end_date")
    search_fields = ("username",)


@admin.register(models.Shift)
class Shift(admin.ModelAdmin):
    list_display = ("id", "day", "start_hour", "end_hour")
    search_fields = ("id", "day")


@admin.register(models.Performs)
class PerformsAdmin(admin.ModelAdmin):
    list_display = ("username", "shift", "start_date")
    search_fields = ("username__username", "shift__id")
    list_filter = ("shift__day",)
