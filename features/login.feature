Feature: Login
  As a registered user of automationexercise.com
  I want to log into my account
  So that I can shop and manage my account

  Background:
    Given I am on the login page

  @smoke
  Scenario: Successful login with valid credentials
    When I log in as "registered_user"
    Then I should be logged in successfully

  @smoke
  Scenario: Login fails with invalid credentials
    When I log in as "invalid_user"
    Then I should see an invalid credentials error
