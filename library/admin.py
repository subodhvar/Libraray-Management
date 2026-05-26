from django.contrib import admin

from .models import Book, Loan, Member


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
	list_display = ("title", "author", "isbn", "total_copies", "available_copies")
	search_fields = ("title", "author", "isbn")


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
	list_display = ("full_name", "email", "phone", "is_active")
	search_fields = ("full_name", "email")
	list_filter = ("is_active",)


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
	list_display = ("id", "book", "member", "borrowed_at", "due_date", "returned_at")
	search_fields = ("book__title", "member__full_name")
	list_filter = ("due_date", "returned_at")
