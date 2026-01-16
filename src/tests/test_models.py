import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models import ProtectedError
from returns.result import Failure, Success

from tests.models import Author, Book, ValidatedModel


@pytest.mark.django_db
class TestSaveSafe:
    def test_save_safe_success(self):
        author = Author(name="Test Author")
        result = author.save_safe()
        
        assert isinstance(result, Success)
        assert author.pk is not None
        assert Author.objects.count() == 1
    
    def test_save_safe_integrity_error(self):
        Author.objects.create(name="Duplicate")
        author = Author(name="Duplicate")
        result = author.save_safe()
        
        assert isinstance(result, Failure)
        assert isinstance(result.failure(), IntegrityError)
    
    def test_save_safe_with_validation(self):
        model = ValidatedModel(value=10)
        result = model.save_safe()
        
        assert isinstance(result, Success)
        assert ValidatedModel.objects.count() == 1


@pytest.mark.django_db
class TestDeleteSafe:
    def test_delete_safe_success(self):
        author = Author.objects.create(name="Test Author")
        result = author.delete_safe()
        
        assert isinstance(result, Success)
        deleted_count, _ = result.unwrap()
        assert deleted_count == 1
        assert Author.objects.count() == 0
    
    def test_delete_safe_protected_error(self):
        author = Author.objects.create(name="Test Author")
        Book.objects.create(title="Test Book", author=author)
        
        result = author.delete_safe()
        
        assert isinstance(result, Failure)
        assert isinstance(result.failure(), ProtectedError)
        assert Author.objects.count() == 1


@pytest.mark.django_db
class TestFullCleanSafe:
    def test_full_clean_safe_success(self):
        author = Author(name="Valid Name")
        result = author.full_clean_safe()
        
        assert isinstance(result, Success)
    
    def test_full_clean_safe_validation_error(self):
        model = ValidatedModel(value=-5)
        result = model.full_clean_safe()
        
        assert isinstance(result, Failure)
        assert isinstance(result.failure(), ValidationError)
    
    def test_full_clean_safe_field_error(self):
        # CharField with max_length=100, providing too long value
        author = Author(name="x" * 101)
        result = author.full_clean_safe()
        
        assert isinstance(result, Failure)
        assert isinstance(result.failure(), ValidationError)
    
    def test_full_clean_safe_unique_constraint(self):
        Author.objects.create(name="Unique Name")
        author = Author(name="Unique Name")
        result = author.full_clean_safe()
        
        assert isinstance(result, Failure)
        assert isinstance(result.failure(), ValidationError)


@pytest.mark.django_db
class TestRefreshFromDbSafe:
    def test_refresh_from_db_safe_success(self):
        author = Author.objects.create(name="Original")
        # Modify in another query
        Author.objects.filter(pk=author.pk).update(name="Updated")
        
        result = author.refresh_from_db_safe()
        
        assert isinstance(result, Success)
        assert author.name == "Updated"
    
    def test_refresh_from_db_safe_does_not_exist(self):
        author = Author.objects.create(name="Test")
        author_pk = author.pk
        author.delete()
        
        # Create a new instance with the deleted pk
        deleted_author = Author(pk=author_pk, name="Test")
        result = deleted_author.refresh_from_db_safe()
        
        assert isinstance(result, Failure)
        # The error type depends on Django version, but it should be a failure
