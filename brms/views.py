from django.shortcuts import render
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests
import json

# Create your views here.
def index(request):
    return render(request, 'index.html')


def get_auth_token():
    url = "http://localhost:4040/token?client_id=01e9db70-1304-4aa2-9ebe-4ba5c16a9a34&client_secret=3f6b57be-d391-4295-a32b-6f1f894543b2&grant_type=client_credentials"
    print(f"Request URL: {url}")  # Add this line to print the URL
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(url, headers=headers, verify=False)
        response.raise_for_status()  # Raise an error for failed requests

        token_data = response.json()

        if 'access_token' in token_data:
            print("Token fetched successfully!")
            return token_data['access_token']
        else:
            raise Exception("Failed to retrieve access token: Key 'access_token' not found in response.")

    except requests.exceptions.RequestException as e:
        raise Exception(f"Error fetching auth token: {str(e)}")



class BirthNotificationAPIView(APIView):
    office_location_id = settings.OFFICE_LOCATION_ID
    office_id = settings.OFFICE_ID
    facility_id = settings.FACILITY_ID
    country_code = settings.COUNTRY_CODE
    district_id = settings.DISTRICT_ID
    state_id = settings.STATE_ID

    # Helper function to create the "Composition" entry
    def create_composition_entry(self):
        return {
            "fullUrl": "urn:uuid:37dd8e55-69c0-493d-b1a0-b7462a1d806a",
            "resource": {
                "identifier": {
                    "system": "urn:ietf:rfc:3986",
                    "value": "8f793c5a-3d53-4c9b-898b-1c04759716c6"
                },
                "resourceType": "Composition",
                "status": "final",
                "type": {
                    "coding": [
                        {
                            "system": "http://opencrvs.org/doc-types",
                            "code": "birth-notification"
                        }
                    ],
                    "text": "Birth Notification"
                },
                "class": {
                    "coding": [
                        {
                            "system": "http://opencrvs.org/specs/classes",
                            "code": "crvs-document"
                        }
                    ],
                    "text": "CRVS Document"
                },
                "subject": {
                    "reference": "urn:uuid:760c393e-4dc3-4572-83f6-b70765963ef1"
                },
                "date": "2022-08-14T14:43:47.000Z",
                "title": "Birth Notification",
                "section": [
                    self.create_section("Child details", "child-details", "urn:uuid:760c393e-4dc3-4572-83f6-b70765963ef1"),
                    self.create_section("Mother's details", "mother-details", "urn:uuid:d9d3a8c8-6a47-47a1-be86-0493a4ec55a7")
                ]
            }
        }

    # Helper function to create sections
    def create_section(self, title, code, reference):
        return {
            "title": title,
            "code": {
                "coding": [
                    {
                        "system": "http://opencrvs.org/specs/sections",
                        "code": code
                    }
                ],
                "text": title
            },
            "entry": [
                {
                    "reference": reference
                }
            ]
        }

    # Helper function to create the Task entry
    def create_task_entry(self):
        return {
            "fullUrl": "urn:uuid:8546aaf3-8a60-4150-bc24-ab5579bc0fa2",
            "resource": {
                "resourceType": "Task",
                "status": "draft",
                "intent": "unknown",
                "identifier": [],
                "code": {
                    "coding": [
                        {
                            "system": "http://opencrvs.org/specs/types",
                            "code": "BIRTH"
                        }
                    ]
                },
                "focus": {
                    "reference": "urn:uuid:37dd8e55-69c0-493d-b1a0-b7462a1d806a"
                },
                "extension": [
                    {
                        "url": "http://opencrvs.org/specs/extension/contact-person",
                        "valueString": "MOTHER"
                    },
                    {
                        "url": "http://opencrvs.org/specs/extension/contact-person-phone-number",
                        "valueString": "+260759205190"
                    },
                    {
                        "url": "http://opencrvs.org/specs/extension/contact-person-email",
                        "valueString": "axon@gmail.com"
                    },
                    {
                        "url": "http://opencrvs.org/specs/extension/timeLoggedMS",
                        "valueInteger": 0
                    },
                    {
                        "url": "http://opencrvs.org/specs/extension/in-complete-fields",
                        "valueString": "N/A"
                    },
                    {
                        "url": "http://opencrvs.org/specs/extension/regLastOffice",
                        "valueReference": {
                            "reference": f"Location/{self.office_id}"
                        }
                    },
                    {
                        "url": "http://opencrvs.org/specs/extension/regLastLocation",
                        "valueReference": {
                            "reference": f"Location/{self.office_location_id}"
                        }
                    }                    
                ]
            }
        }

    # Helper function to create the Patient entry
    def create_patient_entry(self, name, gender, birth_date, reference):
        return {
            "fullUrl": reference,
            "resource": {
                "resourceType": "Patient",
                "active": True,
                "name": [
                    {
                        "use": "en",
                        "family": [name['family']],
                        "given": [name['given']]
                    }
                ],
                "gender": gender,
                "birthDate": birth_date,
                "deceasedBoolean": False,
                "multipleBirthBoolean": False
            }
        }

    # Helper function to create the Encounter entry
    def create_encounter_entry(self):
        return {
            "fullUrl": "urn:uuid:7cb1d9cc-ea4b-4046-bea0-38bdf3082f56",
            "resource": {
                "resourceType": "Encounter",
                "status": "finished",
                "location": [
                    {
                        "location": {
                            "reference": f"Location/{self.facility_id}"
                        }
                    }
                ]
            }
        }

    # Main logic for generating payload
    def create_payload(self, token):
        payload = {
            "resourceType": "Bundle",
            "type": "document",
            "meta": {
                "lastUpdated": "2022-08-14T14:43:47.000Z"
            },
            "entry": [
                self.create_composition_entry(),
                self.create_task_entry(),
                self.create_patient_entry({"family": "Min", "given": "Child"}, "male", "2022-06-29", "urn:uuid:760c393e-4dc3-4572-83f6-b70765963ef1"),
                self.create_patient_entry({"family": "Ratke", "given": "Mom"}, "female", "2002-06-29", "urn:uuid:d9d3a8c8-6a47-47a1-be86-0493a4ec55a7"),
                self.create_patient_entry({"family": "Ratke", "given": "Dad"}, "male", "2002-06-29", "urn:uuid:ad1e15bb-51da-449a-8a12-c7dae10728e4"),
                self.create_encounter_entry()
            ]
        }
        return payload

    # POST method to handle requests
    def post(self, request, *args, **kwargs):
        token = get_auth_token()
        if not token:
            return Response({"error": "Token is required"}, status=status.HTTP_400_BAD_REQUEST)
        payload = self.create_payload(token)
        print(json.dumps(payload))
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        }
        response = requests.post('http://localhost:7070/notification', headers=headers, data=json.dumps(payload))
        if response.status_code == 200:
            return Response(response.json(), status=status.HTTP_200_OK)
        else:
            return Response({"error": f"Failed to send notification {response.json()}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

       