import pytest

from src.PyDAX import (
    DAXExpression,
    DAXArtifactReference,
    DAXTableReference,
    DAXVariableReference,
    DAXFunctionReference,
)


def test_collects_variables_and_variable_references():
    dax = "VAR x = COUNTROWS(DimCustomer) VAR y = x + 1 RETURN y"
    expr = DAXExpression(dax)

    # Variables declared
    assert len(expr.variables) == 2
    names = [v.name for v in expr.variables]
    assert names == ["x", "y"]

    # Last expression tokens
    assert expr.variables[0].last_expression_token is not None
    assert expr.variables[0].last_expression_token.text == ")"  # COUNTROWS(...)
    assert expr.variables[1].last_expression_token is not None
    assert expr.variables[1].last_expression_token.text == "1"  # x + 1

    # Variable references: 'x' used in y definition, 'y' returned
    var_refs = {v.name for v in expr.variable_references}
    assert {"x", "y"}.issubset(var_refs)


def test_detects_user_defined_function_reference(make_function_ref):
    dax = "MyUDF(1) + 2"
    expr = DAXExpression(dax)

    assert expr.function_references == [make_function_ref(name="MyUDF")]


def test_detects_standalone_table_reference_in_filter(make_artifact_ref):
    dax = "CALCULATE(SUM(factTrades[Value]), FILTER(factTrades, factTrades[Export]=\"Import\"))"
    expr = DAXExpression(dax)

    # Column references still found
    assert expr.table_column_references == [
        make_artifact_ref(table_name="factTrades", artifact_name="Value"),
        make_artifact_ref(table_name="factTrades", artifact_name="Export"),
    ]

    # Standalone table reference inside FILTER should be captured
    table_refs = {t.name for t in expr.table_references}
    assert "factTrades" in table_refs


def test_variables_in_nasty_measure():
    dax = (
        "VAR UnusedVar1 = 123\n"
        "VAR SalesPerCustomer = SUM(factCopy[temp_c]) / COUNTROWS(VALUES(dimCities[Kanton]))\n"
        "VAR UnusedVar2 = IFERROR(SUM(factWeather[temp_c]), 0)\n"
        "RETURN\n"
        "CALCULATE(\n"
        "    [Measure displayed charts],\n"
        "    FILTER('factWeather',factWeather[temp_c] > 10),\n"
        "    FILTER(factWeather, [Average Temperature (℃)] > 20)\n"
        ")"
    )
    expr = DAXExpression(dax)
    var_names = {v.name for v in expr.variables}
    assert {"UnusedVar1", "SalesPerCustomer", "UnusedVar2"}.issubset(var_names)


def test_variables_in_average_pressure_card_title():
    dax = (
        "VAR original_metric = \"Pressure\"\n"
        "VAR selected_date = SELECTEDVALUE(factWeather[Datetime])\n"
        "VAR max_date_all=CALCULATE(MAX(factWeather[Datetime]),ALL(factWeather))\n"
        "VAR min_date_all= CALCULATE(MIN(factWeather[Datetime]),ALL(factWeather))\n"
        "VAR max_date=MAX(factWeather[Datetime])\n"
        "VAR min_date= MIN(factWeather[Datetime])\n"
        "VAR actual_datetime = CALCULATE(MIN(factWeather[Datetime]),ALL(factWeather),factWeather[Forecast]=\"Aktuell\")\n"
        "var _datetime = IF(NOT ISBLANK(selected_date), selected_date, IF(max_date=max_date_all &&min_date=min_date_all, actual_datetime,min_date&\" - \"&max_date))\n"
        "VAR lan = [Selected Language]\n"
        "VAR average_ = SWITCH(lan,\n"
        "    \"Deutsch\",\" - (Durchschnitt)\",\n"
        "    \"English\",\" - (average)\",\n"
        "    \"Français\",\" - (moyenne)\",\n"
        "    \"Italiano\",\" - (media)\")\n"
        "VAR _avg = IF(OR(_datetime=actual_datetime,_datetime=selected_date),BLANK(),average_)\n"
        "VAR tr_metric= CALCULATE( FIRSTNONBLANK(trMetrics[Metric],TRUE()), ALL(trMetrics), trMetrics[Original]=original_metric, trMetrics[Language]=lan)\n"
        "RETURN tr_metric&\" (mB)\"&_avg\n"
    )
    expr = DAXExpression(dax)
    var_names = {v.name for v in expr.variables}
    expected = {"original_metric","selected_date","max_date_all","min_date_all","max_date","min_date","actual_datetime","_datetime","lan","average_","_avg","tr_metric"}
    assert expected.issubset(var_names)
