import pytest
from django.urls import reverse

@pytest.mark.django_db
def test_smoke_db():
    """Kiểm tra xem pytest có thể truy cập database không."""
    from django.contrib.auth.models import User
    count = User.objects.count()
    assert count >= 0

def test_smoke_simple():
    """Kiểm tra logic Python cơ bản."""
    assert 1 + 1 == 2
