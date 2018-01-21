from behave import *

num_list = []
global_result = 0.0

startCucumbers = 0.0
leftCucumbers = 0.0


@given('we have behave installed')
def step_impl(context):
    pass


@when('we implement a test')
def step_impl(context):
    assert True is not False


@then('behave will test it for us')
def step_impl(context):
    assert context.failed is False


@given("I have the following numbers")
def step_impl(context):
    """
    @type context: behave.runner.Context
    """
    for row in context.table:
        num_list.append(float(row[0]))


@when("I add them together")
def step_impl(context):
    """
    @type context: behave.runner.Context
    """
    global global_result
    for fl in num_list:
        global_result = global_result + fl


@then("the result should be")
def step_impl(context):
    """
    @type context: behave.runner.Context
    """
    global global_result
    expected_val = float(context.table[0][0])
    assert expected_val == global_result


@given("there are {start} cucumbers")
def step_impl(context, start):
    """
    @type context: behave.runner.Context
    @type start: str
    """
    global startCucumbers
    startCucumbers = start



@when("I eat {eat} cucumbers")
def step_impl(context, eat):
    """
    @type context: behave.runner.Context
    @type eat: str
    """
    global leftCucumbers
    global startCucumbers
    leftCucumbers = float(startCucumbers) - float(eat)


@then("I will have {left} cucumbers left")
def step_impl(context, left):
    """
    @type context: behave.runner.Context
    @type left: str
    """
    global leftCucumbers
    assert float(leftCucumbers) == float(left)