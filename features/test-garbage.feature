Feature: Garbage Collection

Scenario: Router 2 is killed and router 1 and 3 garbage collect
    Given no routers are running
    And the following routers have started:
        | router |
        | 1      |
        | 2      |
        | 3      |
    When we wait for 5 seconds
    Then the routing tables should contain:
        | router | destination | metric |
        | 1      | 2           | 1      |
        | 1      | 3           | 4      |
        | 2      | 1           | 1      |
        | 2      | 3           | 3      |
        | 3      | 1           | 4      |
        | 3      | 2           | 3      |
    When router 2 is killed
    And we wait for 7 seconds
    Then the routing table of router 1 contains a route to 2 with a garbage collection timer running
    And the routing table of router 3 contains a route to 2 with a garbage collection timer running
    And the routing table of router 1 contains a route to 2 with metric 16
    And the routing table of router 3 contains a route to 2 with metric 16

Scenario: Router 4 is killed, breaking paths between 3 and 5
    Given no routers are running
    And the following routers have started:
        | router |
        | 3      |
        | 4      |
        | 5      |
    When we wait for 5 seconds
    Then the routing tables should contain:
        | router | destination | metric |
        | 3      | 4           | 4      |
        | 3      | 5           | 6      |
        | 4      | 3           | 4      |
        | 4      | 5           | 2      |
        | 5      | 3           | 6      |
        | 5      | 4           | 2      |
    When router 4 is killed
    And we wait for 7 seconds
    Then the routing table of router 3 contains a route to 4 with a garbage collection timer running
    And the routing table of router 3 contains a route to 5 with a garbage collection timer running
    And the routing table of router 5 contains a route to 4 with a garbage collection timer running
    And the routing table of router 5 contains a route to 3 with a garbage collection timer running
    And the routing table of router 3 contains a route to 4 with metric 16
    And the routing table of router 3 contains a route to 5 with metric 16
    And the routing table of router 5 contains a route to 4 with metric 16
    And the routing table of router 5 contains a route to 3 with metric 16