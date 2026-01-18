from datetime import date

import pytest
from django.db import models
from django.db.utils import IntegrityError
from returns.io import IOFailure, IOSuccess
from returns.result import Failure, Success
from returns.unsafe import unsafe_perform_io

from django_returns.managers import ReturnsManager


# Test models with different manager configurations
class SafePerson(models.Model):
    name = models.CharField(max_length=100, unique=True)
    dob = models.DateField()

    objects = ReturnsManager(override_with="safe")

    class Meta:
        app_label = "tests"


class ImpurePerson(models.Model):
    name = models.CharField(max_length=100, unique=True)
    dob = models.DateField()

    objects = ReturnsManager(override_with="impure")

    class Meta:
        app_label = "tests"


@pytest.mark.django_db
class TestSafeReturnsQuerySet:
    """Test that SafeReturnsQuerySet overrides methods to return Result."""

    def test_get_returns_result_success(self):
        obj = SafePerson.objects.create(name="test", dob=date(2020, 1, 1)).unwrap()
        result = SafePerson.objects.get(name="test")

        assert isinstance(result, Success)
        assert result.unwrap() == obj

    def test_get_returns_result_failure(self):
        result = SafePerson.objects.get(name="nonexistent")

        assert isinstance(result, Failure)
        assert isinstance(result.failure(), SafePerson.DoesNotExist)

    def test_create_returns_result_success(self):
        result = SafePerson.objects.create(name="test", dob=date(2020, 1, 1))

        assert isinstance(result, Success)
        created_obj = result.unwrap()
        assert created_obj.name == "test"

    def test_create_returns_result_failure(self):
        SafePerson.objects.create(name="test", dob=date(2020, 1, 1))
        result = SafePerson.objects.create(name="test", dob=date(2021, 1, 1))

        assert isinstance(result, Failure)
        assert isinstance(result.failure(), IntegrityError)

    def test_delete_returns_result(self):
        SafePerson.objects.create(name="test1", dob=date(2020, 1, 1))
        SafePerson.objects.create(name="test2", dob=date(2021, 1, 1))

        result = SafePerson.objects.filter(name="test1").delete()

        assert isinstance(result, Success)
        count, _ = result.unwrap()
        assert count == 1


@pytest.mark.django_db
class TestImpureReturnsQuerySet:
    """Test that ImpureReturnsQuerySet overrides methods to return IOResult."""

    def test_get_returns_ioresult_success(self):
        obj = unsafe_perform_io(
            ImpurePerson.objects.create(name="test", dob=date(2020, 1, 1))
        ).unwrap()
        result = ImpurePerson.objects.get(name="test")

        assert isinstance(result, IOSuccess)
        assert unsafe_perform_io(result).unwrap() == obj

    def test_get_returns_ioresult_failure(self):
        result = ImpurePerson.objects.get(name="nonexistent")

        assert isinstance(result, IOFailure)
        assert isinstance(
            unsafe_perform_io(result).failure(), ImpurePerson.DoesNotExist
        )

    def test_create_returns_ioresult_success(self):
        result = ImpurePerson.objects.create(name="test", dob=date(2020, 1, 1))

        assert isinstance(result, IOSuccess)
        created_obj = unsafe_perform_io(result).unwrap()
        assert created_obj.name == "test"

    def test_create_returns_ioresult_failure(self):
        ImpurePerson.objects.create(name="test", dob=date(2020, 1, 1))
        result = ImpurePerson.objects.create(name="test", dob=date(2021, 1, 1))

        assert isinstance(result, IOFailure)
        assert isinstance(unsafe_perform_io(result).failure(), IntegrityError)

    def test_delete_returns_ioresult(self):
        ImpurePerson.objects.create(name="test1", dob=date(2020, 1, 1))
        ImpurePerson.objects.create(name="test2", dob=date(2021, 1, 1))

        result = ImpurePerson.objects.filter(name="test1").delete()

        assert isinstance(result, IOSuccess)
        count, _ = unsafe_perform_io(result).unwrap()
        assert count == 1
