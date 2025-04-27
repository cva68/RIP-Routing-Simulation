Feature: Reconvergence of routing tables after killing a router

Scenario: Killing router 7 and verifying alternative paths remain
    Given no routers are running
    And the following routers have started:
        | router |
        | 4      |
        | 5      |
        | 6      |
        | 7      |
    When we wait for 5 seconds
    Then the routing tables should contain:
        | router | destination | metric |
        | 4      | 5           | 2      |
        | 4      | 6           | 3      |
        | 4      | 7           | 6      |
        | 5      | 4           | 2      |
        | 5      | 6           | 1      |
        | 5      | 7           | 8      |
        | 6      | 4           | 3      |
        | 6      | 5           | 1      |
        | 6      | 7           | 9      |
        | 7      | 4           | 6      |
        | 7      | 5           | 8      |
        | 7      | 6           | 9      |
    When router 7 is killed
    And we wait for 7 seconds
    Then the routing table of router 4 contains a route to 7 with a garbage collection timer running
    And the routing table of router 5 contains a route to 7 with a garbage collection timer running
    And the routing table of router 6 contains a route to 7 with a garbage collection timer running
    When we wait for 5 seconds
    Then the routing tables should contain:
        | router | destination | metric |
        | 4      | 5           | 2      |
        | 4      | 6           | 3      |
        | 5      | 4           | 2      |
        | 5      | 6           | 1      |
        | 6      | 4           | 3      |
        | 6      | 5           | 1      |
