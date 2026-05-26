from django.utils import timezone
from rest_framework import serializers

from .models import Book, Loan, Member


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = [
            "id",
            "title",
            "author",
            "isbn",
            "published_year",
            "total_copies",
            "available_copies",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def validate(self, attrs):
        total = attrs.get("total_copies", getattr(self.instance, "total_copies", 0))
        available = attrs.get("available_copies", getattr(self.instance, "available_copies", 0))
        if available > total:
            raise serializers.ValidationError("Available copies cannot exceed total copies.")
        return attrs


class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = [
            "id",
            "full_name",
            "email",
            "phone",
            "address",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]


class LoanSerializer(serializers.ModelSerializer):
    book_title = serializers.CharField(source="book.title", read_only=True)
    member_name = serializers.CharField(source="member.full_name", read_only=True)

    class Meta:
        model = Loan
        fields = [
            "id",
            "book",
            "book_title",
            "member",
            "member_name",
            "borrowed_at",
            "due_date",
            "returned_at",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["borrowed_at", "returned_at", "created_at", "updated_at"]


class BorrowBookSerializer(serializers.Serializer):
    member_id = serializers.IntegerField()
    due_date = serializers.DateField()
    notes = serializers.CharField(required=False, allow_blank=True)

    def validate_due_date(self, value):
        if value < timezone.localdate():
            raise serializers.ValidationError("Due date cannot be in the past.")
        return value


class ReturnBookSerializer(serializers.Serializer):
    loan_id = serializers.IntegerField()

