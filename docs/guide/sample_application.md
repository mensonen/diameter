---
shallow_toc: 2
---
# A sample application

This section goes through the `"examples/credit_control_sms_client.py"` file,
which demonstrates how to build a diameter client that performs a single SMS
charging request and then disconnects and exits.


## Setting up logging

All parts of the diameter stack use logging extensively. For the purposes of
this example, the logs will be dumped in the console.

```python
import logging

logging.basicConfig(format="%(asctime)s %(name)s %(levelname)s %(message)s")
# this shows a human-readable message dump in the logs
logging.getLogger("diameter.peer.msg").setLevel(logging.DEBUG)
```

## Creating a diameter node

A node represents our own peer and is required for the connectivity to exist.
The node will be configured with one remote peer, which is the destination of
our charging request.

```python
from diameter.message.constants import *
from diameter.node import Node

# Configure our client node
node = Node(
    "smsgw.gy", "testrealm.local",
    vendor_ids=[VENDOR_ETSI, VENDOR_TGPP, VENDOR_TGPP2])
# Add the destination peer
ocs_cfg = node.add_peer(
    "aaa://ocs.gy", "testrealm.local",
    ip_addresses=["10.0.0.50"], is_persistent=True)
node.start()
```

## Creating the charging application

As we are going to act only as a client, our application can be as simple as 
possible. An instance of `SimpleThreadingApplication` with no callback function
to receive messages is sufficient.

```python
from diameter.message.constants import *
from diameter.node.application import SimpleThreadingApplication

# Configure our client application. Credit Control Applications advertise their
# application ID in auth-application-id.
client = SimpleThreadingApplication(
    APP_DIAMETER_CREDIT_CONTROL_APPLICATION,
    is_auth_application=True)
# Add application for `ocs.gy` peer configured above
node.add_application(client, [ocs_cfg])
```

If we were to act as a server and also expect incoming requests, a callback 
function should be passed for the `SimpleThreadingApplication` constructor.


## Constructing a charging request

The charging request will be an instance of `CreditControlRequest`. The header
values, e.g. the hop-by-hop identifier and the application ID will be set 
automatically by the application as the message is submitted, but everything 
else must be set manually.

This example uses multiple services credit control to specify the requested
units, which is a common approach. An alternative would be to provide the 
requested units directly as a value for the `ccr.requested_service_unit` 
attribute.

The example also appends a 3GGP-specified AVP structure at the end, containing 
3GPP identifiers for an SMS submission, in our case the recipient address,
the message data coding scheme and the type of the short message being sent.

```python
import datetime

from diameter.message.commands.credit_control import CreditControlRequest
from diameter.message.commands.credit_control import RequestedServiceUnit
from diameter.message.commands.credit_control import ServiceInformation
from diameter.message.commands.credit_control import SmsInformation
from diameter.message.commands.credit_control import RecipientInfo
from diameter.message.commands.credit_control import RecipientAddress
from diameter.message.constants import *

# Construct a credit control request
ccr = CreditControlRequest()

# These are required:
ccr.session_id = client.node.session_generator.next_id()
ccr.origin_host = client.node.origin_host.encode()
ccr.origin_realm = client.node.realm_name.encode()
ccr.destination_realm = client.node.realm_name.encode()
ccr.auth_application_id = client.application_id
ccr.service_context_id = "32274@3gpp.org"  # SMS
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
```

## Sending the message

The constructed message will be sent through the application. Calling 
`wait_for_ready` before sending the first message is recommended, as our 
destination peer will not accept any messages until the capabilities exchange
procedure has been completed in the background. `wait_for_ready` will also 
block if the remote peer has gone away.

When sending a request through an application, the application will block 
until a given timeout (default 30 seconds) has passed, waiting for an answer to
arrive through the peer. If an answer is received, it is returned, otherwise an
exception is raised.

As we are only going to send one single message, the noed can be stopped 
afterwards, which will cleanly disconnect from the remote peer.

```python
# Wait for CER/CEA to complete
client.wait_for_ready()
cca = client.send_request(ccr, timeout=5)

# Should print 2001, if all goes well
print(cca.result_code)

# Disconnect from peer and exit
node.stop()
```

---

### The complete script

```python
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
# this silences periodic dumping of peer statistics
logging.getLogger("diameter.stats").setLevel(logging.INFO)


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
```
