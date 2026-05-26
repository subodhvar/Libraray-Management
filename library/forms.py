from django import forms

from .models import Book, Member


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ["title", "author", "isbn", "published_year", "total_copies", "available_copies"]


class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ["full_name", "email", "phone", "address", "is_active"]


class BorrowForm(forms.Form):
    book_id = forms.IntegerField(min_value=1)
    member_id = forms.IntegerField(min_value=1)
    due_date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
    notes = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 2}))


class ReturnForm(forms.Form):
    loan_id = forms.IntegerField(min_value=1)

