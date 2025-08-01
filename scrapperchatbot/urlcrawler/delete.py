import requests
import json

APIKEY = "h4dp5mlg44dslddh467eoe4jc1"   # Your API KEY
EMAIL = "info@findpetgps.com"  # Your API EMAIL
DOMAIN = "findcar"  # Your DOMAIN


# check
BASE_URL = "https://" + DOMAIN + ".agilecrm.com/dev/api/"

def check_email_exist(email):
    url = BASE_URL + "contacts/search/email"
    print(url)
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded',
    }

    data = "email_ids=[%s]" % email
    print(data)
    response = requests.post(
        url,
        data=data,
        headers=headers,
        auth=(EMAIL, APIKEY)
    )

    if response.status_code == 200:
        result = response.json()
        print(result)
        if result[0] != None:
            for contact in result:
                for prop in contact['properties']:
                    if prop['name'] == 'first_name':
                        first_name = prop['value']
                    elif prop['name'] == 'last_name':
                        last_name = prop['value']
                    elif prop['name'] == 'email':
                        Email = prop['value']
            if email==Email:
                print("Name:", first_name, last_name)
                print("Email:", Email)
                return True  # Email exists in Agile CRM
        else:
            return False  # Email does not exist in Agile CRM
    else:
        print("Error:", response.text)
        return False
# Example usage:
email_to_check = "andrea.morena71@gmail.com"
exists = check_email_exist(email_to_check)
print("Email exists in Agile CRM:", exists)


#add
#------------------------------------------------
# BASE_URL = "https://" + DOMAIN + ".agilecrm.com/dev/api/"

# def add_contact(contact_data):
#     url = BASE_URL + "contacts"

#     headers = {
#         'Accept': 'application/json',
#         'Content-Type': 'application/json',
#     }

#     response = requests.post(
#         url,
#         data=json.dumps(contact_data),
#         headers=headers,
#         auth=(EMAIL, APIKEY)
#     )

#     if response.status_code == 200:
#         print("Contact added successfully.")
#     else:
#         print("Error:", response.text)

# # Example usage:
# new_contact_data = {
#     "star_value": "4",
#     "lead_score": "92",
#     "tags": [
#         "Lead",
#         "Likely Buyer"
#     ],
#     "properties": [
#         {
#             "type": "SYSTEM",
#             "name": "first_name",
#             "value": "Shubham"
#         },
#         {
#             "type": "SYSTEM",
#             "name": "last_name",
#             "value": "Rajpurohit"
#         },
#         {
#             "type": "SYSTEM",
#             "name": "email",
#             "subtype": "work",
#             "value": "shubham@example.com"
#         },
#         {
#             "type": "SYSTEM",
#             "name": "description",
#             "value": "shubham is a great person who helps everyone in coding"
#         }
#     ]
# }


# add_contact(new_contact_data)


# --------------------
#update


# BASE_URL = "https://" + DOMAIN + ".agilecrm.com/dev/api/"

# def update_contact_description(contact_id, description):
#     url = BASE_URL + f"contacts/edit-properties"

#     headers = {
#         'Accept': 'application/json',
#         'Content-Type': 'application/json',
#     }

#     data = {
#         "id": contact_id,
#         "properties": [
#             {
#                 "type": "SYSTEM",
#                 "name": "description",
#                 "value": description
#             }
#         ]
#     }

#     response = requests.put(
#         url,
#         data=json.dumps(data),
#         headers=headers,
#         auth=(EMAIL, APIKEY)
#     )

#     if response.status_code == 200:
#         print("Contact description updated successfully.")
#     else:
#         print("Error:", response.text)

# # Example usage:
# contact_id = "4573841020092416"  # Replace with the ID of the contact
# new_description = "Updated description for Shubham Rajpurohit."

# update_contact_description(contact_id, new_description)


# auto token
# api 