from store.models import Collection, Product, OrderItem, Customer, Order
from rest_framework import status
from model_bakery import baker
import pytest
from django.contrib.auth import get_user_model

User = get_user_model()

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


@pytest.mark.django_db
class TestUpdateProduct:
    def test_if_user_is_anonymous_returns_401(self, api_client):
        product = baker.make(Product)
        response = api_client.patch(f"/store/products/{product.id}/", data={"title": "Test"})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_not_admin_returns_403(self, authenticate, api_client):
        authenticate()
        product = baker.make(Product)
        response = api_client.patch(f"/store/products/{product.id}/", data={"title": "Test"})

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_data_is_invalid_returns_400(self, authenticate, api_client):
        authenticate(is_staff=True)
        product = baker.make(Product)
        response = api_client.patch(f"/store/products/{product.id}/", data={"title": ""})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["title"] is not None

    def test_if_data_is_valid_returns_200(self, authenticate, api_client):
        authenticate(is_staff=True)
        collection = baker.make(Collection)
        product = baker.make(Product, collection=collection)

        response = api_client.patch(
            f"/store/products/{product.id}/",
            data={
                "title": "Test",
                "slug": "test",
                "unit_price": 10.0,
                "inventory": 10,
                "collection": collection.id,
            },
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == product.id
        assert response.data["title"] == "Test"


@pytest.mark.django_db
class TestDeleteProduct:
    def test_if_user_is_anonymous_returns_401(self, api_client):
        product = baker.make(Product)
        response = api_client.delete(f"/store/products/{product.id}/")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_not_admin_returns_403(self, authenticate, api_client):
        authenticate()
        product = baker.make(Product)
        response = api_client.delete(f"/store/products/{product.id}/")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_user_is_admin_returns_204(self, authenticate, api_client):
        authenticate(is_staff=True)
        product = baker.make(Product)
        response = api_client.delete(f"/store/products/{product.id}/")

        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_if_product_associated_with_order_item_returns_405(
        self, authenticate, api_client
    ):
        # Authenticate an admin user for the delete operation
        admin_user = User.objects.create_user(username='test_admin_for_delete', email='admin_for_delete@example.com', password='password', is_staff=True)
        api_client.force_authenticate(user=admin_user)

        # Create a separate user and customer for the order
        customer_user = User.objects.create_user(username='customer_for_order', email='customer_for_order@example.com', password='password')
        # Customer is created automatically by a signal, so fetch it.
        customer = Customer.objects.get(user=customer_user)
        
        product = baker.make(Product)
        order = baker.make(Order, customer=customer)
        baker.make(OrderItem, product=product, order=order)

        response = api_client.delete(f"/store/products/{product.id}/")

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
        # Ensure the error message is as expected (this might need adjustment based on actual API response)
        # For now, checking the status code is the primary goal based on the problem description.
        # assert response.data["error"] == "Product cannot be deleted because it is associated with an order item."
        # The previous run's assertion on response.data["error"] might be too specific if the actual error message differs.
        # Let's keep it if it was confirmed to be correct. The prompt asks to ensure tests pass.
        # The original test had this:
        assert response.data["error"] == "Product cannot be deleted because it is associated with an order item."
