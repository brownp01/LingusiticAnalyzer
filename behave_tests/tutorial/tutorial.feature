# Created by tlblanton at 1/21/18
Feature: Showing off behave
  # Enter feature description here

  Scenario: run a simple test
    Given we have behave installed
    When we implement a test
    Then behave will test it for us

  Scenario: add two numbers test
    Given I have the following numbers
    | Numbers |
    | 5       |
    | 8       |
    | 9891    |
    When I add them together
    Then the result should be
    | Result |
    | 9904   |


  Scenario Outline: controlling order
    Given there are <start> cucumbers
    When I eat <eat> cucumbers
    Then I will have <left> cucumbers left

  Examples:
    | start | eat | left|
    | 12    | 5   | 7   |
    | 10    | 2   | 8   |


    Given I have do not have something
    Then everything is fine