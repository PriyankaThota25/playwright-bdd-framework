Feature: Shopping journey
  As a new customer
  I want to register, search for products, buy something, and manage my account
  So that I can complete a realistic shopping journey

  @e2e
  Scenario: New customer registers, buys a product, and deletes their account
    Given I am on the home page
    When I sign up as a new customer
    Then I should be logged in as the new customer
    When I navigate to the products page
    And I search for "Dress" in the product catalog
    Then I should see matching search results
    When I add the first search result to my cart
    And I proceed to checkout
    And I place the order with valid payment details
    Then I should see my order confirmation
    When I delete my account
    Then I should see my account deletion confirmation
