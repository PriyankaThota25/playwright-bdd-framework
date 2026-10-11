Feature: Contact us
  As a visitor
  I want to send a message with an attachment
  So that support can help me

  @smoke
  Scenario: Submit the contact form with a file attachment
    Given I am on the home page
    When I sign up as a new customer
    Then I should be logged in as the new customer
    When I open the contact us page
    And I fill the contact form with name "Priyanka", email "test@example.com", subject "Help" and message "Hello, I need help"
    And I attach the file "test_data/sample.txt"
    And I submit the contact form
    Then I should see the success message "Success! Your details have been submitted successfully."