import upstox_client
from upstox_client.rest import ApiException
from config import configuration, api_version

api_instance = upstox_client.UserApi(upstox_client.ApiClient(configuration))

try:
    # Get User Fund And Margin
    api_response = api_instance.get_profile(api_version)
    print(api_response)
except ApiException as e:
    print("Exception when calling UserApi->get_user_fund_margin: %s\n" % e)