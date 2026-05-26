from rest_framework import status
from rest_framework.test import APITestCase

from .models import Book, Loan, Member


class LibraryApiTests(APITestCase):
	def setUp(self):
		self.book = Book.objects.create(
			title="Clean Code",
			author="Robert C. Martin",
			isbn="9780132350884",
			total_copies=1,
			available_copies=1,
		)
		self.member = Member.objects.create(
			full_name="John Doe",
			email="john@example.com",
			phone="1234567890",
		)

	def test_create_book(self):
		response = self.client.post(
			"/api/books/",
			{
				"title": "Design Patterns",
				"author": "GoF",
				"isbn": "9780201633610",
				"total_copies": 2,
				"available_copies": 2,
			},
			format="json",
		)
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

	def test_borrow_book(self):
		response = self.client.post(
			f"/api/books/{self.book.id}/borrow/",
			{
				"member_id": self.member.id,
				"due_date": "2099-01-01",
			},
			format="json",
		)
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.book.refresh_from_db()
		self.assertEqual(self.book.available_copies, 0)

	def test_borrow_unavailable_book(self):
		Loan.objects.create(book=self.book, member=self.member, due_date="2099-01-01")
		self.book.available_copies = 0
		self.book.save(update_fields=["available_copies"])
		response = self.client.post(
			f"/api/books/{self.book.id}/borrow/",
			{
				"member_id": self.member.id,
				"due_date": "2099-01-01",
			},
			format="json",
		)
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

	def test_return_book(self):
		loan = Loan.objects.create(book=self.book, member=self.member, due_date="2099-01-01")
		self.book.available_copies = 0
		self.book.save(update_fields=["available_copies"])

		response = self.client.post(
			f"/api/books/{self.book.id}/return/",
			{
				"loan_id": loan.id,
			},
			format="json",
		)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		loan.refresh_from_db()
		self.assertIsNotNone(loan.returned_at)
		self.book.refresh_from_db()
		self.assertEqual(self.book.available_copies, 1)
