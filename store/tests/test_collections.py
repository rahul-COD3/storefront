from store.models import Collection, Product # Added Product
from rest_framework import status
from model_bakery import baker
import pytest


@pytest.fixture
def create_collection(api_client):
    def do_create_collection(collection):
        return api_client.post("/store/collections/", data=collection)

    return do_create_collection


@pytest.mark.django_db
class TestCreateCollection:
    def test_if_user_is_anonymous_returns_401(self, create_collection):

        response = create_collection({"title": "Test"})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_not_admin_returns_403(self, authenticate, create_collection):
        authenticate()

        response = create_collection({"title": "Test"})

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_check_if_data_is_invalid_returns_400(
        self, authenticate, create_collection
    ):
        authenticate(is_staff=True)

        response = create_collection({"title": ""})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["title"] is not None

    def test_check_if_data_is_valid_returns_201(self, authenticate, create_collection):
        authenticate(is_staff=True)

        response = create_collection({"title": "Test"})

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["id"] is not None


@pytest.mark.django_db
class TestRetrieveCollection:
    def test_if_collection_exists_returns_200(self, api_client):
        collections = baker.make(Collection, _quantity=5)

        response = api_client.get(f"/store/collections/{collections[0].id}/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data == {
            "id": collections[0].id,
            "title": collections[0].title,
            "products_count": 0,
        }

    def test_if_get_all_collections_returns_200(self, api_client):
        baker.make(Collection, _quantity=5)

        response = api_client.get("/store/collections/")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 5


@pytest.mark.django_db
class TestUpdateCollection:
    def test_if_user_is_anonymous_returns_401(self, api_client):
        collection = baker.make(Collection)
        response = api_client.patch(f"/store/collections/{collection.id}/", data={"title": "Test Update"})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_not_admin_returns_403(self, authenticate, api_client):
        authenticate()
        collection = baker.make(Collection)
        response = api_client.patch(f"/store/collections/{collection.id}/", data={"title": "Test Update"})
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_data_is_invalid_returns_400(self, authenticate, api_client):
        authenticate(is_staff=True)
        collection = baker.make(Collection)
        response = api_client.patch(f"/store/collections/{collection.id}/", data={"title": ""})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["title"] is not None

    def test_if_data_is_valid_returns_200(self, authenticate, api_client):
        authenticate(is_staff=True)
        collection = baker.make(Collection)
        response = api_client.patch(f"/store/collections/{collection.id}/", data={"title": "Test Update"})
        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == collection.id
        assert response.data["title"] == "Test Update"


@pytest.mark.django_db
class TestDeleteCollection:
    def test_if_user_is_anonymous_returns_401(self, api_client):
        collection = baker.make(Collection)
        response = api_client.delete(f"/store/collections/{collection.id}/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_not_admin_returns_403(self, authenticate, api_client):
        authenticate()
        collection = baker.make(Collection)
        response = api_client.delete(f"/store/collections/{collection.id}/")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_user_is_admin_and_collection_empty_returns_204(self, authenticate, api_client):
        authenticate(is_staff=True)
        collection = baker.make(Collection)
        response = api_client.delete(f"/store/collections/{collection.id}/")
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_if_collection_has_products_returns_405(self, authenticate, api_client):
        authenticate(is_staff=True)
        collection = baker.make(Collection)
        baker.make(Product, collection=collection, _quantity=3)
        response = api_client.delete(f"/store/collections/{collection.id}/")
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
        # Based on the ProductViewSet, the error detail is usually a list.
        # Assuming a similar structure for CollectionViewSet:
        # Error message from CollectionViewSet's destroy method:
        # return Response({'error': 'Collection cannot be deleted because it includes one or more products.'},
        # status=status.HTTP_405_METHOD_NOT_ALLOWED)
        assert response.data["error"] == "Collection cannot be deleted because it includes one or more products."
