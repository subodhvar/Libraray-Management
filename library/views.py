from datetime import timedelta

from django.contrib import messages
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .forms import BookForm, BorrowForm, MemberForm, ReturnForm
from .models import Book, Loan, Member
from .serializers import (
	BookSerializer,
	BorrowBookSerializer,
	LoanSerializer,
	MemberSerializer,
	ReturnBookSerializer,
)


def dashboard(request):
	context = {
		"book_count": Book.objects.count(),
		"member_count": Member.objects.count(),
		"active_loan_count": Loan.objects.filter(returned_at__isnull=True).count(),
		"recent_loans": Loan.objects.select_related("book", "member")[:5],
	}
	return render(request, "library/dashboard.html", context)


def books_page(request, book_id=None):
	book_instance = get_object_or_404(Book, pk=book_id) if book_id else None

	if request.method == "POST":
		form = BookForm(request.POST, instance=book_instance)
		if form.is_valid():
			form.save()
			messages.success(request, "Book updated successfully." if book_instance else "Book saved successfully.")
			return redirect("books-page")
	else:
		form = BookForm(instance=book_instance)

	context = {
		"form": form,
		"books": Book.objects.all(),
		"editing_book": book_instance,
	}
	return render(request, "library/books.html", context)


def members_page(request, member_id=None):
	member_instance = get_object_or_404(Member, pk=member_id) if member_id else None

	if request.method == "POST":
		form = MemberForm(request.POST, instance=member_instance)
		if form.is_valid():
			form.save()
			messages.success(request, "Member updated successfully." if member_instance else "Member saved successfully.")
			return redirect("members-page")
	else:
		form = MemberForm(instance=member_instance)

	context = {
		"form": form,
		"members": Member.objects.all(),
		"editing_member": member_instance,
	}
	return render(request, "library/members.html", context)


def loans_page(request):
	if request.method == "POST":
		if request.POST.get("action") == "borrow":
			borrow_form = BorrowForm(request.POST)
			if borrow_form.is_valid():
				result, success = _borrow_book(
					book_id=borrow_form.cleaned_data["book_id"],
					member_id=borrow_form.cleaned_data["member_id"],
					due_date=borrow_form.cleaned_data["due_date"],
					notes=borrow_form.cleaned_data.get("notes", ""),
				)
				if success:
					messages.success(request, "Book borrowed successfully.")
					return redirect("loans-page")
				messages.error(request, result)
			return redirect("loans-page")

		if request.POST.get("action") == "return":
			return_form = ReturnForm(request.POST)
			if return_form.is_valid():
				result, success = _return_book(return_form.cleaned_data["loan_id"])
				if success:
					messages.success(request, "Book returned successfully.")
					return redirect("loans-page")
				messages.error(request, result)
			return redirect("loans-page")

	context = {
		"borrow_form": BorrowForm(initial={"due_date": timezone.localdate() + timedelta(days=14)}),
		"return_form": ReturnForm(),
		"active_loans": Loan.objects.select_related("book", "member").filter(returned_at__isnull=True),
		"all_loans": Loan.objects.select_related("book", "member")[:25],
	}
	return render(request, "library/loans.html", context)


class BookViewSet(viewsets.ModelViewSet):
	queryset = Book.objects.all()
	serializer_class = BookSerializer

	@action(detail=True, methods=["post"], url_path="borrow")
	def borrow_book(self, request, pk=None):
		serializer = BorrowBookSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		result, success = _borrow_book(
			book_id=pk,
			member_id=serializer.validated_data["member_id"],
			due_date=serializer.validated_data["due_date"],
			notes=serializer.validated_data.get("notes", ""),
		)
		if not success:
			return Response({"detail": result}, status=status.HTTP_400_BAD_REQUEST)
		return Response(LoanSerializer(result).data, status=status.HTTP_201_CREATED)

	@action(detail=True, methods=["post"], url_path="return")
	def return_book(self, request, pk=None):
		serializer = ReturnBookSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		result, success = _return_book(serializer.validated_data["loan_id"], expected_book_id=int(pk))
		if not success:
			return Response({"detail": result}, status=status.HTTP_400_BAD_REQUEST)
		return Response(LoanSerializer(result).data, status=status.HTTP_200_OK)


class MemberViewSet(viewsets.ModelViewSet):
	queryset = Member.objects.all()
	serializer_class = MemberSerializer

	@action(detail=True, methods=["get"], url_path="borrowed-books")
	def borrowed_books(self, request, pk=None):
		loans = (
			Loan.objects.select_related("book", "member")
			.filter(member_id=pk, returned_at__isnull=True)
			.order_by("due_date")
		)
		return Response(LoanSerializer(loans, many=True).data)


class LoanViewSet(viewsets.ReadOnlyModelViewSet):
	queryset = Loan.objects.select_related("book", "member")
	serializer_class = LoanSerializer

	def get_queryset(self):
		queryset = super().get_queryset()
		active = self.request.query_params.get("active")
		member_id = self.request.query_params.get("member_id")
		if active == "true":
			queryset = queryset.filter(returned_at__isnull=True)
		if member_id:
			queryset = queryset.filter(member_id=member_id)
		return queryset


@transaction.atomic
def _borrow_book(book_id, member_id, due_date, notes=""):
	try:
		book = Book.objects.select_for_update().get(pk=book_id)
	except Book.DoesNotExist:
		return "Book does not exist.", False

	try:
		member = Member.objects.get(pk=member_id, is_active=True)
	except Member.DoesNotExist:
		return "Member does not exist or is inactive.", False

	if book.available_copies < 1:
		return "Book is currently unavailable.", False

	loan = Loan.objects.create(book=book, member=member, due_date=due_date, notes=notes)
	book.available_copies -= 1
	book.save(update_fields=["available_copies", "updated_at"])
	return loan, True


@transaction.atomic
def _return_book(loan_id, expected_book_id=None):
	try:
		loan = Loan.objects.select_for_update().select_related("book").get(pk=loan_id)
	except Loan.DoesNotExist:
		return "Loan does not exist.", False

	if expected_book_id is not None and loan.book_id != expected_book_id:
		return "Loan does not belong to this book.", False

	if loan.returned_at is not None:
		return "Book was already returned.", False

	loan.returned_at = timezone.now()
	loan.save(update_fields=["returned_at", "updated_at"])

	book = loan.book
	book.available_copies += 1
	if book.available_copies > book.total_copies:
		book.available_copies = book.total_copies
	book.save(update_fields=["available_copies", "updated_at"])
	return loan, True
