"""Mapping test factories."""

import factory

from apps.doctors.tests.factories import DoctorFactory
from apps.mappings.models import PatientDoctorMapping
from apps.patients.tests.factories import PatientFactory


class MappingFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PatientDoctorMapping

    patient = factory.SubFactory(PatientFactory)
    doctor = factory.SubFactory(DoctorFactory)
    created_by = factory.LazyAttribute(lambda o: o.patient.created_by)
