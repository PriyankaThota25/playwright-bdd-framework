Feature: Products API
  As a client application
  I want to query product data through automationexercise.com's REST API
  So that I can browse and search the product catalog programmatically

  @api
  Scenario: List all products
    When I GET the products list
    Then the response status code should be 200
    And the response field "responseCode" should be 200
    And the response should contain at least 1 product

  @api
  Scenario: Search for an existing product
    When I search for the product "Top"
    Then the response status code should be 200
    And the response field "responseCode" should be 200
    And the response should contain at least 1 product
