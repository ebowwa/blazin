import pytest
import httpx
from fastapi import status
from uuid import uuid4
from server.models.index import PhoneNumberCreate, PhoneNumberUpdate

# URL for your FastAPI app (change if using different base URL)
BASE_URL = "http://127.0.0.1:8000/phone_numbers"

@pytest.mark.asyncio
async def test_create_phone_number_success():
    # Arrange: Create a valid phone number data
    phone_data = {
        "number": "123-456-7890",
        "has_redeem_value": False,
        "number_of_points": 0
    }

    # Act: Send POST request to create a phone number
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URL}/", json=phone_data)

    # Assert: Check status code and response content
    assert response.status_code == status.HTTP_200_OK
    created_phone = response.json()
    assert created_phone["number"] == phone_data["number"]

@pytest.mark.asyncio
async def test_create_phone_number_duplicate():
    # Arrange: Create a duplicate phone number
    phone_data = {
        "number": "123-456-7890",
        "has_redeem_value": False,
        "number_of_points": 0
    }

    # Act: Send POST request to create the same phone number twice
    async with httpx.AsyncClient() as client:
        response_1 = await client.post(f"{BASE_URL}/", json=phone_data)
        response_2 = await client.post(f"{BASE_URL}/", json=phone_data)

    # Assert: The second request should raise a 400 duplicate error
    assert response_2.status_code == status.HTTP_400_BAD_REQUEST
    assert response_2.json()["detail"] == "Phone number already exists."

@pytest.mark.asyncio
async def test_get_all_phone_numbers():
    # Act: Send GET request to retrieve all phone numbers
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/")

    # Assert: Check status code and data structure
    assert response.status_code == status.HTTP_200_OK
    phone_numbers = response.json()
    assert isinstance(phone_numbers, list)

@pytest.mark.asyncio
async def test_get_phone_number_by_id_success():
    # Arrange: Create a phone number and then retrieve it by ID
    phone_data = {
        "number": "987-654-3210",
        "has_redeem_value": False,
        "number_of_points": 0
    }
    async with httpx.AsyncClient() as client:
        create_response = await client.post(f"{BASE_URL}/", json=phone_data)
        created_phone = create_response.json()

    # Act: Send GET request with the phone's ID
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/{created_phone['id']}")

    # Assert: Check the retrieved phone matches the created one
    assert response.status_code == status.HTTP_200_OK
    phone = response.json()
    assert phone["number"] == phone_data["number"]

@pytest.mark.asyncio
async def test_get_phone_number_by_id_not_found():
    # Arrange: Generate a random UUID that does not exist in the database
    random_uuid = str(uuid4())

    # Act: Send GET request to retrieve a non-existing phone number by UUID
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/{random_uuid}")

    # Assert: Check for 404 not found status code
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Phone number not found."

@pytest.mark.asyncio
async def test_search_phone_number_success():
    # Arrange: Create a phone number and then search for it by number
    phone_data = {
        "number": "555-555-5555",
        "has_redeem_value": True,
        "number_of_points": 10
    }
    async with httpx.AsyncClient() as client:
        create_response = await client.post(f"{BASE_URL}/", json=phone_data)

    # Act: Send GET request to search for the phone number
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/search_phone_number/{phone_data['number']}")

    # Assert: The search should return the phone's UUID
    assert response.status_code == status.HTTP_200_OK
    search_result = response.json()
    assert search_result["client_ip"]
    assert search_result["id"]

@pytest.mark.asyncio
async def test_search_phone_number_not_found():
    # Act: Try to search for a non-existing phone number
    non_existing_number = "999-999-9999"
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/search_phone_number/{non_existing_number}")

    # Assert: The search should return a 404 error
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Phone number not found."

@pytest.mark.asyncio
async def test_update_phone_number_success():
    # Arrange: Create a phone number, then update its details
    phone_data = {
        "number": "444-444-4444",
        "has_redeem_value": False,
        "number_of_points": 0
    }
    phone_update = {
        "number_of_points": 50,
        "has_redeem_value": True
    }
    async with httpx.AsyncClient() as client:
        create_response = await client.post(f"{BASE_URL}/", json=phone_data)
        created_phone = create_response.json()

    # Act: Send PUT request to update the phone number
    async with httpx.AsyncClient() as client:
        response = await client.put(f"{BASE_URL}/{created_phone['id']}", json=phone_update)

    # Assert: Check if phone number was updated
    assert response.status_code == status.HTTP_200_OK
    updated_phone = response.json()
    assert updated_phone["number_of_points"] == 50
    assert updated_phone["has_redeem_value"] is True

@pytest.mark.asyncio
async def test_delete_phone_number_success():
    # Arrange: Create a phone number, then delete it
    phone_data = {
        "number": "333-333-3333",
        "has_redeem_value": True,
        "number_of_points": 100
    }
    async with httpx.AsyncClient() as client:
        create_response = await client.post(f"{BASE_URL}/", json=phone_data)
        created_phone = create_response.json()

    # Act: Send DELETE request to remove the phone number
    async with httpx.AsyncClient() as client:
        delete_response = await client.delete(f"{BASE_URL}/{created_phone['id']}")

    # Assert: Check if phone number was deleted
    assert delete_response.status_code == status.HTTP_200_OK
    assert delete_response.json()["detail"] == "Phone number deleted."
