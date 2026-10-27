Feature: Login API
  As a client application
  I want to verify user credentials through automationexercise.com's REST API
  So that I can authenticate users without going through the UI

  @api
  Scenario: Verify login with valid credentials
    When I verify login as "registered_user"
    Then the response status code should be 200
    And the response field "responseCode" should be 200
    And the response field "message" should be "User exists!"

  @api
  Scenario: Verify login with invalid credentials
    When I verify login as "invalid_user"
    Then the response status code should be 200
    And the response field "responseCode" should be 404
    And the response field "message" should be "User not found!"

  @api
  Scenario: Verify login without credentials
    When I verify login without credentials
    Then the response status code should be 200
    And the response field "responseCode" should be 400
