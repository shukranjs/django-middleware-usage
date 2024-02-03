# views.py
from django.shortcuts import render


def book_list(request):
    books = [
        {"title": "Book 1", "author": "Author 1"},
        {"title": "Book 2", "author": "Author 2"},
        {"title": "Book 3", "author": "Author 3"},
    ]
    return render(request, "book_list.html", {"books": books})
