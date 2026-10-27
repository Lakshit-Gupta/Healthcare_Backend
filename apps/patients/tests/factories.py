"""Patient test factories."""

import datetime

import factory

from apps.accounts.tests.factories import UserFactory
from apps.patients.models import Patient


class PatientFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Patient

    created_by = factory.SubFactory(UserFactory)
    name = factory.Faker("name")
    date_of_birth = factory.LazyFunction(lambda: datetime.date(1990, 1, 15))
    phone = factory.Faker("numerify", text="##########")
    email = factory.Faker("email")
