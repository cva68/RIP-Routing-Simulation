Feature: All routers converge

Scenario: Start 7 routers and check their tables
    Given no routers are running
    And the following routers have started:
        | router |
        | 1      |
        | 2      |
        | 3      |
        | 4      |
        | 5      |
        | 6      |
        | 7      |
    When we wait for 5 seconds
    Then the routing tables should contain:
        | router | destination | metric |
        | 1      | 2           | 1      |
        | 1      | 3           | 4      |
        | 1      | 4           | 8      |
        | 1      | 5           | 6      |
        | 1      | 6           | 5      |
        | 1      | 7           | 8      |
        | 2      | 1           | 1      |
        | 2      | 3           | 3      |
        | 2      | 4           | 7      |
        | 2      | 5           | 7      |
        | 2      | 6           | 6      |
        | 2      | 7           | 9      |
        | 3      | 1           | 4      |
        | 3      | 2           | 3      |
        | 3      | 4           | 4      |
        | 3      | 5           | 6      |
        | 3      | 6           | 7      |
        | 3      | 7           | 10     |
        | 4      | 1           | 8      |
        | 4      | 2           | 7      |
        | 4      | 3           | 4      |
        | 4      | 5           | 2      |
        | 4      | 6           | 3      |
        | 4      | 7           | 6      |
        | 5      | 1           | 6      |
        | 5      | 2           | 7      |
        | 5      | 3           | 6      |
        | 5      | 4           | 2      |
        | 5      | 6           | 1      |
        | 5      | 7           | 8      |
        | 6      | 1           | 5      |
        | 6      | 2           | 6      |
        | 6      | 3           | 7      |
        | 6      | 4           | 3      |
        | 6      | 5           | 1      |
        | 6      | 7           | 9      |
        | 7      | 1           | 8      |
        | 7      | 2           | 9      |
        | 7      | 3           | 10     |
        | 7      | 4           | 6      |
        | 7      | 5           | 8      |
        | 7      | 6           | 9      |
