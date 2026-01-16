import pytest
from returns.result import Failure, Success

from django_returns.utils import getattr_safe
from tests.models import Author, Book


@pytest.mark.django_db
class TestGetAttrSafeWithForeignKeys:
    def test_getattr_safe_existing_fk(self):
        """Access an existing foreign key relationship."""
        author = Author.objects.create(name="Jane Austen")
        book = Book.objects.create(title="Pride and Prejudice", author=author)

        result = getattr_safe(book, "author")

        assert isinstance(result, Success)
        assert result.unwrap() == author

    def test_getattr_safe_chained_fk(self):
        """Chain multiple FK accesses."""
        author = Author.objects.create(name="Jane Austen")
        book = Book.objects.create(title="Pride and Prejudice", author=author)

        # Access book.author
        result1 = getattr_safe(book, "author")
        assert isinstance(result1, Success)
        assert result1.unwrap() == author

        # Access book.author.name
        result2 = getattr_safe(result1.unwrap(), "name")
        assert isinstance(result2, Success)
        assert result2.unwrap() == "Jane Austen"

    def test_getattr_safe_invalid_attribute(self):
        """Access a non-existent attribute."""
        author = Author.objects.create(name="Jane Austen")

        result = getattr_safe(author, "nonexistent_field")

        assert isinstance(result, Failure)
        assert isinstance(result.failure(), AttributeError)

    def test_getattr_safe_regular_field(self):
        """Access a regular field (not FK)."""
        author = Author.objects.create(name="Jane Austen")

        result = getattr_safe(author, "name")

        assert isinstance(result, Success)
        assert result.unwrap() == "Jane Austen"

    def test_getattr_safe_reverse_relation(self):
        """Access reverse FK relationship (returns manager)."""
        author = Author.objects.create(name="Jane Austen")
        Book.objects.create(title="Pride and Prejudice", author=author)
        Book.objects.create(title="Sense and Sensibility", author=author)

        result = getattr_safe(author, "books")

        # Returns the RelatedManager
        assert isinstance(result, Success)
        manager = result.unwrap()
        assert manager.count() == 2

    def test_getattr_safe_pk_field(self):
        """Access primary key field."""
        author = Author.objects.create(name="Jane Austen")

        result = getattr_safe(author, "pk")

        assert isinstance(result, Success)
        assert result.unwrap() == author.pk

    def test_getattr_safe_id_field(self):
        """Access id field."""
        author = Author.objects.create(name="Jane Austen")

        result = getattr_safe(author, "id")

        assert isinstance(result, Success)
        assert result.unwrap() == author.id
