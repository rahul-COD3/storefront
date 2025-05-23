import pytest
from uuid import UUID
from rest_framework import status
from model_bakery import baker
from store.models import Cart, Product, CartItem

# No User model needed here as Cart operations are anonymous as per requirements.

@pytest.mark.django_db
class TestCreateCart:
    def test_create_cart_returns_201(self, api_client):
        response = api_client.post("/store/carts/")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['id'] is not None
        # Verify it's a valid UUID
        try:
            UUID(response.data['id'], version=4)
        except ValueError:
            pytest.fail("ID is not a valid UUID4")
        # Check if cart items list is present and empty by default
        assert "items" in response.data
        assert response.data["items"] == []


@pytest.mark.django_db
class TestRetrieveCart:
    def test_retrieve_existing_cart_returns_200(self, api_client):
        cart = baker.make(Cart)
        # Optionally add an item to test prefetch_related in actual viewset (though serializer handles this)
        product = baker.make(Product)
        baker.make(CartItem, cart=cart, product=product, quantity=1)

        response = api_client.get(f"/store/carts/{cart.id}/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == str(cart.id) # Cart ID is UUID, ensure string comparison if needed
        assert len(response.data['items']) == 1 # Assuming CartSerializer includes items

    def test_retrieve_non_existent_cart_returns_404(self, api_client):
        non_existent_cart_id = "a1b2c3d4-e5f6-7788-9900-aabbccddeeff" # Example UUID
        response = api_client.get(f"/store/carts/{non_existent_cart_id}/")
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestDeleteCart:
    def test_delete_existing_cart_returns_204(self, api_client):
        cart = baker.make(Cart)
        response = api_client.delete(f"/store/carts/{cart.id}/")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Cart.objects.filter(pk=cart.id).exists()

    def test_delete_non_existent_cart_returns_404(self, api_client):
        non_existent_cart_id = "a1b2c3d4-e5f6-7788-9900-aabbccddeeff"
        response = api_client.delete(f"/store/carts/{non_existent_cart_id}/")
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestListCart: # Renamed from TestListCarts
    def test_list_carts_returns_405(self, api_client):
        response = api_client.get("/store/carts/")
        # Based on GenericViewSet not including ListModelMixin
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
        # Or could be 404 if router doesn't register it at all for GET on the base.
        # However, DRF typically registers the base for GET (retrieve) and POST (create)
        # but if list is not supported, it's 405.
        # If the route for list is not defined at all, it could be 404.
        # Given the ViewSet structure, 405 is the more common expectation.
        # Check actual API behavior if this fails.
        # The viewset uses CreateModelMixin, RetrieveModelMixin, DestroyModelMixin.
        # The router usually creates routes for:
        # POST /store/carts/ (create)
        # GET /store/carts/{pk}/ (retrieve)
        # PUT /store/carts/{pk}/ (update, if UpdateModelMixin)
        # PATCH /store/carts/{pk}/ (partial_update, if UpdateModelMixin)
        # DELETE /store/carts/{pk}/ (destroy)
        # A GET to /store/carts/ (list) would only be there if ListModelMixin is present.
        # So, a 405 is expected if the route /store/carts/ exists but GET (for list) is not supported.
        # If /store/carts/ itself is not registered for GET at all (e.g. if only specific actions were routed), it could be 404.
        # DefaultRouter registers list routes.
        # The prompt doesn't specify the router, but DefaultRouter is common.
        # If DefaultRouter is used with this ViewSet, it will try to generate a list route.
        # If the method is not implemented, then 405.
        # If the route itself is not generated (e.g. custom router or specific route registration), then 404.
        # Let's stick to 405 as the most likely DRF default for a disallowed method on a known prefix.
        # If the viewset was registered with a router that doesn't create 'list' routes for viewsets
        # not inheriting ListModelMixin, then the URL itself might not exist, leading to 404 from Django's URL resolver.
        # Given the previous tests, the router seems to be DefaultRouter or SimpleRouter.
        # DefaultRouter *will* create a list route. So 405 is the correct expectation.
