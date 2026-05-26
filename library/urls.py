from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    BookViewSet,
    LoanViewSet,
    MemberViewSet,
    books_page,
    dashboard,
    loans_page,
    members_page,
)

router = DefaultRouter()
router.register(r"books", BookViewSet, basename="book")
router.register(r"members", MemberViewSet, basename="member")
router.register(r"loans", LoanViewSet, basename="loan")

urlpatterns = [
    path("", dashboard, name="dashboard"),
    path("books/", books_page, name="books-page"),
    path("books/<int:book_id>/edit/", books_page, name="books-edit-page"),
    path("members/", members_page, name="members-page"),
    path("members/<int:member_id>/edit/", members_page, name="members-edit-page"),
    path("loans/", loans_page, name="loans-page"),
    path("api/", include(router.urls)),
]

