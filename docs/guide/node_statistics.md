# Node statistics and performance values

The diameter stack collects statistical data on its performance.

Statistics are provided on three different levels:

## Peer statistics

Statistics are collected individually for each configured peer, accessible 
through the [`statistics`][diameter.node.peer.Peer.statistics] instance 
attribute, which holds an instance of [`PeerStats`][diameter.node.peer.PeerStats].

Peer statistics record the following values:

`avg_response_time`
:   Average time in seconds spent processing a request, recorded individually
    for each received request type. Contains a dictionary, with request types
    as keys and average response times as values, e.g.:

    ```json
    {"Capabilities-Exchange": 1.0, "Device-Watchdog": 0.000157}
    ```

    The value is calculated from the time spent processing the last 1024 
    requests.

`avg_response_time_overall`
:   Average time in seconds spent processing any request received through the 
    peer.

    The value is calculated from the time spent processing the last 1024 
    requests.

`processed_req_per_second`
:   The *rate* of requests processed, per second, recorded individually for 
    each received request type. Contains a dictionary, with request types as
    keys and rate of processed requests as values. E.g.:

    ```json
    {"Capabilities-Exchange": 1.0, "Device-Watchdog": 3.0}
    ```

    The rate is calculated by adding the total sum of time spent processing the
    last 1024 requests, separately for each request type, and dividing the sums
    by the amount of requests. 

    The request rate is likely to be very high, if the peer receives low 
    traffic.

`processed_req_per_second_overall`
:   The overall *rate* of requests processed, per second, for the entire peer.

    Similar to `processed_req_per_second`, the rate is calculated by adding the
    total sum of time spent on processing the last 1024 requests, for any 
    request type, and diving the sum by the amount of requests.


## Node statistics

The diameter node collects statistics for all of its peers and calculates 
cumulated values. The node statistics are available as the 
[`statistics`][diameter.node.Node.statistics] instance attribute, which returns 
an instance of [`NodeStats`][diameter.node.NodeStats].

The node statistics record following values:

`avg_response_time`
:   Average response time, recorded individually for each request type. 
    Identical to the same attribute in peer statistics, except calculated 
    cumulated over all peers.

`avg_response_time_overall`
:   Average response time for the entire node.
    Identical to the same attribute in peer statistics, except calculated 
    cumulated over all peers.

`processed_req_per_second`
:   Rate of requests processed per second. Identical to the same attribute in 
    peer statistics, except calculated cumulated over all peers.

`processed_req_per_second_overall`
:   Rate of requests processed per second. Identical to the same attribute in 
    peer statistics, except calculated cumulated over all peers.

`received_req_counters`
:   A list containing three integer values, indicating the exact amount of 
    request received by the node in the last minute, five minutes and the last
    15 minutes.

`sent_result_code_range_counters`
:   A dictionary containing exact values of sent result code types. The 
    dictionary holds result code ranges as keys, and lists of integers as 
    values. Each result code range has the format of "1xxx", "2xxx" etc. Each
    value is a list with three integers; the amount of sent result codes for 
    the last minute, last 5 minutes and last 15 minutes. E.g.:

    ```json
    {"2xxx": [150,321,321], "4xxx": [58,103,103], "5xxx": [1,1,1]}
    ```


## Historical statistics

The node, as long as it is running, takes a snapshot of the `Node.statistics` 
return value every 60 seconds and stores it as a serialised dictionary in the
[`statistics_history`][diameter.node.Node.statistics_history] 
instance attribute. The history is a list (a deque) of dictionaries and holds 
1440 entries, i.e. historical values for the past 24 hours.

Values of each dictionary correspond to attribute names of `NodeStats`, with
one `timestamp` key added, containing the UNIX timestamp of the snapshot.

```json
[
    {
        "avg_response_time": {
            "Capabilities-Exchange": 1.0,
            "Credit-Control": 0.033816425120772944,
            "Device-Watchdog": 0.3333333333333333
        },
        "avg_response_time_overall": 0.029674902627634447,
        "processed_req_per_second": {
            "Capabilities-Exchange": 1.0,
            "Credit-Control": 29.571428571428573,
            "Device-Watchdog": 3.0
        },
        "processed_req_per_second_overall": 30.714285714285715,
        "received_req_counters": [209, 213, 213],
        "sent_result_code_range_counters": {
            "2xxx": [166, 171, 171],
            "4xxx": [44, 44, 44]
        },
        "timestamp": 1705507856
    },
    {
        "avg_response_time": {
            "Capabilities-Exchange": 1.0,
            "Credit-Control": 0.03357314148681055,
            "Device-Watchdog": 0.3333333333333333
        },
        "avg_response_time_overall": 0.028846585890826056,
        "processed_req_per_second": {
            "Capabilities-Exchange": 1.0,
            "Credit-Control": 29.785714285714285,
            "Device-Watchdog": 3.0
        },
        "processed_req_per_second_overall": 30.357142857142858,
        "received_req_counters": [209, 423, 423],
        "sent_result_code_range_counters": {
            "2xxx": [150, 321, 321],
            "4xxx": [58, 103, 103],
            "5xxx": [1, 1, 1]
        },
        "timestamp": 1705507916
    }
]
```