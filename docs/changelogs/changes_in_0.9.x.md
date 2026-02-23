---
shallow_toc: 3
---
# Changelog for the 0.9.x release

## 0.9.0

### New interfaces and commands implemented

Support for the S6a/S6d, S13, S7a/S7d (`3GPP TS 29.272`) and the Sh
(`3GPP TS 29.329`) interfaces has been added, with the following command codes
implemented:

| Command-Name                      | Interface | Abbreviation | Code    |
| ----------------------------------|-----------|--------------|---------|
| Update-Location-Request           | S6a/S6d   | ULR          | 316     |
| Update-Location-Answer            | S6a/S6d   | ULA          | 316     |
| Cancel-Location-Request           | S6a/S6d   | CLR          | 317     |
| Cancel-Location-Answer            | S6a/S6d   | CLA          | 317     |
| Authentication-InformationRequest | S6a/S6d   | AIR          | 318     |
| Authentication-InformationAnswer  | S6a/S6d   | AIA          | 318     |
| Insert-Subscriber-Data-Request    | S6a/S6d   | IDR          | 319     |
| Insert-Subscriber-Data-Answer     | S6a/S6d   | IDA          | 319     |
| Delete-Subscriber-Data-Request    | S6a/S6d   | DSR          | 320     |
| Delete-Subscriber-Data-Answer     | S6a/S6d   | DSA          | 320     |
| Purge-UE-Request                  | S6a/S6d   | PUR          | 321     |
| Purge-UE-Answer                   | S6a/S6d   | PUA          | 321     |
| Reset-Request                     | S6a/S6d   | RSR          | 322     |
| Reset-Answer                      | S6a/S6d   | RSA          | 322     |
| Notify-Request                    | S6a/S6d   | NOR          | 323     |
| Notify-Answer                     | S6a/S6d   | NOA          | 323     |
| Update-VCSG-Location-Request      | S7a/S7d   | UVR          | 8388638 |
| Update-VCSG-Location-Answer       | S7a/S7d   | ULA          | 8388638 |
| Insert-Subscriber-Data-Request    | S7a/S7d   | IDR          | 319     |
| Insert-Subscriber-Data-Answer     | S7a/S7d   | IDA          | 319     |
| Delete-Subscriber-Data-Request    | S7a/S7d   | DSR          | 320     |
| Delete-Subscriber-Data-Answer     | S7a/S7d   | DSA          | 320     |
| Reset-Request                     | S7a/S7d   | RSR          | 322     |
| Reset-Answer                      | S7a/S7d   | RSA          | 322     |
| Cancel-VCSG-Location-Request      | S7a/S7d   | CVR          | 8388642 |
| Cancel-VCSG-Location-Answer       | S7a/S7d   | CVA          | 8388642 |
| ME-Identity-Check-Request         | S13       | ECR          | 324     |
| ME-Identity-Check-Answer          | S13       | ECA          | 324     |
| User-Data-Request                 | Sh        | UDR          | 306     |
| User-Data-Answer                  | Sh        | UDA          | 306     |
| Profile-Update-Request            | Sh        | PUR          | 307     |
| Profile-Update-Answer             | Sh        | PUA          | 307     |
| Subscribe-Notifications-Request   | Sh        | SNR          | 308     |
| Subscribe-Notifications-Answer    | Sh        | SNA          | 308     |
| Push-Notification-Request         | Sh        | PNR          | 309     |
| Push-Notification-Answer          | Sh        | PNA          | 309     |


### New grouped AVPs implemented

The following grouped AVPs have been added, from `3GPP TS 29.272`:

* Active-APN (1612)
* Adjacent-Access-Restriction-Data (1673)
* Adjacent-PLMNs (1672)
* AESE-Communication-Pattern (3113)
* AMBR (1435)
* APN-Configuration (1430)
* APN-Configuration-Profile (1429)
* Area-Scope (1623)
* Authentication-Info (1413)
* Call-Barring-Info (1488)
* CSG-Subscription-Data (1436)
* E-UTRAN-Vector (1414)
* eDRX-Cycle-Length (1691)
* eDRX-Related-RAT (1705)
* Emergency-Info (1687)
* EPS-Location-Information (1496)
* EPS-User-State (1495)
* Equivalent-PLMN-List (1637)
* External-Client (1479)
* GERAN-Vector (1416)
* GPRS-Subscription-Data (1467)
* IMSI-Group-Id (1675)
* LCS-Info (1473)
* LCS-PrivacyException (1475)
* Local-Time-Zone (1649)
* Location-Information-Configuration (3135)
* MBSFN-Area (1694)
* MDT-Configuration (1622)
* MDT-Configuration-NR (1720)
* MIP6-Agent-Info (486)
* MME-Location-Information (1600)
* MME-User-State (1497)
* MO-LR (1485)
* Monitoring-Event-Configuration (3122)
* Monitoring-Event-Report (3123)
* Paging-Time-Window (1701)
* PC5-Flow-Bitrates (1714)
* PC5-QoS-Flow (1712)
* PDP-Context (1469)
* ProSe-Subscription-Data (3701)
* PS-Subscribed-QoS-Profile (1431)
* Requested-EUTRAN-Authentication-Info (1408)
* Requested-UTRAN-GERAN-Authentication-Info (1409)
* Service-Type (1483)
* SGSN-Location-Information (1601)
* SGSN-User-State (1498)
* Specific-APN-Info (1472)
* Subscription-Data (1400)
* Subscription-Data-Deletion (1685)
* Supported-Services (3143)
* Teleservice-List (1486)
* Trace-Data (1458)
* UE-PC5-QoS (1711)
* UE-Reachability-Configuration (3129)
* UTRAN-Vector (1415)
* V2X-Subscription-Data (1688)
* V2X-Subscription-Data (1688)
* V2X-Subscription-Data-Nr (1710)
* VPLMN-CSG-Subscription-Data (1641)
* WLAN-offloadability (1667)

From `3GPP TS 29.336`:

* Communication-Pattern-Set (3114)
* MTC-Provider-Info (3178)
* PDN-Connectivity-Status-Configuration (3180)
* PDN-Connectivity-Status-Report (3181)
* Scheduled-communication-time (3118)

From `3GPP TS 29.128`:

* Idle-Status-Indication (4322)

From `3GPP TS 29.344`:

* ProSe-Allowed-PLMN (3703)
* ProSe-Subscription-Data (3701)

And from `RFC 8583`:

* Load (650)


### New AVP definitions added

Adds new AVPs to the dictionary, from `3GPP TS 29.272`:

* Third-Context-Identifier (1719)
* MDT-Configuration-NR (1720)
* Event-Threshold-SINR (1721)
* Collection-Period-RRM (1722)
* Collection-Period-M6 (1723)
* Collection-Period-M7 (1724)
* Sensor-Measurement (1725)
* NR-Cell-Global-Identity (1726)
* Trace-Reporting-Consumer-Uri (1727)
* PLMN-RAT-Usage-Control (1728)
* SF-ULR-Timestamp (1729)
* SF-Provisional-Indication (1730)

From `3GPP TS 29.336`:

* Battery-Indicator (3185)
* SCEF-Reference-ID-Ex (3186)
* SCEF-Reference-ID-for-Deletion-Ext (3187)

From `3GPP TS 29.329`:

* Call-Reference-Info (720)
* Call-Reference-Number (721)
* AS-Number (722)


### Changed and/or renamed AVPs

* Call-Barring-Infor-List (1488) renamed to Call-Barring-Info (1488)
* Time-First-Reception code changed from 3456 to 3466 as it overlapped with
  Proximity-Cancellation-Timestamp


### Other changes and bugfixes

* Issue fixed, with an AVP length not being set at all if it has no content at all
* `MultipleServicesCreditControl.trigger` type is now corrected to `Trigger`
* `ServiceDataContainer.traffic_steering_policy_identifier_dl` corrected to 
  `ServiceDataContainer.traffic_steering_policy_identifier_ul`
* `RelatedChangeConditionInformation.presence_reporting_area_information` corrected to
  `RelatedChangeConditionInformation.presence_reporting_area_information`
* `Classifier` missing attribute `classifier_id` added
* Check for missing, mandatory AVPs in messages received via `Node` has been
  fixed, missing AVPs now produce an `E_RESULT_CODE_DIAMETER_MISSING_AVP` error
  correctly
* `Node.validate_received_request_avps` attribute added, which permits disabling
  AVP validation during runtime
* AVPs serialised using the `dump` function now show `"(unset)"` as the value 
  for every AVP that has no value at all
