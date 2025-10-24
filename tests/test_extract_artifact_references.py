import os
from pathlib import Path

import pytest

from src.PyDAX import DAXExpression, DAXReference


def read_sample(name: str) -> str:
    root = Path(__file__).resolve().parents[1]
    sample_path = root / "resources" / "sample_dax_expressions" / name
    with open(sample_path, "r", encoding="utf-8") as f:
        return f.read()


def test_udf_using_columns_pairs_table_and_column():
    dax_text = "() => max(factWeather[temp_c]) + max(factWeather[chance_of_snow])"
    expr = DAXExpression(dax_text)
    assert expr.table_column_references == [
        DAXReference(table_name="factWeather", artifact_name="temp_c"),
        DAXReference(table_name="factWeather", artifact_name="chance_of_snow"),
    ]


def test_measure_displayed_charts():
    
    dax_text = """SWITCH(
    [Selected metric],
    "Temperature", [Average Temperature (℃)],
    "Condition",[Average Temperature (℃)],
    "Pressure",[Average Pressure (mB)],
    "Humidity",[Relative humidity (%)],
    "Wind direction",[Average wind speed (km/h)],
    "Wind speed",[Average wind speed (km/h)],
    "Rain probability",[Rain probability (%)])"""
    
    expr = DAXExpression(dax_text)
    assert expr.table_column_references == [
        DAXReference(table_name="", artifact_name="Selected metric"),
        DAXReference(table_name="", artifact_name="Average Temperature (℃)"),
        DAXReference(table_name="", artifact_name="Average Temperature (℃)"),
        DAXReference(table_name="", artifact_name="Average Pressure (mB)"),
        DAXReference(table_name="", artifact_name="Relative humidity (%)"),
        DAXReference(table_name="", artifact_name="Average wind speed (km/h)"),
        DAXReference(table_name="", artifact_name="Average wind speed (km/h)"),
        DAXReference(table_name="", artifact_name="Rain probability (%)"),
        

    ]
    
def test_measure_imports():
    
    dax_text = """CALCULATE(SUM(factTrades[Value (thousands USD)]),factTrades[Export]="Import")"""
    expr = DAXExpression(dax_text)
    assert expr.table_column_references == [
        DAXReference(table_name="factTrades", artifact_name="Value (thousands USD)"),
        DAXReference(table_name="factTrades", artifact_name="Export"),
    ]
    
def test_udf_with_measure_reference():
    dax_text = "() => [Total Sales] / COUNTROWS(DimCustomer)"
    expr = DAXExpression(dax_text)
    assert expr.table_column_references == [
        DAXReference(table_name="", artifact_name="Total Sales"),
    ]