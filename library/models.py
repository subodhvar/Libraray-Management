from django.db import models


class TimeStampedModel(models.Model):
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		abstract = True


class Book(TimeStampedModel):
	title = models.CharField(max_length=255)
	author = models.CharField(max_length=255)
	isbn = models.CharField(max_length=20, unique=True)
	published_year = models.PositiveIntegerField(null=True, blank=True)
	total_copies = models.PositiveIntegerField(default=1)
	available_copies = models.PositiveIntegerField(default=1)

	class Meta:
		ordering = ["title", "author"]

	def __str__(self) -> str:
		return f"{self.title} by {self.author}"


class Member(TimeStampedModel):
	full_name = models.CharField(max_length=255)
	email = models.EmailField(unique=True)
	phone = models.CharField(max_length=20)
	address = models.CharField(max_length=255, blank=True)
	is_active = models.BooleanField(default=True)

	class Meta:
		ordering = ["full_name"]

	def __str__(self) -> str:
		return self.full_name


class Loan(TimeStampedModel):
	book = models.ForeignKey(Book, on_delete=models.PROTECT, related_name="loans")
	member = models.ForeignKey(Member, on_delete=models.PROTECT, related_name="loans")
	borrowed_at = models.DateTimeField(auto_now_add=True)
	due_date = models.DateField()
	returned_at = models.DateTimeField(null=True, blank=True)
	notes = models.TextField(blank=True)

	class Meta:
		ordering = ["-borrowed_at"]

	@property
	def is_returned(self) -> bool:
		return self.returned_at is not None

	def __str__(self) -> str:
		return f"Loan #{self.pk}: {self.book.title} -> {self.member.full_name}"
