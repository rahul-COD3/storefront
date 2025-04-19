from store.models import Collection, Product
from rest_framework import status
from model_bakery import baker
import pytest


@pytest.fixture
def create_product(api_client):
    def do_create_product(product):
        return api_client.post("/store/products/", data=product)

    return do_create_product


@pytest.mark.django_db
class TestCreateProduct:
    def test_if_user_is_anonymous_returns_401(self, create_product):
        response = create_product({"title": "Test"})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_not_admin_returns_403(self, authenticate, create_product):
        authenticate()

        response = create_product({"title": "Test"})

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_check_if_data_is_invalid_returns_400(self, authenticate, create_product):
        authenticate(is_staff=True)

        response = create_product({"title": ""})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["title"] is not None

    def test_check_if_data_is_valid_returns_201(self, authenticate, create_product):
        authenticate(is_staff=True)
        collection = baker.make(Collection)

        response = create_product(
            {
                "title": "Test",
                "slug": "test",
                "unit_price": 10.0,
                "inventory": 10,
                "collection": collection.id,
            }
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["id"] is not None


@pytest.mark.django_db
class TestRetrieveProduct:
    def test_if_product_exists_returns_200(self, api_client):
        products = baker.make(Product, _quantity=5)

        response = api_client.get(f"/store/products/{products[0].id}/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == products[0].id
        assert response.data["unit_price"] == products[0].unit_price

    def test_if_get_all_products_returns_200(self, api_client):
        baker.make(Product, _quantity=5)

        response = api_client.get("/store/products/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 5
