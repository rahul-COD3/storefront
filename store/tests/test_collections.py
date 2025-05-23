from store.models import Collection
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
