"""
A diameter credit control application sample, which establishes connection to
a peer and sends a single credit control EVENT request, with additional SMS
information present and then exits.
"""
import datetime
import logging

from diameter.message.commands.credit_control import CreditControlRequest
from diameter.message.commands.credit_control import RequestedServiceUnit
from diameter.message.commands.credit_control import ServiceInformation
from diameter.message.commands.credit_control import SmsInformation
from diameter.message.commands.credit_control import RecipientInfo
from diameter.message.commands.credit_control import RecipientAddress
from diameter.message.constants import *
from diameter.node import Node
from diameter.node.application import SimpleThreadingApplication

logging.basicConfig(format="%(asctime)s %(name)s %(levelname)s %(message)s")
# this shows a human-readable message dump in the logs
logging.getLogger("diameter.peer.msg").setLevel(logging.DEBUG)


# Configure our client node
node = Node(
    "smsgw.gy", "testrealm.local",
    vendor_ids=[VENDOR_ETSI, VENDOR_TGPP, VENDOR_TGPP2])
# Add the destination peer
ocs_cfg = node.add_peer(
    "aaa://ocs.gy", "testrealm.local",
    ip_addresses=["10.0.0.50"], is_persistent=True)
node.start()


# Configure our client application
client = SimpleThreadingApplication(
    APP_DIAMETER_CREDIT_CONTROL_APPLICATION,
    is_auth_application=True)
# Add application for `ocs.gy` peer
node.add_application(client, [ocs_cfg])


# Construct a credit control request
ccr = CreditControlRequest()

# These are required:
ccr.session_id = client.node.session_generator.next_id()
ccr.origin_host = client.node.origin_host.encode()
ccr.origin_realm = client.node.realm_name.encode()
ccr.destination_realm = client.node.realm_name.encode()
ccr.auth_application_id = client.application_id
ccr.service_context_id = "32274@3gpp.org"
ccr.cc_request_type = E_CC_REQUEST_TYPE_EVENT_REQUEST
ccr.cc_request_number = 1

# These are usually wanted by charging servers:
ccr.user_name = "diameter"
ccr.event_timestamp = datetime.datetime.now()
ccr.requested_action = E_REQUESTED_ACTION_DIRECT_DEBITING

ccr.add_subscription_id(
    subscription_id_type=E_SUBSCRIPTION_ID_TYPE_END_USER_E164,
    subscription_id_data="41780000001")
ccr.add_multiple_services_credit_control(
    requested_service_unit=RequestedServiceUnit(cc_service_specific_units=1),
    service_identifier=1)

# Adds the following 3GPP vendor-specific AVP structure at the end, which
# contains the SMS type and recipient. Looks like:
#
#   Service-Information <Code: 0x369, Flags: 0xc0 (VM-), Length: 120, Vnd: TGPP>
#     SMS-Information <Code: 0x7d0, Flags: 0x80 (V--), Length: 108, Vnd: TGPP>
#       Data-Coding-Scheme <Code: 0x7d1, Flags: 0x80 (V--), Length: 16, Vnd: TGPP, Val: 8>
#       SM-Message-Type <Code: 0x7d7, Flags: 0x80 (V--), Length: 16, Vnd: TGPP, Val: 0>
#       Recipient-Info <Code: 0x7ea, Flags: 0x80 (V--), Length: 64, Vnd: TGPP>
#         Recipient-Address <Code: 0x4b1, Flags: 0x80 (V--), Length: 52, Vnd: TGPP>
#           Address-Type <Code: 0x383, Flags: 0xc0 (VM-), Length: 16, Vnd: TGPP, Val: 1>
#           Address-Data <Code: 0x381, Flags: 0xc0 (VM-), Length: 23, Vnd: TGPP, Val: 41780000001>
#
# Actual content wanted by the OCS on the receiving end may vary depending on
# the vendor and their implementation.
#
# Note that `RecipientInfo` and `RecipientAddress` are wrapped in lists, as the
# specification allows more than one recipient.
ccr.service_information = ServiceInformation(
    sms_information=SmsInformation(
        data_coding_scheme=8,
        sm_message_type=E_SM_MESSAGE_TYPE_SUBMISSION,
        recipient_info=[RecipientInfo(
            recipient_address=[RecipientAddress(
                address_type=E_ADDRESS_TYPE_MSISDN,
                address_data="41780000002"
            )]
        )]
    )
)

# Wait for CER/CEA to complete
client.wait_for_ready()
cca = client.send_request(ccr, timeout=5)

# Should print 2001, if all goes well
print(cca.result_code)

# Disconnect from peer and exit
node.stop()
