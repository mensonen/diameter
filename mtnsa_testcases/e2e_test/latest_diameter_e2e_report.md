# Diameter E2E Evidence Report

- Scenario: SIM in roaming country, start data session, 2 updates, terminate, validate latest S3 record
- Start Time UTC: 2026-03-30T05:08:06.789356+00:00
- End Time UTC: 2026-03-30T05:11:33.930371+00:00
- Duration Seconds: 207.141015
- Session-Id: d0-nlepg1.mtn.co.za;e2e-data-roaming;1774847286;1
- Granted Total Octets: 512000

## Scenario Details

- Origin-Host: d0-nlepg1.mtn.co.za
- Origin-Realm: mtn.co.za
- Destination-Host: diameter01.joburg.eseye.com
- Destination-Realm: diameter.eseye.com
- Service-Context-Id: 8.32251@3gpp.org
- MSISDN: 279603002227198
- IMSI: 655103704646780
- Expected TGPP-SGSN-MCC-MNC: 23420
- Expected TGPP-RAT-Type: 06

## Validation Results

- eksqan_diameter_gy Events Found: 4
- eksqan_diameter_gy Methods Found: INITIALREQUEST, TERMINATIONREQUEST, UPDATEREQUEST
- toucan_diameter_input_stream Events Found: 4
- toucan_diameter_input_stream Methods Found: INITIALREQUEST, TERMINATIONREQUEST, UPDATEREQUEST

## Latest S3 Record

- Key: 2026/03/30/05/toucan-diameter-delivery-1-2026-03-30-05-08-29-e1b048c4-b115-4103-9ea7-1fd22cab158c.gz
- Last Modified: 2026-03-30 05:09:37+00:00
- Size: 1661
- TCN_sessionId Found: True
- TCN_sessionId Value: d0-nlepg1.mtn.co.za;e2e-data-roaming;1774847286;1
- END_USER_E164 Found: True
- END_USER_E164 Value: 279603002227198
- END_USER_IMSI Found: True
- END_USER_IMSI Value: 655103704646780
- TGPP-SGSN-MCC-MNC Found: True
- TGPP-SGSN-MCC-MNC Value: 23420
- TGPP-RAT-Type Found: True
- TGPP-RAT-Type Value: 06

### S3 Payload

```text
{"time": "2026-03-30T05:08:16.677929363Z", "peer": "mtn-test", "method": "INITIAL_REQUEST", "service_type": "DATA", "decision": {"code": 2001, "reason": "APPROVED_DATA", "validity_time_sec": 1800, "include_final_unit": false, "final_unit_action": 0, "granted_data_octets": 512000, "granted_voice_seconds": 0, "granted_sms_units": 0, "granted_ussd_seconds": 0}, "server_host": "ip-172-30-14-75.eu-west-1.compute.internal", "server_time": "2026-03-30T05:08:16.000000000+0000", "Session-Id": "d0-nlepg1.mtn.co.za;e2e-data-roaming;1774847286;1", "Origin-Host": "d0-nlepg1.mtn.co.za", "Origin-Realm": "mtn.co.za", "Destination-Realm": "diameter.eseye.com", "Auth-Application-Id": 4, "Service-Context-Id": "8.32251@3gpp.org", "CC-Request-Type": "INITIAL_REQUEST", "CC-Request-Number": 0, "Destination-Host": "diameter01.joburg.eseye.com", "TGPP-IMSI": "655103704646780nai.epc.mnc655.mcc10.3gppnetwork.org", "Origin-State-Id": 45, "Event-Timestamp": "2026-03-30T05:08:17Z", "END_USER_E164": "279603002227198", "END_USER_IMSI": "655103704646780", "END_USER_NAI": "655103704646780nai.epc.mnc655.mcc10.3gppnetwork.org", "CC-Total-Octets": 512000, "Rating-Group": 1004, "Multiple-Services-Indicator": "MULTIPLE_SERVICES_SUPPORTED", "IMEISV": "3564871075436638", "TGPP-Charging-Id": "o-`C", "PDN-Connection-Charging-Id": 1865244739, "TGPP-PDP-Type": "Ipv4", "PDP-Address": "10.144.18.3", "QoS-Class-Identifier": "QCI_9", "Priority-Level": 2, "APN-Aggregate-Max-Bitrate-UL": 1500000000, "APN-Aggregate-Max-Bitrate-DL": 1500000000, "Dynamic-Address-Flag": "Dynamic", "SGSN-Address": "41.208.22.222", "GGSN-Address": "196.13.128.128", "Serving-Node-Type": "GTPSGW", "TGPP-IMSI-MCC-MNC": "65510", "TGPP-GGSN-MCC-MNC": "23420", "TGPP-NSAPI": "06", "TGPP-Selection-Mode": "0", "TGPP-Charging-Characteristics": "0400", "TGPP-SGSN-MCC-MNC": "23420", "TGPP-MS-TimeZone": "8000", "TGPP-User-Location-Info": "8232F402000132F40200000001", "TGPP-RAT-Type": "06", "Called-Station-Id": "zsmarttest11", "TCN_id": "01KMYJ9DBKTFW2CMFRDNG71030", "TCN_time": "2026-03-30 05:08:29.171702", "TCN_recordType": "diameter", "TCN_version": "20260303", "TCN_eventTime": "2026-03-30 05:08:17", "TCN_msisdn": "279603002227198", "TCN_imsi": "655103704646780", "TCN_otherParty": "zsmarttest11", "TCN_ipv4": "10.144.18.3", "TCN_sessionId": "d0-nlepg1.mtn.co.za;e2e-data-roaming;1774847286;1", "TCN_packageCategoryId": "7", "TCN_packageItemCategoryId": "105", "TCN_simId": "8927000007638675554", "TCN_packageId": "31889", "TCN_dacctId": "9ce457bc241d11f09087000c29c2aa03", "TCN_iccId": "8927000007638675554", "TCN_portfolioId": "5a959b3803ed11f0918f000c293015c7", "TCN_invoicingEntityId": "70", "TCN_portalId": "3f9add1182783c95e27406df64144f24", "TCN_ratType": "EUTRAN", "TCN_imei": "356487107543661", "TCN_mcc": "234", "TCN_mnc": "20", "TCN_invoicingEntityTitle": "MTNSA", "TCN_parentPortfolioId": "3f9add1182783c95e27406df64144f24", "TCN_currency": "ZAR", "TCN_billingCycle": "202603", "TCN_billingDate": "20260330", "TCN_packageItemIdSource": "packageId", "TCN_packageItemId": "50076"}
{"time": "2026-03-30T05:08:16.894229012Z", "peer": "mtn-test", "method": "UPDATE_REQUEST", "service_type": "DATA", "decision": {"code": 2001, "reason": "APPROVED_DATA", "validity_time_sec": 1800, "include_final_unit": false, "final_unit_action": 0, "granted_data_octets": 512000, "granted_voice_seconds": 0, "granted_sms_units": 0, "granted_ussd_seconds": 0}, "server_host": "ip-172-30-14-75.eu-west-1.compute.internal", "server_time": "2026-03-30T05:08:16.000000000+0000", "Session-Id": "d0-nlepg1.mtn.co.za;e2e-data-roaming;1774847286;1", "Origin-Host": "d0-nlepg1.mtn.co.za", "Origin-Realm": "mtn.co.za", "Destination-Realm": "diameter.eseye.com", "Auth-Application-Id": 4, "Service-Context-Id": "8.32251@3gpp.org", "CC-Request-Type": "UPDATE_REQUEST", "CC-Request-Number": 1, "Destination-Host": "diameter01.joburg.eseye.com", "TGPP-IMSI": "655103704646780nai.epc.mnc655.mcc10.3gppnetwork.org", "Origin-State-Id": 45, "Event-Timestamp": "2026-03-30T05:08:17Z", "END_USER_E164": "279603002227198", "END_USER_IMSI": "655103704646780", "END_USER_NAI": "655103704646780nai.epc.mnc655.mcc10.3gppnetwork.org", "CC-Total-Octets": 512000, "CC-Total-Octets-2": 128000, "Rating-Group": 1004, "Reporting-Reason": "QUOTA_EXHAUSTED", "IMEISV": "3564871075436638", "TGPP-Charging-Id": "o-`C", "PDN-Connection-Charging-Id": 1865244739, "TGPP-PDP-Type": "Ipv4", "PDP-Address": "10.144.18.3", "QoS-Class-Identifier": "QCI_9", "Priority-Level": 2, "APN-Aggregate-Max-Bitrate-UL": 1500000000, "APN-Aggregate-Max-Bitrate-DL": 1500000000, "Dynamic-Address-Flag": "Dynamic", "SGSN-Address": "41.208.22.222", "GGSN-Address": "196.13.128.128", "Serving-Node-Type": "GTPSGW", "TGPP-IMSI-MCC-MNC": "65510", "TGPP-GGSN-MCC-MNC": "23420", "TGPP-NSAPI": "06", "TGPP-Selection-Mode": "0", "TGPP-Charging-Characteristics": "0400", "TGPP-SGSN-MCC-MNC": "23420", "TGPP-MS-TimeZone": "8000", "TGPP-User-Location-Info": "8232F402000132F40200000001", "TGPP-RAT-Type": "06", "Called-Station-Id": "zsmarttest11", "TCN_id": "01KMYJ9DDA5N23P4SJK1WYA7Q8", "TCN_time": "2026-03-30 05:08:29.226036", "TCN_recordType": "diameter", "TCN_version": "20260303", "TCN_eventTime": "2026-03-30 05:08:17", "TCN_msisdn": "279603002227198", "TCN_imsi": "655103704646780", "TCN_otherParty": "zsmarttest11", "TCN_ipv4": "10.144.18.3", "TCN_sessionId": "d0-nlepg1.mtn.co.za;e2e-data-roaming;1774847286;1", "TCN_packageCategoryId": "7", "TCN_packageItemCategoryId": "105", "TCN_simId": "8927000007638675554", "TCN_packageId": "31889", "TCN_dacctId": "9ce457bc241d11f09087000c29c2aa03", "TCN_iccId": "8927000007638675554", "TCN_portfolioId": "5a959b3803ed11f0918f000c293015c7", "TCN_invoicingEntityId": "70", "TCN_portalId": "3f9add1182783c95e27406df64144f24", "TCN_ratType": "EUTRAN", "TCN_imei": "356487107543661", "TCN_mcc": "234", "TCN_mnc": "20", "TCN_invoicingEntityTitle": "MTNSA", "TCN_parentPortfolioId": "3f9add1182783c95e27406df64144f24", "TCN_currency": "ZAR", "TCN_billingCycle": "202603", "TCN_billingDate": "20260330", "TCN_packageItemIdSource": "packageId", "TCN_packageItemId": "50076"}
{"time": "2026-03-30T05:08:19.112242905Z", "peer": "mtn-test", "method": "UPDATE_REQUEST", "service_type": "DATA", "decision": {"code": 2001, "reason": "APPROVED_DATA", "validity_time_sec": 1800, "include_final_unit": false, "final_unit_action": 0, "granted_data_octets": 512000, "granted_voice_seconds": 0, "granted_sms_units": 0, "granted_ussd_seconds": 0}, "server_host": "ip-172-30-14-75.eu-west-1.compute.internal", "server_time": "2026-03-30T05:08:19.000000000+0000", "Session-Id": "d0-nlepg1.mtn.co.za;e2e-data-roaming;1774847286;1", "Origin-Host": "d0-nlepg1.mtn.co.za", "Origin-Realm": "mtn.co.za", "Destination-Realm": "diameter.eseye.com", "Auth-Application-Id": 4, "Service-Context-Id": "8.32251@3gpp.org", "CC-Request-Type": "UPDATE_REQUEST", "CC-Request-Number": 2, "Destination-Host": "diameter01.joburg.eseye.com", "TGPP-IMSI": "655103704646780nai.epc.mnc655.mcc10.3gppnetwork.org", "Origin-State-Id": 45, "Event-Timestamp": "2026-03-30T05:08:19Z", "END_USER_E164": "279603002227198", "END_USER_IMSI": "655103704646780", "END_USER_NAI": "655103704646780nai.epc.mnc655.mcc10.3gppnetwork.org", "CC-Total-Octets": 512000, "CC-Total-Octets-2": 256000, "Rating-Group": 1004, "Reporting-Reason": "QUOTA_EXHAUSTED", "IMEISV": "3564871075436638", "TGPP-Charging-Id": "o-`C", "PDN-Connection-Charging-Id": 1865244739, "TGPP-PDP-Type": "Ipv4", "PDP-Address": "10.144.18.3", "QoS-Class-Identifier": "QCI_9", "Priority-Level": 2, "APN-Aggregate-Max-Bitrate-UL": 1500000000, "APN-Aggregate-Max-Bitrate-DL": 1500000000, "Dynamic-Address-Flag": "Dynamic", "SGSN-Address": "41.208.22.222", "GGSN-Address": "196.13.128.128", "Serving-Node-Type": "GTPSGW", "TGPP-IMSI-MCC-MNC": "65510", "TGPP-GGSN-MCC-MNC": "23420", "TGPP-NSAPI": "06", "TGPP-Selection-Mode": "0", "TGPP-Charging-Characteristics": "0400", "TGPP-SGSN-MCC-MNC": "23420", "TGPP-MS-TimeZone": "8000", "TGPP-User-Location-Info": "8232F402000132F40200000001", "TGPP-RAT-Type": "06", "Called-Station-Id": "zsmarttest11", "TCN_id": "01KMYJ9DE85NZMB5KF6VAK68M0", "TCN_time": "2026-03-30 05:08:29.256402", "TCN_recordType": "diameter", "TCN_version": "20260303", "TCN_eventTime": "2026-03-30 05:08:19", "TCN_msisdn": "279603002227198", "TCN_imsi": "655103704646780", "TCN_otherParty": "zsmarttest11", "TCN_ipv4": "10.144.18.3", "TCN_sessionId": "d0-nlepg1.mtn.co.za;e2e-data-roaming;1774847286;1", "TCN_packageCategoryId": "7", "TCN_packageItemCategoryId": "105", "TCN_simId": "8927000007638675554", "TCN_packageId": "31889", "TCN_dacctId": "9ce457bc241d11f09087000c29c2aa03", "TCN_iccId": "8927000007638675554", "TCN_portfolioId": "5a959b3803ed11f0918f000c293015c7", "TCN_invoicingEntityId": "70", "TCN_portalId": "3f9add1182783c95e27406df64144f24", "TCN_ratType": "EUTRAN", "TCN_imei": "356487107543661", "TCN_mcc": "234", "TCN_mnc": "20", "TCN_invoicingEntityTitle": "MTNSA", "TCN_parentPortfolioId": "3f9add1182783c95e27406df64144f24", "TCN_currency": "ZAR", "TCN_billingCycle": "202603", "TCN_billingDate": "20260330", "TCN_packageItemIdSource": "packageId", "TCN_packageItemId": "50076"}
{"time": "2026-03-30T05:08:21.366616493Z", "peer": "mtn-test", "method": "TERMINATION_REQUEST", "service_type": "DATA", "decision": {"code": 2001, "reason": "APPROVED_DATA", "validity_time_sec": 1800, "include_final_unit": false, "final_unit_action": 0, "granted_data_octets": 512000, "granted_voice_seconds": 0, "granted_sms_units": 0, "granted_ussd_seconds": 0}, "server_host": "ip-172-30-14-75.eu-west-1.compute.internal", "server_time": "2026-03-30T05:08:21.000000000+0000", "Session-Id": "d0-nlepg1.mtn.co.za;e2e-data-roaming;1774847286;1", "Origin-Host": "d0-nlepg1.mtn.co.za", "Origin-Realm": "mtn.co.za", "Destination-Realm": "diameter.eseye.com", "Auth-Application-Id": 4, "Service-Context-Id": "8.32251@3gpp.org", "CC-Request-Type": "TERMINATION_REQUEST", "CC-Request-Number": 3, "Destination-Host": "diameter01.joburg.eseye.com", "TGPP-IMSI": "655103704646780nai.epc.mnc655.mcc10.3gppnetwork.org", "Origin-State-Id": 45, "Event-Timestamp": "2026-03-30T05:08:21Z", "END_USER_E164": "279603002227198", "END_USER_IMSI": "655103704646780", "END_USER_NAI": "655103704646780nai.epc.mnc655.mcc10.3gppnetwork.org", "CC-Total-Octets": 256000, "Rating-Group": 1004, "Reporting-Reason": "FINAL", "IMEISV": "3564871075436638", "TGPP-Charging-Id": "o-`C", "PDN-Connection-Charging-Id": 1865244739, "TGPP-PDP-Type": "Ipv4", "PDP-Address": "10.144.18.3", "QoS-Class-Identifier": "QCI_9", "Priority-Level": 2, "APN-Aggregate-Max-Bitrate-UL": 1500000000, "APN-Aggregate-Max-Bitrate-DL": 1500000000, "Dynamic-Address-Flag": "Dynamic", "SGSN-Address": "41.208.22.222", "GGSN-Address": "196.13.128.128", "Serving-Node-Type": "GTPSGW", "TGPP-IMSI-MCC-MNC": "65510", "TGPP-GGSN-MCC-MNC": "23420", "TGPP-NSAPI": "06", "TGPP-Selection-Mode": "0", "TGPP-Charging-Characteristics": "0400", "TGPP-SGSN-MCC-MNC": "23420", "TGPP-MS-TimeZone": "8000", "TGPP-User-Location-Info": "8232F402000132F40200000001", "TGPP-RAT-Type": "06", "Called-Station-Id": "zsmarttest11", "TCN_id": "01KMYJ9Q3PJRD8WS8A32R0RK93", "TCN_time": "2026-03-30 05:08:39.157981", "TCN_recordType": "diameter", "TCN_version": "20260303", "TCN_eventTime": "2026-03-30 05:08:21", "TCN_msisdn": "279603002227198", "TCN_imsi": "655103704646780", "TCN_otherParty": "zsmarttest11", "TCN_ipv4": "10.144.18.3", "TCN_sessionId": "d0-nlepg1.mtn.co.za;e2e-data-roaming;1774847286;1", "TCN_packageCategoryId": "7", "TCN_packageItemCategoryId": "105", "TCN_simId": "8927000007638675554", "TCN_packageId": "31889", "TCN_dacctId": "9ce457bc241d11f09087000c29c2aa03", "TCN_iccId": "8927000007638675554", "TCN_portfolioId": "5a959b3803ed11f0918f000c293015c7", "TCN_invoicingEntityId": "70", "TCN_portalId": "3f9add1182783c95e27406df64144f24", "TCN_ratType": "EUTRAN", "TCN_imei": "356487107543661", "TCN_mcc": "234", "TCN_mnc": "20", "TCN_invoicingEntityTitle": "MTNSA", "TCN_parentPortfolioId": "3f9add1182783c95e27406df64
```

## Console Log

```text
==============================================================================================================
SCENARIO: SIM in roaming country, start data session, 2 updates, terminate, validate latest S3 record
==============================================================================================================
Server FQDN                 : k8s-diameter-diameter-e188306276-a8c44a5bd1bf993c.elb.eu-west-1.amazonaws.com
Session-Id                  : d0-nlepg1.mtn.co.za;e2e-data-roaming;1774847286;1
Expected ENDUSERE164        : 279603002227198
Expected ENDUSERIMSI        : 655103704646780
Expected TGPP-SGSN-MCC-MNC  : 23420
Expected TGPP-RAT-Type      : 06
S3 Bucket                   : toucan-diameter-qan
AWS Profile                 : senior-qa-role
AWS Region                  : eu-west-1
KINESIS_WAIT_SEC            : 22
S3_WAIT_SEC                 : 18
Resolved k8s-diameter-diameter-e188306276-a8c44a5bd1bf993c.elb.eu-west-1.amazonaws.com to 172.30.14.10
Connecting to k8s-diameter-diameter-e188306276-a8c44a5bd1bf993c.elb.eu-west-1.amazonaws.com:3868 (172.30.14.10)

Sending CER...
--------------------------------------------------------------------------------------------------------------
CEA
--------------------------------------------------------------------------------------------------------------
Result-Code           : 2001
Origin-Host           : 6469616D6574657230312E65736579652E636F6D
Origin-Realm          : 6469616D657465722E65736579652E636F6D
Auth-Application-Id   : [4]
--------------------------------------------------------------------------------------------------------------

STEP 1: Send CCR-I
INFO Sending CCR-I 1044 bytes
--------------------------------------------------------------------------------------------------------------
CCR-I RESPONSE
--------------------------------------------------------------------------------------------------------------
Session-Id            : d0-nlepg1.mtn.co.za;e2e-data-roaming;1774847286;1
CC-Request-Type       : 1
CC-Request-Number     : 0
Result-Code           : 2001
Origin-Host           : 6469616D6574657230312E65736579652E636F6D
Origin-Realm          : 6469616D657465722E65736579652E636F6D
Auth-Application-Id   : 4
--------------------------------------------------------------------------------------------------------------
MSCC[1]
  Rating-Group        : 1004
  Validity-Time       : 1800
  Result-Code         : 2001
  GSU CC-Total-Octets : 512000
  GSU CC-Input-Octets : N/A
  GSU CC-Output-Octets: N/A
CCR-I REQUEST HEX:
01000414c00001100000000469ca05413d24870d000001074000003964302d6e6c657067312e6d746e2e636f2e7a613b6532652d646174612d726f616d696e673b313737343834373238363b31000000000001080000001b64302d6e6c657067312e6d746e2e636f2e7a610000000128000000116d746e2e636f2e7a610000000000011b4000001a6469616d657465722e65736579652e636f6d0000000001024000000c00000004000001cd40000018382e333232353140336770702e6f7267000001a04000000c000000010000019f4000000c0000000000000125000000236469616d6574657230312e6a6f627572672e65736579652e636f6d00000000014000003b3635353130333730343634363738306e61692e6570632e6d6e633635352e6d636331302e336770706e6574776f726b2e6f726700000001164000000c0000002d000000374000000ced7483c1000001bb4000002c000001c24000000c00000000000001bc4000001732373936303330303232323731393800000001bb4000002c000001c24000000c00000001000001bc4000001736353531303337303436343637383000000001bb40000050000001c24000000c00000003000001bc4000003b3635353130333730343634363738306e61692e6570632e6d6e633635352e6d636331302e336770706e6574776f726b2e6f726700000001c84000002c000001b540000018000001a540000010000000000007d000000001b04000000c000003ec000001c74000000c00000001000001ca4000002c000001cb4000000c00000000000001cc400000183335363438373130373534333636333800000369c00001b8000028af0000036ac00001ac000028af00000002c0000010000028af6f2d60430000080280000010000028af6f2d604300000003c0000010000028af00000000000004cb80000012000028af00010a9012030000000003f8c0000058000028af00000404c0000010000028af000000090000040ac000001c000028af00000416c0000010000028af0000000200000411c0000010000028af59682f0000000410c0000010000028af59682f000000080380000010000028af00000001000004cc80000012000028af000129d016de00000000034fc0000012000028af0001c40d80800000000007ff80000010000028af0000000200000008c0000011000028af363535313000000000000009c0000011000028af32333432300000000000000ac000000d000028af060000000000000cc000000d000028af300000000000000dc0000010000028af3034303000000012c0000011000028af323334323000000000000017c000000e000028af8000000000000016c0000019000028af8232f402000132f4020000000100000000000015c000000d000028af060000000000001e400000147a736d617274746573743131
CCR-I RESPONSE HEX:
01000108400001100000000469ca05413d24870d000001074000003964302d6e6c657067312e6d746e2e636f2e7a613b6532652d646174612d726f616d696e673b313737343834373238363b310000000000010c4000000c000007d1000001024000000c00000004000001a04000000c000000010000019f4000000c00000000000001164000000c0000002d000001c840000044000001b04000000c000003ec000001c04000000c000007080000010c4000000c000007d1000001af40000018000001a540000010000000000007d000000001084000001c6469616d6574657230312e65736579652e636f6d000001284000001a6469616d657465722e65736579652e636f6d0000

STEP 2: Send exactly 2 CCR-U

Update 1: used_total_octets=128000
INFO Sending CCR-U[1] 1072 bytes
--------------------------------------------------------------------------------------------------------------
CCR-U[1] RESPONSE
--------------------------------------------------------------------------------------------------------------
Session-Id            : d0-nlepg1.mtn.co.za;e2e-data-roaming;1774847286;1
CC-Request-Type       : 2
CC-Request-Number     : 1
Result-Code           : 2001
Origin-Host           : 6469616D6574657230312E65736579652E636F6D
Origin-Realm          : 6469616D657465722E65736579652E636F6D
Auth-Application-Id   : 4
--------------------------------------------------------------------------------------------------------------
MSCC[1]
  Rating-Group        : 1004
  Validity-Time       : 1800
  Result-Code         : 2001
  GSU CC-Total-Octets : 512000
  GSU CC-Input-Octets : N/A
  GSU CC-Output-Octets: N/A
CCR-U[1] REQUEST HEX:
01000430c00001100000000469ca05413d2487e6000001074000003964302d6e6c657067312e6d746e2e636f2e7a613b6532652d646174612d726f616d696e673b313737343834373238363b31000000000001080000001b64302d6e6c657067312e6d746e2e636f2e7a610000000128000000116d746e2e636f2e7a610000000000011b4000001a6469616d657465722e65736579652e636f6d0000000001024000000c00000004000001cd40000018382e333232353140336770702e6f7267000001a04000000c000000020000019f4000000c0000000100000125000000236469616d6574657230312e6a6f627572672e65736579652e636f6d00000000014000003b3635353130333730343634363738306e61692e6570632e6d6e633635352e6d636331302e336770706e6574776f726b2e6f726700000001164000000c0000002d000000374000000ced7483c1000001bb4000002c000001c24000000c00000000000001bc4000001732373936303330303232323731393800000001bb4000002c000001c24000000c00000001000001bc4000001736353531303337303436343637383000000001bb40000050000001c24000000c00000003000001bc4000003b3635353130333730343634363738306e61692e6570632e6d6e633635352e6d636331302e336770706e6574776f726b2e6f726700000001c840000054000001b540000018000001a540000010000000000007d000000001be40000018000001a540000010000000000001f400000001b04000000c000003ec00000368c0000010000028af00000003000001ca4000002c000001cb4000000c00000000000001cc400000183335363438373130373534333636333800000369c00001b8000028af0000036ac00001ac000028af00000002c0000010000028af6f2d60430000080280000010000028af6f2d604300000003c0000010000028af00000000000004cb80000012000028af00010a9012030000000003f8c0000058000028af00000404c0000010000028af000000090000040ac000001c000028af00000416c0000010000028af0000000200000411c0000010000028af59682f0000000410c0000010000028af59682f000000080380000010000028af00000001000004cc80000012000028af000129d016de00000000034fc0000012000028af0001c40d80800000000007ff80000010000028af0000000200000008c0000011000028af363535313000000000000009c0000011000028af32333432300000000000000ac000000d000028af060000000000000cc000000d000028af300000000000000dc0000010000028af3034303000000012c0000011000028af323334323000000000000017c000000e000028af8000000000000016c0000019000028af8232f402000132f4020000000100000000000015c000000d000028af060000000000001e400000147a736d617274746573743131
CCR-U[1] RESPONSE HEX:
01000108400001100000000469ca05413d2487e6000001074000003964302d6e6c657067312e6d746e2e636f2e7a613b6532652d646174612d726f616d696e673b313737343834373238363b310000000000010c4000000c000007d1000001024000000c00000004000001a04000000c000000020000019f4000000c00000001000001164000000c0000002d000001c840000044000001b04000000c000003ec000001c04000000c000007080000010c4000000c000007d1000001af40000018000001a540000010000000000007d000000001084000001c6469616d6574657230312e65736579652e636f6d000001284000001a6469616d657465722e65736579652e636f6d0000

Update 2: used_total_octets=256000
INFO Sending CCR-U[2] 1072 bytes
--------------------------------------------------------------------------------------------------------------
CCR-U[2] RESPONSE
--------------------------------------------------------------------------------------------------------------
Session-Id            : d0-nlepg1.mtn.co.za;e2e-data-roaming;1774847286;1
CC-Request-Type       : 2
CC-Request-Number     : 2
Result-Code           : 2001
Origin-Host           : 6469616D6574657230312E65736579652E636F6D
Origin-Realm          : 6469616D657465722E65736579652E636F6D
Auth-Application-Id   : 4
--------------------------------------------------------------------------------------------------------------
MSCC[1]
  Rating-Group        : 1004
  Validity-Time       : 1800
  Result-Code         : 2001
  GSU CC-Total-Octets : 512000
  GSU CC-Input-Octets : N/A
  GSU CC-Output-Octets: N/A
CCR-U[2] REQUEST HEX:
01000430c00001100000000469ca05433d24908e000001074000003964302d6e6c657067312e6d746e2e636f2e7a613b6532652d646174612d726f616d696e673b313737343834373238363b31000000000001080000001b64302d6e6c657067312e6d746e2e636f2e7a610000000128000000116d746e2e636f2e7a610000000000011b4000001a6469616d657465722e65736579652e636f6d0000000001024000000c00000004000001cd40000018382e333232353140336770702e6f7267000001a04000000c000000020000019f4000000c0000000200000125000000236469616d6574657230312e6a6f627572672e65736579652e636f6d00000000014000003b3635353130333730343634363738306e61692e6570632e6d6e633635352e6d636331302e336770706e6574776f726b2e6f726700000001164000000c0000002d000000374000000ced7483c3000001bb4000002c000001c24000000c00000000000001bc4000001732373936303330303232323731393800000001bb4000002c000001c24000000c00000001000001bc4000001736353531303337303436343637383000000001bb40000050000001c24000000c00000003000001bc4000003b3635353130333730343634363738306e61692e6570632e6d6e633635352e6d636331302e336770706e6574776f726b2e6f726700000001c840000054000001b540000018000001a540000010000000000007d000000001be40000018000001a540000010000000000003e800000001b04000000c000003ec00000368c0000010000028af00000003000001ca4000002c000001cb4000000c00000000000001cc400000183335363438373130373534333636333800000369c00001b8000028af0000036ac00001ac000028af00000002c0000010000028af6f2d60430000080280000010000028af6f2d604300000003c0000010000028af00000000000004cb80000012000028af00010a9012030000000003f8c0000058000028af00000404c0000010000028af000000090000040ac000001c000028af00000416c0000010000028af0000000200000411c0000010000028af59682f0000000410c0000010000028af59682f000000080380000010000028af00000001000004cc80000012000028af000129d016de00000000034fc0000012000028af0001c40d80800000000007ff80000010000028af0000000200000008c0000011000028af363535313000000000000009c0000011000028af32333432300000000000000ac000000d000028af060000000000000cc000000d000028af300000000000000dc0000010000028af3034303000000012c0000011000028af323334323000000000000017c000000e000028af8000000000000016c0000019000028af8232f402000132f4020000000100000000000015c000000d000028af060000000000001e400000147a736d617274746573743131
CCR-U[2] RESPONSE HEX:
01000108400001100000000469ca05433d24908e000001074000003964302d6e6c657067312e6d746e2e636f2e7a613b6532652d646174612d726f616d696e673b313737343834373238363b310000000000010c4000000c000007d1000001024000000c00000004000001a04000000c000000020000019f4000000c00000002000001164000000c0000002d000001c840000044000001b04000000c000003ec000001c04000000c000007080000010c4000000c000007d1000001af40000018000001a540000010000000000007d000000001084000001c6469616d6574657230312e65736579652e636f6d000001284000001a6469616d657465722e65736579652e636f6d0000

STEP 3: Send CCR-T
INFO Sending CCR-T 1048 bytes
--------------------------------------------------------------------------------------------------------------
CCR-T RESPONSE
--------------------------------------------------------------------------------------------------------------
Session-Id            : d0-nlepg1.mtn.co.za;e2e-data-roaming;1774847286;1
CC-Request-Type       : 3
CC-Request-Number     : 3
Result-Code           : 2001
Origin-Host           : 6469616D6574657230312E65736579652E636F6D
Origin-Realm          : 6469616D657465722E65736579652E636F6D
Auth-Application-Id   : 4
--------------------------------------------------------------------------------------------------------------
CCA-T contains no MSCC, acceptable for termination
CCR-T REQUEST HEX:
01000418c00001100000000469ca05453d24995f000001074000003964302d6e6c657067312e6d746e2e636f2e7a613b6532652d646174612d726f616d696e673b313737343834373238363b31000000000001080000001b64302d6e6c657067312e6d746e2e636f2e7a610000000128000000116d746e2e636f2e7a610000000000011b4000001a6469616d657465722e65736579652e636f6d0000000001024000000c00000004000001cd40000018382e333232353140336770702e6f7267000001a04000000c000000030000019f4000000c0000000300000125000000236469616d6574657230312e6a6f627572672e65736579652e636f6d00000000014000003b3635353130333730343634363738306e61692e6570632e6d6e633635352e6d636331302e336770706e6574776f726b2e6f726700000001164000000c0000002d000000374000000ced7483c5000001bb4000002c000001c24000000c00000000000001bc4000001732373936303330303232323731393800000001bb4000002c000001c24000000c00000001000001bc4000001736353531303337303436343637383000000001bb40000050000001c24000000c00000003000001bc4000003b3635353130333730343634363738306e61692e6570632e6d6e633635352e6d636331302e336770706e6574776f726b2e6f726700000001c84000003c000001be40000018000001a540000010000000000003e800000001b04000000c000003ec00000368c0000010000028af00000002000001ca4000002c000001cb4000000c00000000000001cc400000183335363438373130373534333636333800000369c00001b8000028af0000036ac00001ac000028af00000002c0000010000028af6f2d60430000080280000010000028af6f2d604300000003c0000010000028af00000000000004cb80000012000028af00010a9012030000000003f8c0000058000028af00000404c0000010000028af000000090000040ac000001c000028af00000416c0000010000028af0000000200000411c0000010000028af59682f0000000410c0000010000028af59682f000000080380000010000028af00000001000004cc80000012000028af000129d016de00000000034fc0000012000028af0001c40d80800000000007ff80000010000028af0000000200000008c0000011000028af363535313000000000000009c0000011000028af32333432300000000000000ac000000d000028af060000000000000cc000000d000028af300000000000000dc0000010000028af3034303000000012c0000011000028af323334323000000000000017c000000e000028af8000000000000016c0000019000028af8232f402000132f4020000000100000000000015c000000d000028af060000000000001e400000147a736d617274746573743131
CCR-T RESPONSE HEX:
010000c4400001100000000469ca05453d24995f000001074000003964302d6e6c657067312e6d746e2e636f2e7a613b6532652d646174612d726f616d696e673b313737343834373238363b310000000000010c4000000c000007d1000001024000000c00000004000001a04000000c000000030000019f4000000c00000003000001164000000c0000002d000001084000001c6469616d6574657230312e65736579652e636f6d000001284000001a6469616d657465722e65736579652e636f6d0000
==============================================================================================================
STEP 4: READ eksqan_diameter_gy
==============================================================================================================
Waiting 22 seconds for stream propagation...
Kinesis: found 1 shard(s) in stream eksqan_diameter_gy
Kinesis: reading stream=eksqan_diameter_gy shard=shardId-000000000000 from 2026-03-30T05:08:15.293457+00:00
==============================================================================================================
eksqan_diameter_gy EVENTS
==============================================================================================================
Matched events          : 4
--------------------------------------------------------------------------------------------------------------
Event 1
Stream                 : eksqan_diameter_gy
PartitionKey           : 03d5b86f533bd6480684e69c25f1612f
SequenceNumber         : 49673127375500584479530676173964796386550232921768198146
ApproxArrival          : 2026-03-30 10:38:21.313000+05:30
Full JSON:
{
  "time": "2026-03-30T05:08:16.677929363Z",
  "peer": "mtn-test",
  "method": "INITIAL_REQUEST",
  "service_type": "DATA",
  "decision": {
    "code": 2001,
    "reason": "APPROVED_DATA",
    "validity_time_sec": 1800,
    "include_final_unit": false,
    "final_unit_action": 0,
    "granted_data_octets": 512000,
    "granted_voice_seconds": 0,
    "granted_sms_units": 0,
    "granted_ussd_seconds": 0
  },
  "avps": [
    {
      "name": "Session-Id",
      "app": 4,
      "code": 263,
      "type": "UTF8String",
      "value": "d0-nlepg1.mtn.co.za;e2e-data-roaming;1774847286;1"
    },
    {
      "name": "Origin-Host",
      "app": 4,
      "code": 264,
      "type": "DiameterIdentity",
      "value": "d0-nlepg1.mtn.co.za"
    },
    {
      "name": "Origin-Realm",
      "app": 4,
      "code": 296,
      "type": "DiameterIdentity",
      "value": "mtn.co.za"
    },
    {
      "name": "Destination-Realm",
      "app": 4,
      "code": 283,
      "type": "DiameterIdentity",
      "value": "diameter.eseye.com"
    },
    {
      "name": "Auth-Application-Id",
      "app": 4,
      "code": 258,
      "type": "Unsigned32",
      "value": 4
    },
    {
      "name": "Service-Context-Id",
      "app": 4,
      "code": 461,
      "type": "UTF8String",
      "value": "8.32251@3gpp.org"
    },
    {
      "name": "CC-Request-Type",
      "app": 4,
      "code": 416,
      "type": "Enumerated",
      "value": "1",
      "label": "INITIAL_REQUEST"
    },
    {
      "name": "CC-Request-Number",
      "app": 4,
      "code": 415,
      "type": "Unsigned32",
      "value": 0
    },
    {
      "name": "Destination-Host",
      "app": 4,
      "code": 293,
      "type": "DiameterIdentity",
      "value": "diameter01.joburg.eseye.com"
    },
    {
      "name": "TGPP-IMSI",
      "app": 4,
      "code": 1,
      "type": "UTF8String",
      "value": "655103704646780nai.epc.mnc655.mcc10.3gppnetwork.org"
    },
    {
      "name": "Origin-State-Id",
      "app": 4,
      "code": 278,
      "type": "Unsigned32",
      "value": 45
    },
    {
      "name": "Event-Timestamp",
      "app": 4,
      "code": 55,
      "type": "Time",
      "value": "2026-03-30T05:08:17Z"
    },
    {
      "name": "Subscription-Id",
      "app": 4,
      "code": 443,
      "type": "Grouped",
      "value": [
        {
          "name": "Subscription-Id-Type",
          "app": 4,
          "code": 450,
          "type": "Enumerated",
          "value": "0",
          "label": "END_USER_E164"
        },
        {
          "name": "Subscription-Id-Data",
          "app": 4,
          "code": 444,
          "type": "UTF8String",
          "value": "279603002227198"
        }
      ]
    },
    {
      "name": "Subscription-Id",
      "app": 4,
      "code": 443,
      "type": "Grouped",
      "value": [
        {
          "name": "Subscription-Id-Type",
          "app": 4,
          "code": 450,
          "type": "Enumerated",
          "value": "1",
          "label": "END_USER_IMSI"
        },
        {
          "name": "Subscription-Id-Data",
          "app": 4,
          "code": 444,
          "type": "UTF8String",
          "value": "655103704646780"
        }
      ]
    },
    {
      "name": "Subscription-Id",
      "app": 4,
      "code": 443,
      "type": "Grouped",
      "value": [
        {
          "name": "Subscription-Id-Type",
          "app": 4,
          "code": 450,
          "type": "Enumerated",
          "value": "3",
          "label": "END_USER_NAI"
        },
        {
          "name": "Subscription-Id-Data",
          "app": 4,
          "code": 444,
          "type": "UTF8String",
          "value": "655103704646780nai.epc.mnc655.mcc10.3gppnetwork.org"
        }
      ]
    },
    {
      "name": "Multiple-Services-Credit-Control",
      "app": 4,
      "code": 456,
      "type": "Grouped",
      "value": [
        {
          "name": "Requested-Service-Unit",
          "app": 4,
          "code": 437,
          "type": "Grouped",
          "value": [
            {
              "name": "CC-Total-Octets",
              "app": 4,
              "code": 421,
              "type": "Unsigned64",
              "value": 512000
            }
          ]
        },
        {
          "name": "Rating-Group",
          "app": 4,
          "code": 432,
          "type": "Unsigned32",
          "value": 1004
        }
      ]
    },
    {
      "name": "Multiple-Services-Indicator",
      "app": 4,
      "code": 455,
      "type": "Enumerated",
      "value": "1",
      "label": "MULTIPLE_SERVICES_SUPPORTED"
    },
    {
      "name": "User-Equipment-Info",
      "app": 4,
      "code": 458,
      "type": "Grouped",
      "value": [
        {
          "name": "User-Equipment-Info-Type",
          "app": 4,
          "code": 459,
          "type": "Enumerated",
          "value": "0",
          "label": "IMEISV"
        },
        {
          "name": "User-Equipment-Info-Value",
          "app": 4,
          "code": 460,
          "type": "OctetString",
          "value": "3564871075436638"
        }
      ]
    },
    {
      "name": "Service-Information",
      "app": 4,
      "code": 873,
      "type": "Grouped",
      "vendor": 10415,
      "value": [
        {
          "name": "PS-Information",
          "app": 4,
          "code": 874,
          "type": "Grouped",
          "vendor": 10415,
          "value": [
            {
              "name": "TGPP-Charging-Id",
              "app": 4,
              "code": 2,
              "type": "OctetString",
              "vendor": 10415,
              "value": "o-`C"
            },
            {
              "name": "PDN-Connection-Charging-Id",
              "app": 4,
              "code": 2050,
              "type": "Unsigned32",
              "vendor": 10415,
              "value": 1865244739
            },
            {
              "name": "TGPP-PDP-Type",
              "app": 4,
              "code": 3,
              "type": "Enumerated",
              "vendor": 10415,
              "value": "0",
              "label": "Ipv4"
            },
            {
              "name": "PDP-Address",
              "app": 4,
              "code": 1227,
              "type": "Address",
              "vendor": 10415,
              "value": "10.144.18.3"
            },
            {
              "name": "QoS-Information",
              "app": 4,
              "code": 1016,
              "type": "Grouped",
              "vendor": 10415,
              "value": [
                {
                  "name": "QoS-Class-Identifier",
                  "app": 4,
                  "code": 1028,
                  "type": "Enumerated",
                  "vendor": 10415,
                  "value": "9",
                  "label": "QCI_9"
                },
                {
                  "name": "Allocation-Retention-Priority",
                  "app": 4,
                  "code": 1034,
                  "type": "Grouped",
                  "vendor": 10415,
                  "value": [
                    {
                      "name": "Priority-Level",
                      "app": 4,
                      "code": 1046,
                      "type": "Unsigned32",
                      "vendor": 10415,
                      "value": 2
                    }
                  ]
                },
                {
                  "name": "APN-Aggregate-Max-Bitrate-UL",
                  "app": 4,
                  "code": 1041,
                  "type": "Unsigned32",
                  "vendor": 10415,
                  "value": 1500000000
                },
                {
                  "name": "APN-Aggregate-Max-Bitrate-DL",
                  "app": 4,
                  "code": 1040,
                  "type": "Unsigned32",
                  "vendor": 10415,
                  "value": 1500000000
                }
              ]
            },
            {
              "name": "Dynamic-Address-Flag",
              "app": 4,
              "code": 2051,
              "type": "Enumerated",
              "vendor": 10415,
              "value": "1",
              "label": "Dynamic"
            },
            {
              "name": "SGSN-Address",
              "app": 4,
              "code": 1228,
              "type": "Address",
              "vendor": 10415,
              "value": "41.208.22.222"
            },
            {
              "name": "GGSN-Address",
              "app": 4,
              "code": 847,
              "type": "Address",
              "vendor": 10415,
              "value": "196.13.128.128"
            },
            {
              "name": "Serving-Node-Type",
              "app": 4,
              "code": 2047,
              "type": "Enumerated",
              "vendor": 10415,
              "value": "2",
              "label": "GTPSGW"
            },
            {
              "name": "TGPP-IMSI-MCC-MNC",
              "app": 4,
              "code": 8,
              "type": "UTF8String",
              "vendor": 10415,
              "value": "65510"
            },
            {
              "name": "TGPP-GGSN-MCC-MNC",
              "app": 4,
              "code": 9,
              "type": "UTF8String",
              "vendor": 10415,
              "value": "23420"
            },
            {
              "name": "TGPP-NSAPI",
              "app": 4,
              "code": 10,
              "type": "OctetString",
              "vendor": 10415,
              "value": "06"
            },
            {
              "name": "TGPP-Selection-Mode",
              "app": 4,
              "code": 12,
              "type": "UTF8String",
              "vendor": 10415,
              "value": "0"
            },
            {
              "name": "TGPP-Charging-Characteristics",
              "app": 4,
              "code": 13,
              "type": "UTF8String",
              "vendor": 10415,
              "value": "0400"
            },
            {
              "name": "TGPP-SGSN-MCC-MNC",
              "app": 4,
              "code": 18,
              "type": "UTF8String",
              "vendor": 10415,
              "value": "23420"
            },
            {
              "name": "TGPP-MS-TimeZone",
              "app": 4,
              "code": 23,
              "type": "OctetString",
              "vendor": 10415,
              "value": "8000"
            },
            {
              "name": "TGPP-User-Location-Info",
              "app": 4,
              "code": 22,
              "type": "OctetString",
              "vendor": 10415,
              "value": "8232F402000132F40200000001"
            },
            {
              "name": "TGPP-RAT-Type",
              "app": 4,
              "code": 21,
              "type": "OctetString",
              "vendor": 10415,
              "value": "06"
            },
            {
              "name": "Called-Station-Id",
              "app": 4,
              "code": 30,
              "type": "UTF8String",
              "value": "zsmarttest11"
            }
          ]
        }
      ]
    }
  ],
  "server_host": "ip-172-30-14-75.eu-west-1.compute.internal",
  "server_time": "2026-03-30T05:08:16.000000000+0000"
}
--------------------------------------------------------------------------------------------------------------
Event 2
Stream                 : eksqan_diameter_gy
PartitionKey           : 03d5b86f533bd6480684e69c25f1612f
SequenceNumber         : 49673127375500584479530676173964796386550232921768198146
ApproxArrival          : 2026-03-30 10:38:21.313000+05:30
Full JSON:
{
  "time": "2026-03-30T05:08:16.894229012Z",
  "peer": "mtn-test",
  "method": "UPDATE_REQUEST",
  "service_type": "DATA",
  "decision": {
    "code": 2001,
    "reason": "APPROVED_DATA",
    "validity_time_sec": 1800,
    "include_final_unit": false,
    "final_unit_action": 0,
    "granted_data_octets": 512000,
    "granted_voice_seconds": 0,
    "granted_sms_units": 0,
    "granted_ussd_seconds": 0
  },
  "avps": [
    {
      "name": "Session-Id",
      "app": 4,
      "code": 263,
      "type": "UTF8String",
      "value": "d0-nlepg1.mtn.co.za;e2e-data-roaming;1774847286;1"
    },
    {
      "name": "Origin-Host",
      "app": 4,
      "code": 264,
      "type": "DiameterIdentity",
      "value": "d0-nlepg1.mtn.co.za"
    },
    {
      "name": "Origin-Realm",
      "app": 4,
      "code": 296,
      "type": "DiameterIdentity",
      "value": "mtn.co.za"
    },
    {
      "name": "Destination-Realm",
      "app": 4,
      "code": 283,
      "type": "DiameterIdentity",
      "value": "diameter.eseye.com"
    },
    {
      "name": "Auth-Application-Id",
      "app": 4,
      "code": 258,
      "type": "Unsigned32",
      "value": 4
    },
    {
      "name": "Service-Context-Id",
      "app": 4,
      "code": 461,
      "type": "UTF8String",
      "value": "8.32251@3gpp.org"
    },
    {
      "name": "CC-Request-Type",
      "app": 4,
      "code": 416,
      "type": "Enumerated",
      "value": "2",
      "label": "UPDATE_REQUEST"
    },
    {
      "name": "CC-Request-Number",
      "app": 4,
      "code": 415,
      "type": "Unsigned32",
      "value": 1
    },
    {
      "name": "Destination-Host",
      "app": 4,
      "code": 293,
      "type": "DiameterIdentity",
      "value": "diameter01.joburg.eseye.com"
    },
    {
      "name": "TGPP-IMSI",
      "app": 4,
      "code": 1,
      "type": "UTF8String",
      "value": "655103704646780nai.epc.mnc655.mcc10.3gppnetwork.org"
    },
    {
      "name": "Origin-State-Id",
      "app": 4,
      "code": 278,
      "type": "Unsigned32",
      "value": 45
    },
    {
      "name": "Event-Timestamp",
      "app": 4,
      "code": 55,
      "type": "Time",
      "value": "2026-03-30T05:08:17Z"
    },
    {
      "name": "Subscription-Id",
      "app": 4,
      "code": 443,
      "type": "Grouped",
      "value": [
        {
          "name": "Subscription-Id-Type",
          "app": 4,
          "code": 450,
          "type": "Enumerated",
          "value": "0",
          "label": "END_USER_E164"
        },
        {
          "name": "Subscription-Id-Data",
          "app": 4,
          "code": 444,
          "type": "UTF8String",
          "value": "279603002227198"
        }
      ]
    },
    {
      "name": "Subscription-Id",
      "app": 4,
      "code": 443,
      "type": "Grouped",
      "value": [
        {
          "name": "Subscription-Id-Type",
          "app": 4,
          "code": 450,
          "type": "Enumerated",
          "value": "1",
          "label": "END_USER_IMSI"
        },
        {
          "name": "Subscription-Id-Data",
          "app": 4,
          "code": 444,
          "type": "UTF8String",
          "value": "655103704646780"
        }
      ]
    },
    {
      "name": "Subscription-Id",
      "app": 4,
      "code": 443,
      "type": "Grouped",
      "value": [
        {
          "name": "Subscription-Id-Type",
          "app": 4,
          "code": 450,
          "type": "Enumerated",
          "value": "3",
          "label": "END_USER_NAI"
        },
        {
          "name": "Subscription-Id-Data",
          "app": 4,
          "code": 444,
          "type": "UTF8String",
          "value": "655103704646780nai.epc.mnc655.mcc10.3gppnetwork.org"
        }
      ]
    },
    {
      "name": "Multiple-Services-Credit-Control",
      "app": 4,
      "code": 456,
      "type": "Grouped",
      "value": [
        {
          "name": "Requested-Service-Unit",
          "app": 4,
          "code": 437,
          "type": "Grouped",
          "value": [
            {
              "name": "CC-Total-Octets",
              "app": 4,
              "code": 421,
              "type": "Unsigned64",
              "value": 512000
            }
          ]
        },
        {
          "name": "Used-Service-Unit",
          "app": 4,
          "code": 446,
          "type": "Grouped",
          "value": [
            {
              "name": "CC-Total-Octets",
              "app": 4,
              "code": 421,
              "type": "Unsigned64",
              "value": 128000
            }
          ]
        },
        {
          "name": "Rating-Group",
          "app": 4,
          "code": 432,
          "type": "Unsigned32",
          "value": 1004
        },
        {
          "name": "Reporting-Reason",
          "app": 4,
          "code": 872,
          "type": "Enumerated",
          "vendor": 10415,
          "value": "3",
          "label": "QUOTA_EXHAUSTED"
        }
      ]
    },
    {
      "name": "User-Equipment-Info",
      "app": 4,
      "code": 458,
      "type": "Grouped",
      "value": [
        {
          "name": "User-Equipment-Info-Type",
          "app": 4,
          "code": 459,
          "type": "Enumerated",
          "value": "0",
          "label": "IMEISV"
        },
        {
          "name": "User-Equipment-Info-Value",
          "app": 4,
          "code": 460,
          "type": "OctetString",
          "value": "3564871075436638"
        }
      ]
    },
    {
      "name": "Service-Information",
      "app": 4,
      "code": 873,
      "type": "Grouped",
      "vendor": 10415,
      "value": [
        {
          "name": "PS-Information",
          "app": 4,
          "code": 874,
          "type": "Grouped",
          "vendor": 10415,
          "value": [
            {
              "name": "TGPP-Charging-Id",
              "app": 4,
              "code": 2,
              "type": "OctetString",
              "vendor": 10415,
              "value": "o-`C"
            },
            {
              "name": "PDN-Connection-Charging-Id",
              "app": 4,
              "code": 2050,
              "type": "Unsigned32",
              "vendor": 10415,
              "value": 1865244739
            },
            {
              "name": "TGPP-PDP-Type",
              "app": 4,
              "code": 3,
              "type": "Enumerated",
              "vendor": 10415,
              "value": "0",
              "label": "Ipv4"
            },
            {
              "name": "PDP-Address",
              "app": 4,
              "code": 1227,
              "type": "Address",
              "vendor": 10415,
              "value": "10.144.18.3"
            },
            {
              "name": "QoS-Information",
              "app": 4,
              "code": 1016,
              "type": "Grouped",
              "vendor": 10415,
              "value": [
                {
                  "name": "QoS-Class-Identifier",
                  "app": 4,
                  "code": 1028,
                  "type": "Enumerated",
                  "vendor": 10415,
                  "value": "9",
                  "label": "QCI_9"
                },
                {
                  "name": "Allocation-Retention-Priority",
                  "app": 4,
                  "code": 1034,
                  "type": "Grouped",
                  "vendor": 10415,
                  "value": [
                    {
                      "name": "Priority-Level",
                      "app": 4,
                      "code": 1046,
                      "type": "Unsigned32",
                      "vendor": 10415,
                      "value": 2
                    }
                  ]
                },
                {
                  "name": "APN-Aggregate-Max-Bitrate-UL",
                  "app": 4,
                  "code": 1041,
                  "type": "Unsigned32",
                  "vendor": 10415,
                  "value": 1500000000
                },
                {
                  "name": "APN-Aggregate-Max-Bitrate-DL",
                  "app": 4,
                  "code": 1040,
                  "type": "Unsigned32",
                  "vendor": 10415,
                  "value": 1500000000
                }
              ]
            },
            {
              "name": "Dynamic-Address-Flag",
              "app": 4,
              "code": 2051,
              "type": "Enumerated",
              "vendor": 10415,
              "value": "1",
              "label": "Dynamic"
            },
            {
              "name": "SGSN-Address",
              "app": 4,
              "code": 1228,
              "type": "Address",
              "vendor": 10415,
              "value": "41.208.22.222"
            },
            {
              "name": "GGSN-Address",
              "app": 4,
              "code": 847,
              "type": "Address",
              "vendor": 10415,
              "value": "196.13.128.128"
            },
            {
              "name": "Serving-Node-Type",
              "app": 4,
              "code": 2047,
              "type": "Enumerated",
              "vendor": 10415,
              "value": "2",
              "label": "GTPSGW"
            },
            {
              "name": "TGPP-IMSI-MCC-MNC",
              "app": 4,
              "code": 8,
              "type": "UTF8String",
              "vendor": 10415,
              "value": "65510"
            },
            {
              "name": "TGPP-GGSN-MCC-MNC",
              "app": 4,
              "code": 9,
              "type": "UTF8String",
              "vendor": 10415,
              "value": "23420"
            },
            {
              "name": "TGPP-NSAPI",
              "app": 4,
              "code": 10,
              "type": "OctetString",
              "vendor": 10415,
              "value": "06"
            },
            {
              "name": "TGPP-Selection-Mode",
              "app": 4,
              "code": 12,
              "type": "UTF8String",
              "vendor": 10415,
              "value": "0"
            },
            {
              "name": "TGPP-Charging-Characteristics",
              "app": 4,
              "code": 13,
              "type": "UTF8String",
              "vendor": 10415,
              "value": "0400"
            },
            {
              "name": "TGPP-SGSN-MCC-MNC",
              "app": 4,
              "code": 18,
              "type": "UTF8String",
              "vendor": 10415,
              "value": "23420"
            },
            {
              "name": "TGPP-MS-TimeZone",
              "app": 4,
              "code": 23,
              "type": "OctetString",
              "vendor": 10415,
              "value": "8000"
            },
            {
              "name": "TGPP-User-Location-Info",
              "app": 4,
              "code": 22,
              "type": "OctetString",
              "vendor": 10415,
              "value": "8232F402000132F40200000001"
            },
            {
              "name": "TGPP-RAT-Type",
              "app": 4,
              "code": 21,
              "type": "OctetString",
              "vendor": 10415,
              "value": "06"
            },
            {
              "name": "Called-Station-Id",
              "app": 4,
              "code": 30,
              "type": "UTF8String",
              "value": "zsmarttest11"
            }
          ]
        }
      ]
    }
  ],
  "server_host": "ip-172-30-14-75.eu-west-1.compute.internal",
  "server_time": "2026-03-30T05:08:16.000000000+0000"
}
--------------------------------------------------------------------------------------------------------------
Event 3
Stream                 : eksqan_diameter_gy
PartitionKey           : 03d5b86f533bd6480684e69c25f1612f
SequenceNumber         : 49673127375500584479530676173964796386550232921768198146
ApproxArrival          : 2026-03-30 10:38:21.313000+05:30
Full JSON:
{
  "time": "2026-03-30T05:08:19.112242905Z",
  "peer": "mtn-test",
  "method": "UPDATE_REQUEST",
  "service_type": "DATA",
  "decision": {
    "code": 2001,
    "reason": "APPROVED_DATA",
    "validity_time_sec": 1800,
    "include_final_unit": false,
    "final_unit_action": 0,
    "granted_data_octets": 512000,
    "granted_voice_seconds": 0,
    "granted_sms_units": 0,
    "granted_ussd_seconds": 0
  },
  "avps": [
    {
      "name": "Session-Id",
      "app": 4,
      "code": 263,
      "type": "UTF8String",
      "value": "d0-nlepg1.mtn.co.za;e2e-data-roaming;1774847286;1"
    },
    {
      "name": "Origin-Host",
      "app": 4,
      "code": 264,
      "type": "DiameterIdentity",
      "value": "d0-nlepg1.mtn.co.za"
    },
    {
      "name": "Origin-Realm",
      "app": 4,
      "code": 296,
      "type": "DiameterIdentity",
      "value": "mtn.co.za"
    },
    {
      "name": "Destination-Realm",
      "app": 4,
      "code": 283,
      "type": "DiameterIdentity",
      "value": "diameter.eseye.com"
    },
    {
      "name": "Auth-Application-Id",
      "app": 4,
      "code": 258,
      "type": "Unsigned32",
      "value": 4
    },
    {
      "name": "Service-Context-Id",
      "app": 4,
      "code": 461,
      "type": "UTF8String",
      "value": "8.32251@3gpp.org"
    },
    {
      "name": "CC-Request-Type",
      "app": 4,
      "code": 416,
      "type": "Enumerated",
      "value": "2",
      "label": "UPDATE_REQUEST"
    },
    {
      "name": "CC-Request-Number",
      "app": 4,
      "code": 415,
      "type": "Unsigned32",
      "value": 2
    },
    {
      "name": "Destination-Host",
      "app": 4,
      "code": 293,
      "type": "DiameterIdentity",
      "value": "diameter01.joburg.eseye.com"
    },
    {
      "name": "TGPP-IMSI",
      "app": 4,
      "code": 1,
      "type": "UTF8String",
      "value": "655103704646780nai.epc.mnc655.mcc10.3gppnetwork.org"
    },
    {
      "name": "Origin-State-Id",
      "app": 4,
      "code": 278,
      "type": "Unsigned32",
      "value": 45
    },
    {
      "name": "Event-Timestamp",
      "app": 4,
      "code": 55,
      "type": "Time",
      "value": "2026-03-30T05:08:19Z"
    },
    {
      "name": "Subscription-Id",
      "app": 4,
      "code": 443,
      "type": "Grouped",
      "value": [
        {
          "name": "Subscription-Id-Type",
          "app": 4,
          "code": 450,
          "type": "Enumerated",
          "value": "0",
          "label": "END_USER_E164"
        },
        {
          "name": "Subscription-Id-Data",
          "app": 4,
          "code": 444,
          "type": "UTF8String",
          "value": "279603002227198"
        }
      ]
    },
    {
      "name": "Subscription-Id",
      "app": 4,
      "code": 443,
      "type": "Grouped",
      "value": [
        {
          "name": "Subscription-Id-Type",
          "app": 4,
          "code": 450,
          "type": "Enumerated",
          "value": "1",
          "label": "END_USER_IMSI"
        },
        {
          "name": "Subscription-Id-Data",
          "app": 4,
          "code": 444,
          "type": "UTF8String",
          "value": "655103704646780"
        }
      ]
    },
    {
      "name": "Subscription-Id",
      "app": 4,
      "code": 443,
      "type": "Grouped",
      "value": [
        {
          "name": "Subscription-Id-Type",
          "app": 4,
          "code": 450,
          "type": "Enumerated",
          "value": "3",
          "label": "END_USER_NAI"
        },
        {
          "name": "Subscription-Id-Data",
          "app": 4,
          "code": 444,
          "type": "UTF8String",
          "value": "655103704646780nai.epc.mnc655.mcc10.3gppnetwork.org"
        }
      ]
    },
    {
      "name": "Multiple-Services-Credit-Control",
      "app": 4,
      "code": 456,
      "type": "Grouped",
      "value": [
        {
          "name": "Requested-Service-Unit",
          "app": 4,
          "code": 437,
          "type": "Grouped",
          "value": [
            {
              "name": "CC-Total-Octets",
              "app": 4,
              "code": 421,
              "type": "Unsigned64",
              "value": 512000
            }
          ]
        },
        {
          "name": "Used-Service-Unit",
          "app": 4,
          "code": 446,
          "type": "Grouped",
          "value": [
            {
              "name": "CC-Total-Octets",
              "app": 4,
              "code": 421,
              "type": "Unsigned64",
              "value": 256000
            }
          ]
        },
        {
          "name": "Rating-Group",
          "app": 4,
          "code": 432,
          "type": "Unsigned32",
          "value": 1004
        },
        {
          "name": "Reporting-Reason",
          "app": 4,
          "code": 872,
          "type": "Enumerated",
          "vendor": 10415,
          "value": "3",
          "label": "QUOTA_EXHAUSTED"
        }
      ]
    },
    {
      "name": "User-Equipment-Info",
      "app": 4,
      "code": 458,
      "type": "Grouped",
      "value": [
        {
          "name": "User-Equipment-Info-Type",
          "app": 4,
          "code": 459,
          "type": "Enumerated",
          "value": "0",
          "label": "IMEISV"
        },
        {
          "name": "User-Equipment-Info-Value",
          "app": 4,
          "code": 460,
          "type": "OctetString",
          "value": "3564871075436638"
        }
      ]
    },
    {
      "name": "Service-Information",
      "app": 4,
      "code": 873,
      "type": "Grouped",
      "vendor": 10415,
      "value": [
        {
          "name": "PS-Information",
          "app": 4,
          "code": 874,
          "type": "Grouped",
          "vendor": 10415,
          "value": [
            {
              "name": "TGPP-Charging-Id",
              "app": 4,
              "code": 2,
              "type": "OctetString",
              "vendor": 10415,
              "value": "o-`C"
            },
            {
              "name": "PDN-Connection-Charging-Id",
              "app": 4,
              "code": 2050,
              "type": "Unsigned32",
              "vendor": 10415,
              "value": 1865244739
            },
            {
              "name": "TGPP-PDP-Type",
              "app": 4,
              "code": 3,
              "type": "Enumerated",
              "vendor": 10415,
              "value": "0",
              "label": "Ipv4"
            },
            {
              "name": "PDP-Address",
              "app": 4,
              "code": 1227,
              "type": "Address",
              "vendor": 10415,
              "value": "10.144.18.3"
            },
            {
              "name": "QoS-Information",
              "app": 4,
              "code": 1016,
              "type": "Grouped",
              "vendor": 10415,
              "value": [
                {
                  "name": "QoS-Class-Identifier",
                  "app": 4,
                  "code": 1028,
                  "type": "Enumerated",
                  "vendor": 10415,
                  "value": "9",
                  "label": "QCI_9"
                },
                {
                  "name": "Allocation-Retention-Priority",
                  "app": 4,
                  "code": 1034,
                  "type": "Grouped",
                  "vendor": 10415,
                  "value": [
                    {
                      "name": "Priority-Level",
                      "app": 4,
                      "code": 1046,
                      "type": "Unsigned32",
                      "vendor": 10415,
                      "value": 2
                    }
                  ]
                },
                {
                  "name": "APN-Aggregate-Max-Bitrate-UL",
                  "app": 4,
                  "code": 1041,
                  "type": "Unsigned32",
                  "vendor": 10415,
                  "value": 1500000000
                },
                {
                  "name": "APN-Aggregate-Max-Bitrate-DL",
                  "app": 4,
                  "code": 1040,
                  "type": "Unsigned32",
                  "vendor": 10415,
                  "value": 1500000000
                }
              ]
            },
            {
              "name": "Dynamic-Address-Flag",
              "app": 4,
              "code": 2051,
              "type": "Enumerated",
              "vendor": 10415,
              "value": "1",
              "label": "Dynamic"
            },
            {
              "name": "SGSN-Address",
              "app": 4,
              "code": 1228,
              "type": "Address",
              "vendor": 10415,
              "value": "41.208.22.222"
            },
            {
              "name": "GGSN-Address",
              "app": 4,
              "code": 847,
              "type": "Address",
              "vendor": 10415,
              "value": "196.13.128.128"
            },
            {
              "name": "Serving-Node-Type",
              "app": 4,
              "code": 2047,
              "type": "Enumerated",
              "vendor": 10415,
              "value": "2",
              "label": "GTPSGW"
            },
            {
              "name": "TGPP-IMSI-MCC-MNC",
              "app": 4,
              "code": 8,
              "type": "UTF8String",
              "vendor": 10415,
              "value": "65510"
            },
            {
              "name": "TGPP-GGSN-MCC-MNC",
              "app": 4,
              "code": 9,
              "type": "UTF8String",
              "vendor": 10415,
              "value": "23420"
            },
            {
              "name": "TGPP-NSAPI",
              "app": 4,
              "code": 10,
              "type": "OctetString",
              "vendor": 10415,
              "value": "06"
            },
            {
              "name": "TGPP-Selection-Mode",
              "app": 4,
              "code": 12,
              "type": "UTF8String",
              "vendor": 10415,
              "value": "0"
            },
            {
              "name": "TGPP-Charging-Characteristics",
              "app": 4,
              "code": 13,
              "type": "UTF8String",
              "vendor": 10415,
              "value": "0400"
            },
            {
              "name": "TGPP-SGSN-MCC-MNC",
              "app": 4,
              "code": 18,
              "type": "UTF8String",
              "vendor": 10415,
              "value": "23420"
            },
            {
              "name": "TGPP-MS-TimeZone",
              "app": 4,
              "code": 23,
              "type": "OctetString",
              "vendor": 10415,
              "value": "8000"
            },
            {
              "name": "TGPP-User-Location-Info",
              "app": 4,
              "code": 22,
              "type": "OctetString",
              "vendor": 10415,
              "value": "8232F402000132F40200000001"
            },
            {
              "name": "TGPP-RAT-Type",
              "app": 4,
              "code": 21,
              "type": "OctetString",
              "vendor": 10415,
              "value": "06"
            },
            {
              "name": "Called-Station-Id",
              "app": 4,
              "code": 30,
              "type": "UTF8String",
              "value": "zsmarttest11"
            }
          ]
        }
      ]
    }
  ],
  "server_host": "ip-172-30-14-75.eu-west-1.compute.internal",
  "server_time": "2026-03-30T05:08:19.000000000+0000"
}
--------------------------------------------------------------------------------------------------------------
Event 4
Stream                 : eksqan_diameter_gy
PartitionKey           : f5d6bea8182d6b9dd320436b7597a422
SequenceNumber         : 49673127375500584479530676174088106820150925441185611778
ApproxArrival          : 2026-03-30 10:38:26.226000+05:30
Full JSON:
{
  "time": "2026-03-30T05:08:21.366616493Z",
  "peer": "mtn-test",
  "method": "TERMINATION_REQUEST",
  "service_type": "DATA",
  "decision": {
    "code": 2001,
    "reason": "APPROVED_DATA",
    "validity_time_sec": 1800,
    "include_final_unit": false,
    "final_unit_action": 0,
    "granted_data_octets": 512000,
    "granted_voice_seconds": 0,
    "granted_sms_units": 0,
    "granted_ussd_seconds": 0
  },
  "avps": [
    {
      "name": "Session-Id",
      "app": 4,
      "code": 263,
      "type": "UTF8String",
      "value": "d0-nlepg1.mtn.co.za;e2e-data-roaming;1774847286;1"
    },
    {
      "name": "Origin-Host",
      "app": 4,
      "code": 264,
      "type": "DiameterIdentity",
      "value": "d0-nlepg1.mtn.co.za"
    },
    {
      "name": "Origin-Realm",
      "app": 4,
      "code": 296,
      "type": "DiameterIdentity",
      "value": "mtn.co.za"
    },
    {
      "name": "Destination-Realm",
      "app": 4,
      "code": 283,
      "type": "DiameterIdentity",
      "value": "diameter.eseye.com"
    },
    {
      "name": "Auth-Application-Id",
      "app": 4,
      "code": 258,
      "type": "Unsigned32",
      "value": 4
    },
    {
      "name": "Service-Context-Id",
      "app": 4,
      "code": 461,
      "type": "UTF8String",
      "value": "8.32251@3gpp.org"
    },
    {
      "name": "CC-Request-Type",
      "app": 4,
      "code": 416,
      "type": "Enumerated",
      "value": "3",
      "label": "TERMINATION_REQUEST"
    },
    {
      "name": "CC-Request-Number",
      "app": 4,
      "code": 415,
      "type": "Unsigned32",
      "value": 3
    },
    {
      "name": "Destination-Host",
      "app": 4,
      "code": 293,
      "type": "DiameterIdentity",
      "value": "diameter01.joburg.eseye.com"
    },
    {
      "name": "TGPP-IMSI",
      "app": 4,
      "code": 1,
      "type": "UTF8String",
      "value": "655103704646780nai.epc.mnc655.mcc10.3gppnetwork.org"
    },
    {
      "name": "Origin-State-Id",
      "app": 4,
      "code": 278,
      "type": "Unsigned32",
      "value": 45
    },
    {
      "name": "Event-Timestamp",
      "app": 4,
      "code": 55,
      "type": "Time",
      "value": "2026-03-30T05:08:21Z"
    },
    {
      "name": "Subscription-Id",
      "app": 4,
      "code": 443,
      "type": "Grouped",
      "value": [
        {
          "name": "Subscription-Id-Type",
          "app": 4,
          "code": 450,
          "type": "Enumerated",
          "value": "0",
          "label": "END_USER_E164"
        },
        {
          "name": "Subscription-Id-Data",
          "app": 4,
          "code": 444,
          "type": "UTF8String",
          "value": "279603002227198"
        }
      ]
    },
    {
      "name": "Subscription-Id",
      "app": 4,
      "code": 443,
      "type": "Grouped",
      "value": [
        {
          "name": "Subscription-Id-Type",
          "app": 4,
          "code": 450,
          "type": "Enumerated",
          "value": "1",
          "label": "END_USER_IMSI"
        },
        {
          "name": "Subscription-Id-Data",
          "app": 4,
          "code": 444,
          "type": "UTF8String",
          "value": "655103704646780"
        }
      ]
    },
    {
      "name": "Subscription-Id",
      "app": 4,
      "code": 443,
      "type": "Grouped",
      "value": [
        {
          "name": "Subscription-Id-Type",
          "app": 4,
          "code": 450,
          "type": "Enumerated",
          "value": "3",
          "label": "END_USER_NAI"
        },
        {
          "name": "Subscription-Id-Data",
          "app": 4,
          "code": 444,
          "type": "UTF8String",
          "value": "655103704646780nai.epc.mnc655.mcc10.3gppnetwork.org"
        }
      ]
    },
    {
      "name": "Multiple-Services-Credit-Control",
      "app": 4,
      "code": 456,
      "type": "Grouped",
      "value": [
        {
          "name": "Used-Service-Unit",
          "app": 4,
          "code": 446,
          "type": "Grouped",
          "value": [
            {
              "name": "CC-Total-Octets",
              "app": 4,
              "code": 421,
              "type": "Unsigned64",
              "value": 256000
            }
          ]
        },
        {
          "name": "Rating-Group",
          "app": 4,
          "code": 432,
          "type": "Unsigned32",
          "value": 1004
        },
        {
          "name": "Reporting-Reason",
          "app": 4,
          "code": 872,
          "type": "Enumerated",
          "vendor": 10415,
          "value": "2",
          "label": "FINAL"
        }
      ]
    },
    {
      "name": "User-Equipment-Info",
      "app": 4,
      "code": 458,
      "type": "Grouped",
      "value": [
        {
          "name": "User-Equipment-Info-Type",
          "app": 4,
          "code": 459,
          "type": "Enumerated",
          "value": "0",
          "label": "IMEISV"
        },
        {
          "name": "User-Equipment-Info-Value",
          "app": 4,
          "code": 460,
          "type": "OctetString",
          "value": "3564871075436638"
        }
      ]
    },
    {
      "name": "Service-Information",
      "app": 4,
      "code": 873,
      "type": "Grouped",
      "vendor": 10415,
      "value": [
        {
          "name": "PS-Information",
          "app": 4,
          "code": 874,
          "type": "Grouped",
          "vendor": 10415,
          "value": [
            {
              "name": "TGPP-Charging-Id",
              "app": 4,
              "code": 2,
              "type": "OctetString",
              "vendor": 10415,
              "value": "o-`C"
            },
            {
              "name": "PDN-Connection-Charging-Id",
              "app": 4,
              "code": 2050,
              "type": "Unsigned32",
              "vendor": 10415,
              "value": 1865244739
            },
            {
              "name": "TGPP-PDP-Type",
              "app": 4,
              "code": 3,
              "type": "Enumerated",
              "vendor": 10415,
              "value": "0",
              "label": "Ipv4"
            },
            {
              "name": "PDP-Address",
              "app": 4,
              "code": 1227,
              "type": "Address",
              "vendor": 10415,
              "value": "10.144.18.3"
            },
            {
              "name": "QoS-Information",
              "app": 4,
              "code": 1016,
              "type": "Grouped",
              "vendor": 10415,
              "value": [
                {
                  "name": "QoS-Class-Identifier",
                  "app": 4,
                  "code": 1028,
                  "type": "Enumerated",
                  "vendor": 10415,
                  "value": "9",
                  "label": "QCI_9"
                },
                {
                  "name": "Allocation-Retention-Priority",
                  "app": 4,
                  "code": 1034,
                  "type": "Grouped",
                  "vendor": 10415,
                  "value": [
                    {
                      "name": "Priority-Level",
                      "app": 4,
                      "code": 1046,
                      "type": "Unsigned32",
                      "vendor": 10415,
                      "value": 2
                    }
                  ]
                },
                {
                  "name": "APN-Aggregate-Max-Bitrate-UL",
                  "app": 4,
                  "code": 1041,
                  "type": "Unsigned32",
                  "vendor": 10415,
                  "value": 1500000000
                },
                {
                  "name": "APN-Aggregate-Max-Bitrate-DL",
                  "app": 4,
                  "code": 1040,
                  "type": "Unsigned32",
                  "vendor": 10415,
                  "value": 1500000000
                }
              ]
            },
            {
              "name": "Dynamic-Address-Flag",
              "app": 4,
              "code": 2051,
              "type": "Enumerated",
              "vendor": 10415,
              "value": "1",
              "label": "Dynamic"
            },
            {
              "name": "SGSN-Address",
              "app": 4,
              "code": 1228,
              "type": "Address",
              "vendor": 10415,
              "value": "41.208.22.222"
            },
            {
              "name": "GGSN-Address",
              "app": 4,
              "code": 847,
              "type": "Address",
              "vendor": 10415,
              "value": "196.13.128.128"
            },
            {
              "name": "Serving-Node-Type",
              "app": 4,
              "code": 2047,
              "type": "Enumerated",
              "vendor": 10415,
              "value": "2",
              "label": "GTPSGW"
            },
            {
              "name": "TGPP-IMSI-MCC-MNC",
              "app": 4,
              "code": 8,
              "type": "UTF8String",
              "vendor": 10415,
              "value": "65510"
            },
            {
              "name": "TGPP-GGSN-MCC-MNC",
              "app": 4,
              "code": 9,
              "type": "UTF8String",
              "vendor": 10415,
              "value": "23420"
            },
            {
              "name": "TGPP-NSAPI",
              "app": 4,
              "code": 10,
              "type": "OctetString",
              "vendor": 10415,
              "value": "06"
            },
            {
              "name": "TGPP-Selection-Mode",
              "app": 4,
              "code": 12,
              "type": "UTF8String",
              "vendor": 10415,
              "value": "0"
            },
            {
              "name": "TGPP-Charging-Characteristics",
              "app": 4,
              "code": 13,
              "type": "UTF8String",
              "vendor": 10415,
              "value": "0400"
            },
            {
              "name": "TGPP-SGSN-MCC-MNC",
              "app": 4,
              "code": 18,
              "type": "UTF8String",
              "vendor": 10415,
              "value": "23420"
            },
            {
              "name": "TGPP-MS-TimeZone",
              "app": 4,
              "code": 23,
              "type": "OctetString",
              "vendor": 10415,
              "value": "8000"
            },
            {
              "name": "TGPP-User-Location-Info",
              "app": 4,
              "code": 22,
              "type": "OctetString",
              "vendor": 10415,
              "value": "8232F402000132F40200000001"
            },
            {
              "name": "TGPP-RAT-Type",
              "app": 4,
              "code": 21,
              "type": "OctetString",
              "vendor": 10415,
              "value": "06"
            },
            {
              "name": "Called-Station-Id",
              "app": 4,
              "code": 30,
              "type": "UTF8String",
              "value": "zsmarttest11"
            }
          ]
        }
      ]
    }
  ],
  "server_host": "ip-172-30-14-75.eu-west-1.compute.internal",
  "server_time": "2026-03-30T05:08:21.000000000+0000"
}
--------------------------------------------------------------------------------------------------------------
==============================================================================================================
STEP 5: READ toucan_diameter_input_stream
==============================================================================================================
Waiting 8 seconds before reading translated stream...
Kinesis: found 1 shard(s) in stream toucan_diameter_input_stream
Kinesis: reading stream=toucan_diameter_input_stream shard=shardId-000000000000 from 2026-03-30T05:08:15.293457+00:00
==============================================================================================================
toucan_diameter_input_stream EVENTS
==============================================================================================================
Matched events          : 4
--------------------------------------------------------------------------------------------------------------
Event 1
Stream                 : toucan_diameter_input_stream
PartitionKey           : 655103704646780
SequenceNumber         : 49672725324820916135104985959961190069575289866612113410
ApproxArrival          : 2026-03-30 10:38:23.410000+05:30
Full JSON:
{
  "time": "2026-03-30T05:08:16.677929363Z",
  "peer": "mtn-test",
  "method": "INITIAL_REQUEST",
  "service_type": "DATA",
  "decision": {
    "code": 2001,
    "reason": "APPROVED_DATA",
    "validity_time_sec": 1800,
    "include_final_unit": false,
    "final_unit_action": 0,
    "granted_data_octets": 512000,
    "granted_voice_seconds": 0,
    "granted_sms_units": 0,
    "granted_ussd_seconds": 0
  },
  "server_host": "ip-172-30-14-75.eu-west-1.compute.internal",
  "server_time": "2026-03-30T05:08:16.000000000+0000",
  "Session-Id": "d0-nlepg1.mtn.co.za;e2e-data-roaming;1774847286;1",
  "Origin-Host": "d0-nlepg1.mtn.co.za",
  "Origin-Realm": "mtn.co.za",
  "Destination-Realm": "diameter.eseye.com",
  "Auth-Application-Id": 4,
  "Service-Context-Id": "8.32251@3gpp.org",
  "CC-Request-Type": "INITIAL_REQUEST",
  "CC-Request-Number": 0,
  "Destination-Host": "diameter01.joburg.eseye.com",
  "TGPP-IMSI": "655103704646780nai.epc.mnc655.mcc10.3gppnetwork.org",
  "Origin-State-Id": 45,
  "Event-Timestamp": "2026-03-30T05:08:17Z",
  "END_USER_E164": "279603002227198",
  "END_USER_IMSI": "655103704646780",
  "END_USER_NAI": "655103704646780nai.epc.mnc655.mcc10.3gppnetwork.org",
  "CC-Total-Octets": 512000,
  "Rating-Group": 1004,
  "Multiple-Services-Indicator": "MULTIPLE_SERVICES_SUPPORTED",
  "IMEISV": "3564871075436638",
  "TGPP-Charging-Id": "o-`C",
  "PDN-Connection-Charging-Id": 1865244739,
  "TGPP-PDP-Type": "Ipv4",
  "PDP-Address": "10.144.18.3",
  "QoS-Class-Identifier": "QCI_9",
  "Priority-Level": 2,
  "APN-Aggregate-Max-Bitrate-UL": 1500000000,
  "APN-Aggregate-Max-Bitrate-DL": 1500000000,
  "Dynamic-Address-Flag": "Dynamic",
  "SGSN-Address": "41.208.22.222",
  "GGSN-Address": "196.13.128.128",
  "Serving-Node-Type": "GTPSGW",
  "TGPP-IMSI-MCC-MNC": "65510",
  "TGPP-GGSN-MCC-MNC": "23420",
  "TGPP-NSAPI": "06",
  "TGPP-Selection-Mode": "0",
  "TGPP-Charging-Characteristics": "0400",
  "TGPP-SGSN-MCC-MNC": "23420",
  "TGPP-MS-TimeZone": "8000",
  "TGPP-User-Location-Info": "8232F402000132F40200000001",
  "TGPP-RAT-Type": "06",
  "Called-Station-Id": "zsmarttest11"
}
--------------------------------------------------------------------------------------------------------------
Event 2
Stream                 : toucan_diameter_input_stream
PartitionKey           : 655103704646780
SequenceNumber         : 49672725324820916135104985959962398995394904495786819586
ApproxArrival          : 2026-03-30 10:38:23.410000+05:30
Full JSON:
{
  "time": "2026-03-30T05:08:16.894229012Z",
  "peer": "mtn-test",
  "method": "UPDATE_REQUEST",
  "service_type": "DATA",
  "decision": {
    "code": 2001,
    "reason": "APPROVED_DATA",
    "validity_time_sec": 1800,
    "include_final_unit": false,
    "final_unit_action": 0,
    "granted_data_octets": 512000,
    "granted_voice_seconds": 0,
    "granted_sms_units": 0,
    "granted_ussd_seconds": 0
  },
  "server_host": "ip-172-30-14-75.eu-west-1.compute.internal",
  "server_time": "2026-03-30T05:08:16.000000000+0000",
  "Session-Id": "d0-nlepg1.mtn.co.za;e2e-data-roaming;1774847286;1",
  "Origin-Host": "d0-nlepg1.mtn.co.za",
  "Origin-Realm": "mtn.co.za",
  "Destination-Realm": "diameter.eseye.com",
  "Auth-Application-Id": 4,
  "Service-Context-Id": "8.32251@3gpp.org",
  "CC-Request-Type": "UPDATE_REQUEST",
  "CC-Request-Number": 1,
  "Destination-Host": "diameter01.joburg.eseye.com",
  "TGPP-IMSI": "655103704646780nai.epc.mnc655.mcc10.3gppnetwork.org",
  "Origin-State-Id": 45,
  "Event-Timestamp": "2026-03-30T05:08:17Z",
  "END_USER_E164": "279603002227198",
  "END_USER_IMSI": "655103704646780",
  "END_USER_NAI": "655103704646780nai.epc.mnc655.mcc10.3gppnetwork.org",
  "CC-Total-Octets": 512000,
  "CC-Total-Octets-2": 128000,
  "Rating-Group": 1004,
  "Reporting-Reason": "QUOTA_EXHAUSTED",
  "IMEISV": "3564871075436638",
  "TGPP-Charging-Id": "o-`C",
  "PDN-Connection-Charging-Id": 1865244739,
  "TGPP-PDP-Type": "Ipv4",
  "PDP-Address": "10.144.18.3",
  "QoS-Class-Identifier": "QCI_9",
  "Priority-Level": 2,
  "APN-Aggregate-Max-Bitrate-UL": 1500000000,
  "APN-Aggregate-Max-Bitrate-DL": 1500000000,
  "Dynamic-Address-Flag": "Dynamic",
  "SGSN-Address": "41.208.22.222",
  "GGSN-Address": "196.13.128.128",
  "Serving-Node-Type": "GTPSGW",
  "TGPP-IMSI-MCC-MNC": "65510",
  "TGPP-GGSN-MCC-MNC": "23420",
  "TGPP-NSAPI": "06",
  "TGPP-Selection-Mode": "0",
  "TGPP-Charging-Characteristics": "0400",
  "TGPP-SGSN-MCC-MNC": "23420",
  "TGPP-MS-TimeZone": "8000",
  "TGPP-User-Location-Info": "8232F402000132F40200000001",
  "TGPP-RAT-Type": "06",
  "Called-Station-Id": "zsmarttest11"
}
--------------------------------------------------------------------------------------------------------------
Event 3
Stream                 : toucan_diameter_input_stream
PartitionKey           : 655103704646780
SequenceNumber         : 49672725324820916135104985959963607921214519124961525762
ApproxArrival          : 2026-03-30 10:38:23.410000+05:30
Full JSON:
{
  "time": "2026-03-30T05:08:19.112242905Z",
  "peer": "mtn-test",
  "method": "UPDATE_REQUEST",
  "service_type": "DATA",
  "decision": {
    "code": 2001,
    "reason": "APPROVED_DATA",
    "validity_time_sec": 1800,
    "include_final_unit": false,
    "final_unit_action": 0,
    "granted_data_octets": 512000,
    "granted_voice_seconds": 0,
    "granted_sms_units": 0,
    "granted_ussd_seconds": 0
  },
  "server_host": "ip-172-30-14-75.eu-west-1.compute.internal",
  "server_time": "2026-03-30T05:08:19.000000000+0000",
  "Session-Id": "d0-nlepg1.mtn.co.za;e2e-data-roaming;1774847286;1",
  "Origin-Host": "d0-nlepg1.mtn.co.za",
  "Origin-Realm": "mtn.co.za",
  "Destination-Realm": "diameter.eseye.com",
  "Auth-Application-Id": 4,
  "Service-Context-Id": "8.32251@3gpp.org",
  "CC-Request-Type": "UPDATE_REQUEST",
  "CC-Request-Number": 2,
  "Destination-Host": "diameter01.joburg.eseye.com",
  "TGPP-IMSI": "655103704646780nai.epc.mnc655.mcc10.3gppnetwork.org",
  "Origin-State-Id": 45,
  "Event-Timestamp": "2026-03-30T05:08:19Z",
  "END_USER_E164": "279603002227198",
  "END_USER_IMSI": "655103704646780",
  "END_USER_NAI": "655103704646780nai.epc.mnc655.mcc10.3gppnetwork.org",
  "CC-Total-Octets": 512000,
  "CC-Total-Octets-2": 256000,
  "Rating-Group": 1004,
  "Reporting-Reason": "QUOTA_EXHAUSTED",
  "IMEISV": "3564871075436638",
  "TGPP-Charging-Id": "o-`C",
  "PDN-Connection-Charging-Id": 1865244739,
  "TGPP-PDP-Type": "Ipv4",
  "PDP-Address": "10.144.18.3",
  "QoS-Class-Identifier": "QCI_9",
  "Priority-Level": 2,
  "APN-Aggregate-Max-Bitrate-UL": 1500000000,
  "APN-Aggregate-Max-Bitrate-DL": 1500000000,
  "Dynamic-Address-Flag": "Dynamic",
  "SGSN-Address": "41.208.22.222",
  "GGSN-Address": "196.13.128.128",
  "Serving-Node-Type": "GTPSGW",
  "TGPP-IMSI-MCC-MNC": "65510",
  "TGPP-GGSN-MCC-MNC": "23420",
  "TGPP-NSAPI": "06",
  "TGPP-Selection-Mode": "0",
  "TGPP-Charging-Characteristics": "0400",
  "TGPP-SGSN-MCC-MNC": "23420",
  "TGPP-MS-TimeZone": "8000",
  "TGPP-User-Location-Info": "8232F402000132F40200000001",
  "TGPP-RAT-Type": "06",
  "Called-Station-Id": "zsmarttest11"
}
--------------------------------------------------------------------------------------------------------------
Event 4
Stream                 : toucan_diameter_input_stream
PartitionKey           : 655103704646780
SequenceNumber         : 49672725324820916135104985969063192565453833610169679874
ApproxArrival          : 2026-03-30 10:38:33.397000+05:30
Full JSON:
{
  "time": "2026-03-30T05:08:21.366616493Z",
  "peer": "mtn-test",
  "method": "TERMINATION_REQUEST",
  "service_type": "DATA",
  "decision": {
    "code": 2001,
    "reason": "APPROVED_DATA",
    "validity_time_sec": 1800,
    "include_final_unit": false,
    "final_unit_action": 0,
    "granted_data_octets": 512000,
    "granted_voice_seconds": 0,
    "granted_sms_units": 0,
    "granted_ussd_seconds": 0
  },
  "server_host": "ip-172-30-14-75.eu-west-1.compute.internal",
  "server_time": "2026-03-30T05:08:21.000000000+0000",
  "Session-Id": "d0-nlepg1.mtn.co.za;e2e-data-roaming;1774847286;1",
  "Origin-Host": "d0-nlepg1.mtn.co.za",
  "Origin-Realm": "mtn.co.za",
  "Destination-Realm": "diameter.eseye.com",
  "Auth-Application-Id": 4,
  "Service-Context-Id": "8.32251@3gpp.org",
  "CC-Request-Type": "TERMINATION_REQUEST",
  "CC-Request-Number": 3,
  "Destination-Host": "diameter01.joburg.eseye.com",
  "TGPP-IMSI": "655103704646780nai.epc.mnc655.mcc10.3gppnetwork.org",
  "Origin-State-Id": 45,
  "Event-Timestamp": "2026-03-30T05:08:21Z",
  "END_USER_E164": "279603002227198",
  "END_USER_IMSI": "655103704646780",
  "END_USER_NAI": "655103704646780nai.epc.mnc655.mcc10.3gppnetwork.org",
  "CC-Total-Octets": 256000,
  "Rating-Group": 1004,
  "Reporting-Reason": "FINAL",
  "IMEISV": "3564871075436638",
  "TGPP-Charging-Id": "o-`C",
  "PDN-Connection-Charging-Id": 1865244739,
  "TGPP-PDP-Type": "Ipv4",
  "PDP-Address": "10.144.18.3",
  "QoS-Class-Identifier": "QCI_9",
  "Priority-Level": 2,
  "APN-Aggregate-Max-Bitrate-UL": 1500000000,
  "APN-Aggregate-Max-Bitrate-DL": 1500000000,
  "Dynamic-Address-Flag": "Dynamic",
  "SGSN-Address": "41.208.22.222",
  "GGSN-Address": "196.13.128.128",
  "Serving-Node-Type": "GTPSGW",
  "TGPP-IMSI-MCC-MNC": "65510",
  "TGPP-GGSN-MCC-MNC": "23420",
  "TGPP-NSAPI": "06",
  "TGPP-Selection-Mode": "0",
  "TGPP-Charging-Characteristics": "0400",
  "TGPP-SGSN-MCC-MNC": "23420",
  "TGPP-MS-TimeZone": "8000",
  "TGPP-User-Location-Info": "8232F402000132F40200000001",
  "TGPP-RAT-Type": "06",
  "Called-Station-Id": "zsmarttest11"
}
--------------------------------------------------------------------------------------------------------------
==============================================================================================================
STEP 6: READ LATEST S3 .gz OBJECT
==============================================================================================================
Waiting 18 seconds before searching S3 bucket...
S3: scanning 40 recent .gz objects in bucket toucan-diameter-qan
S3: exact Session-Id match found in 1 object(s), selecting latest exact match
==============================================================================================================
LATEST S3 RECORD
==============================================================================================================
Key          : 2026/03/30/05/toucan-diameter-delivery-1-2026-03-30-05-08-29-e1b048c4-b115-4103-9ea7-1fd22cab158c.gz
LastModified : 2026-03-30 05:09:37+00:00
Size         : 1661
--------------------------------------------------------------------------------------------------------------
{"time": "2026-03-30T05:08:16.677929363Z", "peer": "mtn-test", "method": "INITIAL_REQUEST", "service_type": "DATA", "decision": {"code": 2001, "reason": "APPROVED_DATA", "validity_time_sec": 1800, "include_final_unit": false, "final_unit_action": 0, "granted_data_octets": 512000, "granted_voice_seconds": 0, "granted_sms_units": 0, "granted_ussd_seconds": 0}, "server_host": "ip-172-30-14-75.eu-west-1.compute.internal", "server_time": "2026-03-30T05:08:16.000000000+0000", "Session-Id": "d0-nlepg1.mtn.co.za;e2e-data-roaming;1774847286;1", "Origin-Host": "d0-nlepg1.mtn.co.za", "Origin-Realm": "mtn.co.za", "Destination-Realm": "diameter.eseye.com", "Auth-Application-Id": 4, "Service-Context-Id": "8.32251@3gpp.org", "CC-Request-Type": "INITIAL_REQUEST", "CC-Request-Number": 0, "Destination-Host": "diameter01.joburg.eseye.com", "TGPP-IMSI": "655103704646780nai.epc.mnc655.mcc10.3gppnetwork.org", "Origin-State-Id": 45, "Event-Timestamp": "2026-03-30T05:08:17Z", "END_USER_E164": "279603002227198", "END_USER_IMSI": "655103704646780", "END_USER_NAI": "655103704646780nai.epc.mnc655.mcc10.3gppnetwork.org", "CC-Total-Octets": 512000, "Rating-Group": 1004, "Multiple-Services-Indicator": "MULTIPLE_SERVICES_SUPPORTED", "IMEISV": "3564871075436638", "TGPP-Charging-Id": "o-`C", "PDN-Connection-Charging-Id": 1865244739, "TGPP-PDP-Type": "Ipv4", "PDP-Address": "10.144.18.3", "QoS-Class-Identifier": "QCI_9", "Priority-Level": 2, "APN-Aggregate-Max-Bitrate-UL": 1500000000, "APN-Aggregate-Max-Bitrate-DL": 1500000000, "Dynamic-Address-Flag": "Dynamic", "SGSN-Address": "41.208.22.222", "GGSN-Address": "196.13.128.128", "Serving-Node-Type": "GTPSGW", "TGPP-IMSI-MCC-MNC": "65510", "TGPP-GGSN-MCC-MNC": "23420", "TGPP-NSAPI": "06", "TGPP-Selection-Mode": "0", "TGPP-Charging-Characteristics": "0400", "TGPP-SGSN-MCC-MNC": "23420", "TGPP-MS-TimeZone": "8000", "TGPP-User-Location-Info": "8232F402000132F40200000001", "TGPP-RAT-Type": "06", "Called-Station-Id": "zsmarttest11", "TCN_id": "01KMYJ9DBKTFW2CMFRDNG71030", "TCN_time": "2026-03-30 05:08:29.171702", "TCN_recordType": "diameter", "TCN_version": "20260303", "TCN_eventTime": "2026-03-30 05:08:17", "TCN_msisdn": "279603002227198", "TCN_imsi": "655103704646780", "TCN_otherParty": "zsmarttest11", "TCN_ipv4": "10.144.18.3", "TCN_sessionId": "d0-nlepg1.mtn.co.za;e2e-data-roaming;1774847286;1", "TCN_packageCategoryId": "7", "TCN_packageItemCategoryId": "105", "TCN_simId": "8927000007638675554", "TCN_packageId": "31889", "TCN_dacctId": "9ce457bc241d11f09087000c29c2aa03", "TCN_iccId": "8927000007638675554", "TCN_portfolioId": "5a959b3803ed11f0918f000c293015c7", "TCN_invoicingEntityId": "70", "TCN_portalId": "3f9add1182783c95e27406df64144f24", "TCN_ratType": "EUTRAN", "TCN_imei": "356487107543661", "TCN_mcc": "234", "TCN_mnc": "20", "TCN_invoicingEntityTitle": "MTNSA", "TCN_parentPortfolioId": "3f9add1182783c95e27406df64144f24", "TCN_currency": "ZAR", "TCN_billingCycle": "202603", "TCN_billingDate": "20260330", "TCN_packageItemIdSource": "packageId", "TCN_packageItemId": "50076"}
{"time": "2026-03-30T05:08:16.894229012Z", "peer": "mtn-test", "method": "UPDATE_REQUEST", "service_type": "DATA", "decision": {"code": 2001, "reason": "APPROVED_DATA", "validity_time_sec": 1800, "include_final_unit": false, "final_unit_action": 0, "granted_data_octets": 512000, "granted_voice_seconds": 0, "granted_sms_units": 0, "granted_ussd_seconds": 0}, "server_host": "ip-172-30-14-75.eu-west-1.compute.internal", "server_time": "2026-03-30T05:08:16.000000000+0000", "Session-Id": "d0-nlepg1.mtn.co.za;e2e-data-roaming;1774847286;1", "Origin-Host": "d0-nlepg1.mtn.co.za", "Origin-Realm": "mtn.co.za", "Destination-Realm": "diameter.eseye.com", "Auth-Application-Id": 4, "Service-Context-Id": "8.32251@3gpp.org", "CC-Request-Type": "UPDATE_REQUEST", "CC-Request-Number": 1, "Destination-Host": "diameter01.joburg.eseye.com", "TGPP-IMSI": "655103704646780nai.epc.mnc655.mcc10.3gppnetwork.org", "Origin-State-Id": 45, "Event-Timestamp": "2026-03-30T05:08:17Z", "END_USER_E164": "279603002227198", "END_USER_IMSI": "655103704646780", "END_USER_NAI": "655103704646780nai.epc.mnc655.mcc10.3gppnetwork.org", "CC-Total-Octets": 512000, "CC-Total-Octets-2": 128000, "Rating-Group": 1004, "Reporting-Reason": "QUOTA_EXHAUSTED", "IMEISV": "3564871075436638", "TGPP-Charging-Id": "o-`C", "PDN-Connection-Charging-Id": 1865244739, "TGPP-PDP-Type": "Ipv4", "PDP-Address": "10.144.18.3", "QoS-Class-Identifier": "QCI_9", "Priority-Level": 2, "APN-Aggregate-Max-Bitrate-UL": 1500000000, "APN-Aggregate-Max-Bitrate-DL": 1500000000, "Dynamic-Address-Flag": "Dynamic", "SGSN-Address": "41.208.22.222", "GGSN-Address": "196.13.128.128", "Serving-Node-Type": "GTPSGW", "TGPP-IMSI-MCC-MNC": "65510", "TGPP-GGSN-MCC-MNC": "23420", "TGPP-NSAPI": "06", "TGPP-Selection-Mode": "0", "TGPP-Charging-Characteristics": "0400", "TGPP-SGSN-MCC-MNC": "23420", "TGPP-MS-TimeZone": "8000", "TGPP-User-Location-Info": "8232F402000132F40200000001", "TGPP-RAT-Type": "06", "Called-Station-Id": "zsmarttest11", "TCN_id": "01KMYJ9DDA5N23P4SJK1WYA7Q8", "TCN_time": "2026-03-30 05:08:29.226036", "TCN_recordType": "diameter", "TCN_version": "20260303", "TCN_eventTime": "2026-03-30 05:08:17", "TCN_msisdn": "279603002227198", "TCN_imsi": "655103704646780", "TCN_otherParty": "zsmarttest11", "TCN_ipv4": "10.144.18.3", "TCN_sessionId": "d0-nlepg1.mtn.co.za;e2e-data-roaming;1774847286;1", "TCN_packageCategoryId": "7", "TCN_packageItemCategoryId": "105", "TCN_simId": "8927000007638675554", "TCN_packageId": "31889", "TCN_dacctId": "9ce457bc241d11f09087000c29c2aa03", "TCN_iccId": "8927000007638675554", "TCN_portfolioId": "5a959b3803ed11f0918f000c293015c7", "TCN_invoicingEntityId": "70", "TCN_portalId": "3f9add1182783c95e27406df64144f24", "TCN_ratType": "EUTRAN", "TCN_imei": "356487107543661", "TCN_mcc": "234", "TCN_mnc": "20", "TCN_invoicingEntityTitle": "MTNSA", "TCN_parentPortfolioId": "3f9add1182783c95e27406df64144f24", "TCN_currency": "ZAR", "TCN_billingCycle": "202603", "TCN_billingDate": "20260330", "TCN_packageItemIdSource": "packageId", "TCN_packageItemId": "50076"}
{"time": "2026-03-30T05:08:19.112242905Z", "peer": "mtn-test", "method": "UPDATE_REQUEST", "service_type": "DATA", "decision": {"code": 2001, "reason": "APPROVED_DATA", "validity_time_sec": 1800, "include_final_unit": false, "final_unit_action": 0, "granted_data_octets": 512000, "granted_voice_seconds": 0, "granted_sms_units": 0, "granted_ussd_seconds": 0}, "server_host": "ip-172-30-14-75.eu-west-1.compute.internal", "server_time": "2026-03-30T05:08:19.000000000+0000", "Session-Id": "d0-nlepg1.mtn.co.za;e2e-data-roaming;1774847286;1", "Origin-Host": "d0-nlepg1.mtn.co.za", "Origin-Realm": "mtn.co.za", "Destination-Realm": "diameter.eseye.com", "Auth-Application-Id": 4, "Service-Context-Id": "8.32251@3gpp.org", "CC-Request-Type": "UPDATE_REQUEST", "CC-Request-Number": 2, "Destination-Host": "diameter01.joburg.eseye.com", "TGPP-IMSI": "655103704646780nai.epc.mnc655.mcc10.3gppnetwork.org", "Origin-State-Id": 45, "Event-Timestamp": "2026-03-30T05:08:19Z", "END_USER_E164": "279603002227198", "END_USER_IMSI": "655103704646780", "END_USER_NAI": "655103704646780nai.epc.mnc655.mcc10.3gppnetwork.org", "CC-Total-Octets": 512000, "CC-Total-Octets-2": 256000, "Rating-Group": 1004, "Reporting-Reason": "QUOTA_EXHAUSTED", "IMEISV": "3564871075436638", "TGPP-Charging-Id": "o-`C", "PDN-Connection-Charging-Id": 1865244739, "TGPP-PDP-Type": "Ipv4", "PDP-Address": "10.144.18.3", "QoS-Class-Identifier": "QCI_9", "Priority-Level": 2, "APN-Aggregate-Max-Bitrate-UL": 1500000000, "APN-Aggregate-Max-Bitrate-DL": 1500000000, "Dynamic-Address-Flag": "Dynamic", "SGSN-Address": "41.208.22.222", "GGSN-Address": "196.13.128.128", "Serving-Node-Type": "GTPSGW", "TGPP-IMSI-MCC-MNC": "65510", "TGPP-GGSN-MCC-MNC": "23420", "TGPP-NSAPI": "06", "TGPP-Selection-Mode": "0", "TGPP-Charging-Characteristics": "0400", "TGPP-SGSN-MCC-MNC": "23420", "TGPP-MS-TimeZone": "8000", "TGPP-User-Location-Info": "8232F402000132F40200000001", "TGPP-RAT-Type": "06", "Called-Station-Id": "zsmarttest11", "TCN_id": "01KMYJ9DE85NZMB5KF6VAK68M0", "TCN_time": "2026-03-30 05:08:29.256402", "TCN_recordType": "diameter", "TCN_version": "20260303", "TCN_eventTime": "2026-03-30 05:08:19", "TCN_msisdn": "279603002227198", "TCN_imsi": "655103704646780", "TCN_otherParty": "zsmarttest11", "TCN_ipv4": "10.144.18.3", "TCN_sessionId": "d0-nlepg1.mtn.co.za;e2e-data-roaming;1774847286;1", "TCN_packageCategoryId": "7", "TCN_packageItemCategoryId": "105", "TCN_simId": "8927000007638675554", "TCN_packageId": "31889", "TCN_dacctId": "9ce457bc241d11f09087000c29c2aa03", "TCN_iccId": "8927000007638675554", "TCN_portfolioId": "5a959b3803ed11f0918f000c293015c7", "TCN_invoicingEntityId": "70", "TCN_portalId": "3f9add1182783c95e27406df64144f24", "TCN_ratType": "EUTRAN", "TCN_imei": "356487107543661", "TCN_mcc": "234", "TCN_mnc": "20", "TCN_invoicingEntityTitle": "MTNSA", "TCN_parentPortfolioId": "3f9add1182783c95e27406df64144f24", "TCN_currency": "ZAR", "TCN_billingCycle": "202603", "TCN_billingDate": "20260330", "TCN_packageItemIdSource": "packageId", "TCN_packageItemId": "50076"}
{"time": "2026-03-30T05:08:21.366616493Z", "peer": "mtn-test", "method": "TERMINATION_REQUEST", "service_type": "DATA", "decision": {"code": 2001, "reason": "APPROVED_DATA", "validity_time_sec": 1800, "include_final_unit": false, "final_unit_action": 0, "granted_data_octets": 512000, "granted_voice_seconds": 0, "granted_sms_units": 0, "granted_ussd_seconds": 0}, "server_host": "ip-172-30-14-75.eu-west-1.compute.internal", "server_time": "2026-03-30T05:08:21.000000000+0000", "Session-Id": "d0-nlepg1.mtn.co.za;e2e-data-roaming;1774847286;1", "Origin-Host": "d0-nlepg1.mtn.co.za", "Origin-Realm": "mtn.co.za", "Destination-Realm": "diameter.eseye.com", "Auth-Application-Id": 4, "Service-Context-Id": "8.32251@3gpp.org", "CC-Request-Type": "TERMINATION_REQUEST", "CC-Request-Number": 3, "Destination-Host": "diameter01.joburg.eseye.com", "TGPP-IMSI": "655103704646780nai.epc.mnc655.mcc10.3gppnetwork.org", "Origin-State-Id": 45, "Event-Timestamp": "2026-03-30T05:08:21Z", "END_USER_E164": "279603002227198", "END_USER_IMSI": "655103704646780", "END_USER_NAI": "655103704646780nai.epc.mnc655.mcc10.3gppnetwork.org", "CC-Total-Octets": 256000, "Rating-Group": 1004, "Reporting-Reason": "FINAL", "IMEISV": "3564871075436638", "TGPP-Charging-Id": "o-`C", "PDN-Connection-Charging-Id": 1865244739, "TGPP-PDP-Type": "Ipv4", "PDP-Address": "10.144.18.3", "QoS-Class-Identifier": "QCI_9", "Priority-Level": 2, "APN-Aggregate-Max-Bitrate-UL": 1500000000, "APN-Aggregate-Max-Bitrate-DL": 1500000000, "Dynamic-Address-Flag": "Dynamic", "SGSN-Address": "41.208.22.222", "GGSN-Address": "196.13.128.128", "Serving-Node-Type": "GTPSGW", "TGPP-IMSI-MCC-MNC": "65510", "TGPP-GGSN-MCC-MNC": "23420", "TGPP-NSAPI": "06", "TGPP-Selection-Mode": "0", "TGPP-Charging-Characteristics": "0400", "TGPP-SGSN-MCC-MNC": "23420", "TGPP-MS-TimeZone": "8000", "TGPP-User-Location-Info": "8232F402000132F40200000001", "TGPP-RAT-Type": "06", "Called-Station-Id": "zsmarttest11", "TCN_id": "01KMYJ9Q3PJRD8WS8A32R0RK93", "TCN_time": "2026-03-30 05:08:39.157981", "TCN_recordType": "diameter", "TCN_version": "20260303", "TCN_eventTime": "2026-03-30 05:08:21", "TCN_msisdn": "279603002227198", "TCN_imsi": "655103704646780", "TCN_otherParty": "zsmarttest11", "TCN_ipv4": "10.144.18.3", "TCN_sessionId": "d0-nlepg1.mtn.co.za;e2e-data-roaming;1774847286;1", "TCN_packageCategoryId": "7", "TCN_packageItemCategoryId": "105", "TCN_simId": "8927000007638675554", "TCN_packageId": "31889", "TCN_dacctId": "9ce457bc241d11f09087000c29c2aa03", "TCN_iccId": "8927000007638675554", "TCN_portfolioId": "5a959b3803ed11f0918f000c293015c7", "TCN_invoicingEntityId": "70", "TCN_portalId": "3f9add1182783c95e27406df64144f24", "TCN_ratType": "EUTRAN", "TCN_imei": "356487107543661", "TCN_mcc": "234", "TCN_mnc": "20", "TCN_invoicingEntityTitle": "MTNSA", "TCN_parentPortfolioId": "3f9add1182783c95e27406df64
--------------------------------------------------------------------------------------------------------------
==============================================================================================================
LATEST S3 FIELD VALIDATION
==============================================================================================================
[PASS] TCNsessionId             expected='d0-nlepg1.mtn.co.za;e2e-data-roaming;1774847286;1' actual='d0-nlepg1.mtn.co.za;e2e-data-roaming;1774847286;1'
[PASS] ENDUSERE164              expected='279603002227198'                   actual='279603002227198'
[PASS] ENDUSERIMSI              expected='655103704646780'                   actual='655103704646780'
[PASS] TGPP-SGSN-MCC-MNC        expected='23420'                             actual='23420'
[PASS] TGPP-RAT-Type            expected='06'                                actual='06'
==============================================================================================================
STEP 7: FINAL SUMMARY
==============================================================================================================
Session-Id                  : d0-nlepg1.mtn.co.za;e2e-data-roaming;1774847286;1
Granted Total Octets        : 512000
Latest S3 Key               : 2026/03/30/05/toucan-diameter-delivery-1-2026-03-30-05-08-29-e1b048c4-b115-4103-9ea7-1fd22cab158c.gz
Latest S3 LastModified      : 2026-03-30 05:09:37+00:00
--------------------------------------------------------------------------------------------------------------
[PASS] TCNsessionId             expected='d0-nlepg1.mtn.co.za;e2e-data-roaming;1774847286;1' actual='d0-nlepg1.mtn.co.za;e2e-data-roaming;1774847286;1'
[PASS] ENDUSERE164              expected='279603002227198'                   actual='279603002227198'
[PASS] ENDUSERIMSI              expected='655103704646780'                   actual='655103704646780'
[PASS] TGPP-SGSN-MCC-MNC        expected='23420'                             actual='23420'
[PASS] TGPP-RAT-Type            expected='06'                                actual='06'
--------------------------------------------------------------------------------------------------------------
E2E validation PASSED FROM DIAMETER CLIENT TO toucan-diameter-qan S3 Bucket!
```