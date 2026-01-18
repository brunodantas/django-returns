from datetime import date

import pytest
from django.db.utils import IntegrityError
from returns.io import IOFailure, IOSuccess
from returns.maybe import Nothing, Some
from returns.result import Failure, Success
from returns.unsafe import unsafe_perform_io

from tests.models import Person


@pytest.mark.django_db
class TestGetMethods:
    def test_get_result_success(self):
        obj = Person.objects.create(name="test", dob=date(2020, 1, 1))
        result = Person.objects.get_result(name="test")

        assert isinstance(result, Success)
        assert result.unwrap() == obj

    def test_get_result_failure(self):
        result = Person.objects.get_result(name="nonexistent")

        assert isinstance(result, Failure)
        assert isinstance(result.failure(), Person.DoesNotExist)


@pytest.mark.django_db
class TestEarliestLatestMethods:
    def test_earliest_result_success(self):
        obj1 = Person.objects.create(name="test1", dob=date(2020, 1, 1))
        Person.objects.create(name="test2", dob=date(2021, 1, 1))

        result = Person.objects.earliest_result("dob")

        assert isinstance(result, Success)
        assert result.unwrap() == obj1

    def test_earliest_result_failure(self):
        result = Person.objects.earliest_result("dob")

        assert isinstance(result, Failure)
        assert isinstance(result.failure(), Person.DoesNotExist)

    def test_latest_result_success(self):
        Person.objects.create(name="test1", dob=date(2020, 1, 1))
        obj2 = Person.objects.create(name="test2", dob=date(2021, 1, 1))

        result = Person.objects.latest_result("dob")

        assert isinstance(result, Success)
        assert result.unwrap() == obj2

    def test_latest_result_failure(self):
        result = Person.objects.latest_result("dob")

        assert isinstance(result, Failure)
        assert isinstance(result.failure(), Person.DoesNotExist)


@pytest.mark.django_db
class TestCreateMethods:
    def test_create_result_success(self):
        result = Person.objects.create_result(name="test", dob=date(2020, 1, 1))

        assert isinstance(result, Success)
        assert Person.objects.count() == 1

    def test_create_result_failure(self):
        Person.objects.create(name="test", dob=date(2020, 1, 1))
        result = Person.objects.create_result(name="test", dob=date(2021, 1, 1))

        assert isinstance(result, Failure)
        assert isinstance(result.failure(), IntegrityError)


@pytest.mark.django_db
class TestGetOrCreateMethods:
    def test_get_or_create_result_get(self):
        existing = Person.objects.create(name="test", dob=date(2020, 1, 1))
        result = Person.objects.get_or_create_result(
            name="test", defaults={"dob": date(2021, 1, 1)}
        )

        assert isinstance(result, Success)
        obj, created = result.unwrap()
        assert obj == existing
        assert created is False

    def test_get_or_create_result_create(self):
        result = Person.objects.get_or_create_result(
            name="test", defaults={"dob": date(2020, 1, 1)}
        )

        assert isinstance(result, Success)
        obj, created = result.unwrap()
        assert created is True


@pytest.mark.django_db
class TestUpdateOrCreateMethods:
    def test_update_or_create_result_update(self):
        _ = Person.objects.create(name="test", dob=date(2020, 1, 1))
        result = Person.objects.update_or_create_result(
            name="test", defaults={"dob": date(2021, 1, 1)}
        )

        assert isinstance(result, Success)
        obj, created = result.unwrap()
        assert obj.dob == date(2021, 1, 1)
        assert created is False

    def test_update_or_create_result_create(self):
        result = Person.objects.update_or_create_result(
            name="test", defaults={"dob": date(2020, 1, 1)}
        )

        assert isinstance(result, Success)
        obj, created = result.unwrap()
        assert created is True


@pytest.mark.django_db
class TestDeleteMethods:
    def test_delete_result_success(self):
        Person.objects.create(name="test1", dob=date(2020, 1, 1))
        Person.objects.create(name="test2", dob=date(2021, 1, 1))

        result = Person.objects.filter(name="test1").delete_result()

        assert isinstance(result, Success)
        assert Person.objects.count() == 1


@pytest.mark.django_db
class TestBulkCreateMethods:
    def test_bulk_create_result_success(self):
        objects = [
            Person(name="test1", dob=date(2020, 1, 1)),
            Person(name="test2", dob=date(2021, 1, 1)),
        ]

        result = Person.objects.bulk_create_result(objects)

        assert isinstance(result, Success)
        assert Person.objects.count() == 2

    def test_bulk_create_result_failure(self):
        Person.objects.create(name="test1", dob=date(2020, 1, 1))
        objects = [
            Person(name="test1", dob=date(2020, 1, 1)),  # Duplicate
            Person(name="test2", dob=date(2021, 1, 1)),
        ]

        result = Person.objects.bulk_create_result(objects)

        assert isinstance(result, Failure)


@pytest.mark.django_db
class TestSyncIOResultMethods:
    """Test sync methods that return IOResult (using impure_safe)."""

    def test_get_ioresult_success(self):
        obj = Person.objects.create(name="io_test", dob=date(2020, 1, 1))
        io_result = Person.objects.get_ioresult(name="io_test")

        assert isinstance(io_result, IOSuccess)
        result = unsafe_perform_io(io_result)
        assert isinstance(result, Success)
        assert result.unwrap() == obj

    def test_get_ioresult_failure(self):
        io_result = Person.objects.get_ioresult(name="nonexistent")

        assert isinstance(io_result, IOFailure)
        result = unsafe_perform_io(io_result)
        assert isinstance(result, Failure)
        assert isinstance(result.failure(), Person.DoesNotExist)

    def test_create_ioresult_success(self):
        io_result = Person.objects.create_ioresult(
            name="io_create", dob=date(2020, 1, 1)
        )

        assert isinstance(io_result, IOSuccess)
        result = unsafe_perform_io(io_result)
        assert isinstance(result, Success)
        obj = result.unwrap()
        assert obj.name == "io_create"
        assert Person.objects.count() == 1

    def test_create_ioresult_failure(self):
        Person.objects.create(name="duplicate", dob=date(2020, 1, 1))
        io_result = Person.objects.create_ioresult(
            name="duplicate", dob=date(2021, 1, 1)
        )

        assert isinstance(io_result, IOFailure)
        result = unsafe_perform_io(io_result)
        assert isinstance(result, Failure)
        assert isinstance(result.failure(), IntegrityError)

    def test_earliest_ioresult_success(self):
        obj1 = Person.objects.create(name="io_earliest1", dob=date(2020, 1, 1))
        Person.objects.create(name="io_earliest2", dob=date(2021, 1, 1))

        io_result = Person.objects.earliest_ioresult("dob")

        assert isinstance(io_result, IOSuccess)
        result = unsafe_perform_io(io_result)
        assert result.unwrap() == obj1

    def test_latest_ioresult_success(self):
        Person.objects.create(name="io_latest1", dob=date(2020, 1, 1))
        obj2 = Person.objects.create(name="io_latest2", dob=date(2021, 1, 1))

        io_result = Person.objects.latest_ioresult("dob")

        assert isinstance(io_result, IOSuccess)
        result = unsafe_perform_io(io_result)
        assert result.unwrap() == obj2

    def test_delete_ioresult_success(self):
        Person.objects.create(name="io_delete1", dob=date(2020, 1, 1))
        Person.objects.create(name="io_delete2", dob=date(2021, 1, 1))

        io_result = Person.objects.filter(name="io_delete1").delete_ioresult()

        assert isinstance(io_result, IOSuccess)
        result = unsafe_perform_io(io_result)
        assert isinstance(result, Success)
        assert Person.objects.count() == 1

    def test_bulk_create_ioresult_success(self):
        objects = [
            Person(name="io_bulk1", dob=date(2020, 1, 1)),
            Person(name="io_bulk2", dob=date(2021, 1, 1)),
        ]

        io_result = Person.objects.bulk_create_ioresult(objects)

        assert isinstance(io_result, IOSuccess)
        result = unsafe_perform_io(io_result)
        assert isinstance(result, Success)
        assert Person.objects.count() == 2


@pytest.mark.django_db
class TestMaybeMethods:
    def test_first_maybe_some(self):
        obj1 = Person.objects.create(name="test1", dob=date(2020, 1, 1))
        Person.objects.create(name="test2", dob=date(2021, 1, 1))

        result = Person.objects.first_maybe()

        assert isinstance(result, Some)
        assert result.unwrap() == obj1

    def test_first_maybe_nothing(self):
        result = Person.objects.first_maybe()

        assert result == Nothing

    def test_last_maybe_some(self):
        Person.objects.create(name="test1", dob=date(2020, 1, 1))
        obj2 = Person.objects.create(name="test2", dob=date(2021, 1, 1))

        result = Person.objects.last_maybe()

        assert isinstance(result, Some)
        assert result.unwrap() == obj2

    def test_last_maybe_nothing(self):
        result = Person.objects.last_maybe()

        assert result == Nothing


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
class TestAsyncIOResultMethods:
    """Test async methods that return FutureResult -> IOResult (using future_safe)."""

    async def test_aget_ioresult_success(self):
        obj = await Person.objects.acreate(name="async_test", dob=date(2020, 1, 1))
        result = await Person.objects.aget_ioresult(name="async_test")

        assert isinstance(result, IOSuccess)
        assert unsafe_perform_io(result).unwrap() == obj

    async def test_aget_ioresult_failure(self):
        result = await Person.objects.aget_ioresult(name="nonexistent")

        assert isinstance(result, IOFailure)
        assert isinstance(unsafe_perform_io(result).failure(), Person.DoesNotExist)

    async def test_aearliest_ioresult_success(self):
        obj1 = await Person.objects.acreate(
            name="async_earliest1", dob=date(2020, 1, 1)
        )
        await Person.objects.acreate(name="async_earliest2", dob=date(2021, 1, 1))

        result = await Person.objects.aearliest_ioresult("dob")

        assert isinstance(result, IOSuccess)
        assert unsafe_perform_io(result).unwrap() == obj1

    async def test_aearliest_ioresult_failure(self):
        result = await Person.objects.aearliest_ioresult("dob")

        assert isinstance(result, IOFailure)

    async def test_alatest_ioresult_success(self):
        await Person.objects.acreate(name="async_latest1", dob=date(2020, 1, 1))
        obj2 = await Person.objects.acreate(name="async_latest2", dob=date(2021, 1, 1))

        result = await Person.objects.alatest_ioresult("dob")

        assert isinstance(result, IOSuccess)
        assert unsafe_perform_io(result).unwrap() == obj2

    async def test_alatest_ioresult_failure(self):
        result = await Person.objects.alatest_ioresult("dob")

        assert isinstance(result, IOFailure)


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
class TestAsyncCreateMethods:
    async def test_acreate_ioresult_success(self):
        result = await Person.objects.acreate_ioresult(
            name="async_create", dob=date(2020, 1, 1)
        )

        assert isinstance(result, IOSuccess)
        obj = unsafe_perform_io(result).unwrap()
        assert obj.name == "async_create"

    async def test_acreate_ioresult_failure(self):
        await Person.objects.acreate(name="duplicate_async", dob=date(2020, 1, 1))
        result = await Person.objects.acreate_ioresult(
            name="duplicate_async", dob=date(2021, 1, 1)
        )

        assert isinstance(result, IOFailure)
        assert isinstance(unsafe_perform_io(result).failure(), IntegrityError)

    async def test_aget_or_create_ioresult_get(self):
        existing = await Person.objects.acreate(
            name="existing_async", dob=date(2020, 1, 1)
        )
        result = await Person.objects.aget_or_create_ioresult(
            name="existing_async", defaults={"dob": date(2021, 1, 1)}
        )

        assert isinstance(result, IOSuccess)
        obj, created = unsafe_perform_io(result).unwrap()
        assert obj == existing
        assert created is False

    async def test_aget_or_create_ioresult_create(self):
        result = await Person.objects.aget_or_create_ioresult(
            name="new_async", defaults={"dob": date(2020, 1, 1)}
        )

        assert isinstance(result, IOSuccess)
        obj, created = unsafe_perform_io(result).unwrap()
        assert obj.name == "new_async"
        assert created is True

    async def test_aupdate_or_create_ioresult_update(self):
        existing = await Person.objects.acreate(
            name="update_me_async", dob=date(2020, 1, 1)
        )
        result = await Person.objects.aupdate_or_create_ioresult(
            name="update_me_async", defaults={"dob": date(2021, 1, 1)}
        )

        assert isinstance(result, IOSuccess)
        obj, created = unsafe_perform_io(result).unwrap()
        assert obj.id == existing.id
        assert obj.dob == date(2021, 1, 1)
        assert created is False

    async def test_aupdate_or_create_ioresult_create(self):
        result = await Person.objects.aupdate_or_create_ioresult(
            name="create_new_async", defaults={"dob": date(2020, 1, 1)}
        )

        assert isinstance(result, IOSuccess)
        obj, created = unsafe_perform_io(result).unwrap()
        assert obj.name == "create_new_async"
        assert created is True

    async def test_adelete_ioresult_success(self):
        await Person.objects.acreate(name="delete1_async", dob=date(2020, 1, 1))
        await Person.objects.acreate(name="delete2_async", dob=date(2021, 1, 1))

        result = await Person.objects.filter(name="delete1_async").adelete_ioresult()
        assert isinstance(result, IOSuccess)
        deleted_count, _ = unsafe_perform_io(result).unwrap()
        assert deleted_count == 1

    async def test_abulk_create_ioresult_success(self):
        objects = [
            Person(name="bulk1_async", dob=date(2020, 1, 1)),
            Person(name="bulk2_async", dob=date(2021, 1, 1)),
            Person(name="bulk3_async", dob=date(2022, 1, 1)),
        ]

        result = await Person.objects.abulk_create_ioresult(objects)

        assert isinstance(result, IOSuccess)
        created = unsafe_perform_io(result).unwrap()
        assert len(created) == 3

    async def test_abulk_create_ioresult_failure(self):
        await Person.objects.acreate(name="bulk1_fail_async", dob=date(2020, 1, 1))
        objects = [
            Person(name="bulk1_fail_async", dob=date(2020, 1, 1)),  # Duplicate
            Person(name="bulk2_fail_async", dob=date(2021, 1, 1)),
        ]

        result = await Person.objects.abulk_create_ioresult(objects)

        assert isinstance(result, IOFailure)
        assert isinstance(unsafe_perform_io(result).failure(), IntegrityError)
