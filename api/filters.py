import django_filters
from django.db.models import Q
from patients.models import Patient

class PatientFilter(django_filters.FilterSet):
    # Map FHIR 'family' and 'given' to your Django name fields
    family = django_filters.CharFilter(field_name="last_name", lookup_expr='icontains')
    given = django_filters.CharFilter(field_name="first_name", lookup_expr='icontains')
    
    # Custom methods to handle FHIR-specific formatting
    gender = django_filters.CharFilter(method='filter_gender')
    identifier = django_filters.CharFilter(method='filter_identifier')

    class Meta:
        model = Patient
        fields = ['family', 'given', 'gender', 'identifier']

    def filter_gender(self, queryset, name, value):
        # FHIR uses lowercase ('male'), but your Django model uses Title Case ('Male')
        return queryset.filter(gender__iexact=value)

    def filter_identifier(self, queryset, name, value):
        # FHIR identifiers are often passed as 'system|value'. 
        # We split it and search by the value against your national_id or oph_id.
        search_value = value.split('|')[-1]
        return queryset.filter(
            Q(national_id=search_value) | Q(oph_id=search_value)
        )