from datetime import date

import pytest
from django.db.utils import IntegrityError
from returns.maybe import Nothing, Some
from returns.result import Failure, Success

from tests.models import TestModel


@pytest.mark.django_db
class TestGetMethods:
    def test_get_safe_success(self):
        obj = TestModel.objects.create(name="test", dob=date(2020, 1, 1))
        result = TestModel.objects.get_safe(name="test")

        assert isinstance(result, Success)
        assert result.unwrap() == obj

    def test_get_safe_failure(self):
        result = TestModel.objects.get_safe(name="nonexistent")

        assert isinstance(result, Failure)
        assert isinstance(result.failure(), TestModel.DoesNotExist)


@pytest.mark.django_db
class TestEarliestLatestMethods:
    def test_earliest_safe_success(self):
        obj1 = TestModel.objects.create(name="test1", dob=date(2020, 1, 1))
        TestModel.objects.create(name="test2", dob=date(2021, 1, 1))

        result = TestModel.objects.earliest_safe("dob")

        assert isinstance(result, Success)
        assert result.unwrap() == obj1

    def test_earliest_safe_failure(self):
        result = TestModel.objects.earliest_safe("dob")

        assert isinstance(result, Failure)
        assert isinstance(result.failure(), TestModel.DoesNotExist)

    def test_latest_safe_success(self):
        TestModel.objects.create(name="test1", dob=date(2020, 1, 1))
        obj2 = TestModel.objects.create(name="test2", dob=date(2021, 1, 1))

        result = TestModel.objects.latest_safe("dob")

        assert isinstance(result, Success)
        assert result.unwrap() == obj2

    def test_latest_safe_failure(self):
        result = TestModel.objects.latest_safe("dob")

        assert isinstance(result, Failure)
        assert isinstance(result.failure(), TestModel.DoesNotExist)


@pytest.mark.django_db
class TestCreateMethods:
    def test_create_safe_success(self):
        result = TestModel.objects.create_safe(name="test", dob=date(2020, 1, 1))

        assert isinstance(result, Success)
        assert TestModel.objects.count() == 1

    def test_create_safe_failure(self):
        TestModel.objects.create(name="test", dob=date(2020, 1, 1))
        result = TestModel.objects.create_safe(name="test", dob=date(2021, 1, 1))

        assert isinstance(result, Failure)
        assert isinstance(result.failure(), IntegrityError)


@pytest.mark.django_db
class TestGetOrCreateMethods:
    def test_get_or_create_safe_get(self):
        existing = TestModel.objects.create(name="test", dob=date(2020, 1, 1))
        result = TestModel.objects.get_or_create_safe(
            name="test", defaults={"dob": date(2021, 1, 1)}
        )

        assert isinstance(result, Success)
        obj, created = result.unwrap()
        assert obj == existing
        assert created is False

    def test_get_or_create_safe_create(self):
        result = TestModel.objects.get_or_create_safe(
            name="test", defaults={"dob": date(2020, 1, 1)}
        )

        assert isinstance(result, Success)
        obj, created = result.unwrap()
        assert created is True


@pytest.mark.django_db
class TestUpdateOrCreateMethods:
    def test_update_or_create_safe_update(self):
        _ = TestModel.objects.create(name="test", dob=date(2020, 1, 1))
        result = TestModel.objects.update_or_create_safe(
            name="test", defaults={"dob": date(2021, 1, 1)}
        )

        assert isinstance(result, Success)
        obj, created = result.unwrap()
        assert obj.dob == date(2021, 1, 1)
        assert created is False

    def test_update_or_create_safe_create(self):
        result = TestModel.objects.update_or_create_safe(
            name="test", defaults={"dob": date(2020, 1, 1)}
        )

        assert isinstance(result, Success)
        obj, created = result.unwrap()
        assert created is True


@pytest.mark.django_db
class TestDeleteMethods:
    def test_delete_safe_success(self):
        TestModel.objects.create(name="test1", dob=date(2020, 1, 1))
        TestModel.objects.create(name="test2", dob=date(2021, 1, 1))

        result = TestModel.objects.filter(name="test1").delete_safe()

        assert isinstance(result, Success)
        assert TestModel.objects.count() == 1


@pytest.mark.django_db
class TestBulkCreateMethods:
    def test_bulk_create_safe_success(self):
        objects = [
            TestModel(name="test1", dob=date(2020, 1, 1)),
            TestModel(name="test2", dob=date(2021, 1, 1)),
        ]

        result = TestModel.objects.bulk_create_safe(objects)

        assert isinstance(result, Success)
        assert TestModel.objects.count() == 2

    def test_bulk_create_safe_failure(self):
        TestModel.objects.create(name="test1", dob=date(2020, 1, 1))
        objects = [
            TestModel(name="test1", dob=date(2020, 1, 1)),  # Duplicate
            TestModel(name="test2", dob=date(2021, 1, 1)),
        ]

        result = TestModel.objects.bulk_create_safe(objects)

        assert isinstance(result, Failure)


@pytest.mark.django_db
class TestMaybeMethods:
    def test_first_maybe_some(self):
        obj1 = TestModel.objects.create(name="test1", dob=date(2020, 1, 1))
        TestModel.objects.create(name="test2", dob=date(2021, 1, 1))
        
        result = TestModel.objects.first_maybe()
        
        assert isinstance(result, Some)
        assert result.unwrap() == obj1
    
    def test_first_maybe_nothing(self):
        result = TestModel.objects.first_maybe()
        
        assert result == Nothing
    
    def test_last_maybe_some(self):
        TestModel.objects.create(name="test1", dob=date(2020, 1, 1))
        obj2 = TestModel.objects.create(name="test2", dob=date(2021, 1, 1))
        
        result = TestModel.objects.last_maybe()
        
        assert isinstance(result, Some)
        assert result.unwrap() == obj2
    
    def test_last_maybe_nothing(self):
        result = TestModel.objects.last_maybe()
        
        assert result == Nothing
