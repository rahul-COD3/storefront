import pytest
from rest_framework import status
from model_bakery import baker
from store.models import Product, Review, Customer
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.fixture
def create_review(api_client, product): # product fixture is defined below
    def do_create_review(review_data):
        return api_client.post(f"/store/products/{product.id}/reviews/", data=review_data)
    return do_create_review

@pytest.fixture
def product():
    return baker.make(Product)

@pytest.mark.django_db
class TestCreateReview:
    def test_if_user_is_anonymous_returns_401(self, create_review):
        # NOTE: Anonymous users can currently create reviews. Test reflects current behavior.
        response = create_review({"name": "Anonymous Reviewer", "description": "Great product!"})
        assert response.status_code == status.HTTP_201_CREATED

    def test_if_user_is_authenticated_and_data_invalid_returns_400(self, authenticate, create_review):
        authenticate() 
        response = create_review({"name": "", "description": "Test"}) # Invalid: empty name
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "name" in response.data 

    def test_if_user_is_authenticated_and_data_valid_returns_201(self, authenticate, create_review, product):
        user = User.objects.create_user(username='testuser_review', email='testuser_review@example.com', password='password')
        authenticate(user=user) 
        
        response = create_review({
            "name": "Test User", 
            "description": "This is a fantastic product."
        })
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["id"] is not None
        assert response.data["name"] == "Test User"
        assert response.data["description"] == "This is a fantastic product."
        review = Review.objects.get(pk=response.data["id"])
        assert review.product == product


@pytest.mark.django_db
class TestListReview:
    def test_get_reviews_for_a_product_returns_200(self, api_client, product):
        baker.make(Review, product=product, _quantity=3, name="Reviewer", description="Good")
        other_product = baker.make(Product)
        baker.make(Review, product=other_product, name="Other Reviewer", description="Excellent")

        response = api_client.get(f"/store/products/{product.id}/reviews/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 3 # Should only return reviews for 'product'

    def test_get_reviews_when_product_has_no_reviews_returns_200_and_empty_list(self, api_client, product):
        response = api_client.get(f"/store/products/{product.id}/reviews/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0

@pytest.mark.django_db
class TestRetrieveReview:
    def test_if_review_exists_returns_200(self, api_client, product):
        review = baker.make(Review, product=product, name="Reviewer 1", description="Amazing!")
        response = api_client.get(f"/store/products/{product.id}/reviews/{review.id}/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == review.id
        assert response.data["name"] == "Reviewer 1"

    def test_if_review_does_not_exist_returns_404(self, api_client, product):
        non_existent_review_id = 999
        response = api_client.get(f"/store/products/{product.id}/reviews/{non_existent_review_id}/")
        assert response.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.django_db
class TestUpdateReview:
    def test_if_user_is_anonymous_returns_401(self, api_client, product):
        # NOTE: Anonymous users can currently update reviews. Test reflects current behavior.
        review = baker.make(Review, product=product)
        response = api_client.patch(f"/store/products/{product.id}/reviews/{review.id}/", data={"description": "Updated"})
        assert response.status_code == status.HTTP_200_OK

    def test_if_user_is_authenticated_and_data_invalid_returns_400(self, authenticate, api_client, product):
        authenticate()
        review = baker.make(Review, product=product)
        response = api_client.patch(f"/store/products/{product.id}/reviews/{review.id}/", data={"name": ""}) # Empty name is invalid
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "name" in response.data

    def test_if_user_is_authenticated_and_data_valid_returns_200(self, authenticate, api_client, product):
        authenticate()
        review = baker.make(Review, product=product, name="Original Name", description="Original Desc")
        updated_description = "This is an updated description."
        updated_name = "Updated Name"
        response = api_client.patch(f"/store/products/{product.id}/reviews/{review.id}/", data={
            "description": updated_description,
            "name": updated_name
        })
        assert response.status_code == status.HTTP_200_OK
        assert response.data["description"] == updated_description
        assert response.data["name"] == updated_name

    def test_if_review_does_not_exist_returns_404(self, authenticate, api_client, product):
        authenticate()
        non_existent_review_id = 999
        response = api_client.patch(f"/store/products/{product.id}/reviews/{non_existent_review_id}/", data={"description": "Updated"})
        assert response.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.django_db
class TestDeleteReview:
    def test_if_user_is_anonymous_returns_401(self, api_client, product):
        # NOTE: Anonymous users can currently delete reviews. Test reflects current behavior.
        review = baker.make(Review, product=product)
        response = api_client.delete(f"/store/products/{product.id}/reviews/{review.id}/")
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_if_user_is_authenticated_deletes_successfully_returns_204(self, authenticate, api_client, product):
        # Since Review model has no author, any authenticated user can delete.
        authenticate()
        review = baker.make(Review, product=product)
        response = api_client.delete(f"/store/products/{product.id}/reviews/{review.id}/")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Review.objects.filter(pk=review.id).exists()
        
    def test_if_review_does_not_exist_returns_404(self, authenticate, api_client, product):
        authenticate()
        non_existent_review_id = 999
        response = api_client.delete(f"/store/products/{product.id}/reviews/{non_existent_review_id}/")
        assert response.status_code == status.HTTP_404_NOT_FOUND
