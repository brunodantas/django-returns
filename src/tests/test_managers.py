from datetime import date

import pytest
from django.db.utils import IntegrityError
from returns.io import IOFailure, IOSuccess
from returns.maybe import Nothing, Some
from returns.result import Failure, Success
from returns.unsafe import unsafe_perform_io

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


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
class TestAsyncGetMethods:
    async def test_aget_safe_success(self):
        obj = await TestModel.objects.acreate(name="async_test", dob=date(2020, 1, 1))
        result = await TestModel.objects.aget_safe(name="async_test")

        assert isinstance(result, IOSuccess)
        assert unsafe_perform_io(result).unwrap() == obj

    async def test_aget_safe_failure(self):
        result = await TestModel.objects.aget_safe(name="nonexistent")

        assert isinstance(result, IOFailure)
        assert isinstance(unsafe_perform_io(result).failure(), TestModel.DoesNotExist)


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
class TestAsyncEarliestLatestMethods:
    async def test_aearliest_safe_success(self):
        obj1 = await TestModel.objects.acreate(
            name="async_earliest1", dob=date(2020, 1, 1)
        )
        await TestModel.objects.acreate(name="async_earliest2", dob=date(2021, 1, 1))

        result = await TestModel.objects.aearliest_safe("dob")

        assert isinstance(result, IOSuccess)
        assert unsafe_perform_io(result).unwrap() == obj1

    async def test_aearliest_safe_failure(self):
        result = await TestModel.objects.aearliest_safe("dob")

        assert isinstance(result, IOFailure)

    async def test_alatest_safe_success(self):
        await TestModel.objects.acreate(name="async_latest1", dob=date(2020, 1, 1))
        obj2 = await TestModel.objects.acreate(
            name="async_latest2", dob=date(2021, 1, 1)
        )

        result = await TestModel.objects.alatest_safe("dob")

        assert isinstance(result, IOSuccess)
        assert unsafe_perform_io(result).unwrap() == obj2

    async def test_alatest_safe_failure(self):
        result = await TestModel.objects.alatest_safe("dob")

        assert isinstance(result, IOFailure)


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
class TestAsyncCreateMethods:
    async def test_acreate_safe_success(self):
        result = await TestModel.objects.acreate_safe(
            name="async_create", dob=date(2020, 1, 1)
        )

        assert isinstance(result, IOSuccess)
        obj = unsafe_perform_io(result).unwrap()
        assert obj.name == "async_create"

    async def test_acreate_safe_failure(self):
        await TestModel.objects.acreate(name="duplicate_async", dob=date(2020, 1, 1))
        result = await TestModel.objects.acreate_safe(
            name="duplicate_async", dob=date(2021, 1, 1)
        )

        assert isinstance(result, IOFailure)
        assert isinstance(unsafe_perform_io(result).failure(), IntegrityError)


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
class TestAsyncGetOrCreateMethods:
    async def test_aget_or_create_safe_get(self):
        existing = await TestModel.objects.acreate(
            name="existing_async", dob=date(2020, 1, 1)
        )
        result = await TestModel.objects.aget_or_create_safe(
            name="existing_async", defaults={"dob": date(2021, 1, 1)}
        )

        assert isinstance(result, IOSuccess)
        obj, created = unsafe_perform_io(result).unwrap()
        assert obj == existing
        assert created is False

    async def test_aget_or_create_safe_create(self):
        result = await TestModel.objects.aget_or_create_safe(
            name="new_async", defaults={"dob": date(2020, 1, 1)}
        )

        assert isinstance(result, IOSuccess)
        obj, created = unsafe_perform_io(result).unwrap()
        assert obj.name == "new_async"
        assert created is True


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
class TestAsyncUpdateOrCreateMethods:
    async def test_aupdate_or_create_safe_update(self):
        existing = await TestModel.objects.acreate(
            name="update_me_async", dob=date(2020, 1, 1)
        )
        result = await TestModel.objects.aupdate_or_create_safe(
            name="update_me_async", defaults={"dob": date(2021, 1, 1)}
        )

        assert isinstance(result, IOSuccess)
        obj, created = unsafe_perform_io(result).unwrap()
        assert obj.id == existing.id
        assert obj.dob == date(2021, 1, 1)
        assert created is False

    async def test_aupdate_or_create_safe_create(self):
        result = await TestModel.objects.aupdate_or_create_safe(
            name="create_new_async", defaults={"dob": date(2020, 1, 1)}
        )

        assert isinstance(result, IOSuccess)
        obj, created = unsafe_perform_io(result).unwrap()
        assert obj.name == "create_new_async"
        assert created is True


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
class TestAsyncDeleteMethods:
    async def test_adelete_safe_success(self):
        await TestModel.objects.acreate(name="delete1_async", dob=date(2020, 1, 1))
        await TestModel.objects.acreate(name="delete2_async", dob=date(2021, 1, 1))

        result = await TestModel.objects.filter(name="delete1_async").adelete_safe()

        assert isinstance(result, IOSuccess)
        deleted_count, _ = unsafe_perform_io(result).unwrap()
        assert deleted_count == 1


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
class TestAsyncBulkCreateMethods:
    async def test_abulk_create_safe_success(self):
        objects = [
            TestModel(name="bulk1_async", dob=date(2020, 1, 1)),
            TestModel(name="bulk2_async", dob=date(2021, 1, 1)),
            TestModel(name="bulk3_async", dob=date(2022, 1, 1)),
        ]

        result = await TestModel.objects.abulk_create_safe(objects)

        assert isinstance(result, IOSuccess)
        created = unsafe_perform_io(result).unwrap()
        assert len(created) == 3

    async def test_abulk_create_safe_failure(self):
        await TestModel.objects.acreate(name="bulk1_fail_async", dob=date(2020, 1, 1))
        objects = [
            TestModel(name="bulk1_fail_async", dob=date(2020, 1, 1)),  # Duplicate
            TestModel(name="bulk2_fail_async", dob=date(2021, 1, 1)),
        ]

        result = await TestModel.objects.abulk_create_safe(objects)

        assert isinstance(result, IOFailure)
        assert isinstance(unsafe_perform_io(result).failure(), IntegrityError)
