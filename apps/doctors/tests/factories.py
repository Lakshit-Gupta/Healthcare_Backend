"""Doctor test factories."""

import factory

from apps.accounts.tests.factories import UserFactory
from apps.doctors.models import Doctor


class DoctorFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Doctor

    created_by = factory.SubFactory(UserFactory)
    name = factory.Faker("name")
    specialization = factory.Iterator(
        ["Cardiology", "Neurology", "Orthopedics", "Pediatrics"]
    )
    phone = factory.Faker("numerify", text="##########")
    email = factory.Faker("email")
