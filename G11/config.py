# -*- coding: utf-8 -*-
"""GUM数据处理配置文件"""

# 需要处理的列名
SKIP_COLUMNS = [
    'current_standby_external', 'current_standby_internal', 'current_consumption',
    'ref_pressure', 'dut_pressure', 'pressure_accuracy', 'ref_pressure.1',
    'dut_pressure.1', 'pressure_accuracy.1', 'ref_pressure.2', 'dut_pressure.2',
    'pressure_accuracy.2', 'ref_pressure.3', 'dut_pressure.3', 'pressure_accuracy.3',
    'ref_pressure.4', 'dut_pressure.4', 'pressure_accuracy.4', 'ref_temperature',
    'dut_temperature', 'temperature_accuracy', 'ref_temperature.1', 'dut_temperature.1',
    'temperature_accuracy.1', 'ref_temperature.2', 'dut_temperature.2',
    'temperature_accuracy.2', 'ref_temperature.3', 'dut_temperature.3',
    'temperature_accuracy.3', 'ref_temperature.4', 'dut_temperature.4',
    'temperature_accuracy.4', 'pressure_noise', 'pressure_noise.1', 'tco_dt_10',
    'tco_self_test', 'pressure_humidity_sensitivity', 'ASIC_self_test_signal1_accuracy',
    'ASIC_self_test_signal2_accuracy', 'ASIC_self_test_signal1_accuracy_pre_comp',
    'ASIC_self_test_signal2_accuracy_pre_comp', 'ASIC_self_test_signal_sensitivity_error',
    'tco_self_test_error', 'temperature_noise', 'temperature_noise.1', 'temperature_noise.2',
    'temperature_noise.3', 'temperature_noise.4', 'pressure_accuracy_current'
]

# 温度设置
SET_TEMPERATURE = ['25', '25', '25', '35', '35', '35', '35', '35', '35', '35', '35', '35', '25', '25', '25', '25', '25', '25', '35', '35', '35', '35', '35', '35', '35', '35', '35', '25', '25', '25', '25', '25', '25', '25', '25', '25_35', '25', '25', '25', '25', '25', '25', '25', '25', '35', '35', '35', '25', '25', '25']

# 压力设置
SET_PRESSURE = ['ambient', '100000', '100000', '110000', '110000', '110000', '100000', '100000', '100000', '70000', '70000', '70000', '100000', '100000', '100000', '100000', '100000', '100000', '110000', '110000', '110000', '100000', '100000', '100000', '70000', '70000', '70000', '100000', '100000', '100000', '100000', '100000', '100000', '100000', '100000', '100000', '100000', 'ambient', 'ambient', 'ambient', 'ambient', 'ambient', 'ambient', '100000', '110000', '100000', '70000', '100000', '100000', 'ambient']

# 湿度设置
SET_HUMIDITY = ['50', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '15_50', '15', '15', '15', '15', '15', '0', '0', '0', '0', '0', '0', '50']

# 传感器模式
SENSOR_MODE = ['30LN', '30LN', '30LN', '30LN', '30LN', '30LN', '30LN', '30LN', '30LN', '30LN', '30LN', '30LN', '30LN', '30LN', '30LN', '240LP', '240LP', '240LP', '30LN', '30LN', '30LN', '30LN', '30LN', '30LN', '30LN', '30LN', '30LN', '30LN', '30LN', '30LN', '240LP', '240LP', '240LP', '30LN', '240LP', '30LN', '30LN', '30LN', '30LN', '30LN', '30LN', '30LN', '30LN', '30LN', '30LN', '30LN', '30LN', '30LN', '240LP', '30LN']

# Drift数据的上下限
DRIFT_UPPER_LIMIT = ['5', '5', '44.5', '200', '200', '20', '200', '200', '20', '200', '200', '20', '200', '200', '20', '200', '200', '20', '1', '10', '0.25', '1', '10', '0.25', '1', '10', '0.25', '1', '10', '0.25', '1', '10', '0.25', '0.65', '1.5', '0.5', '0.5', '0.175', '50', '50', '5', '5', '100', '0.25', '0.1', '0.1', '0.1', '0.1', '0.1', '100000']

DRIFT_LOWER_LIMIT = ['-5', '-5', '-44.5', '-200', '-200', '-20', '-200', '-200', '-20', '-200', '-200', '-20', '-200', '-200', '-20', '-200', '-200', '-20', '-1', '-10', '-0.25', '-1', '-10', '-0.25', '-1', '-10', '-0.25', '-1', '-10', '-0.25', '-1', '-10', '-0.25', '-0.65', '-1.5', '-0.5', '-0.5', '-0.175', '-50', '-50', '-5', '-5', '-100', '-0.25', '-0.1', '-0.1', '-0.1', '-0.1', '-0.1', '-100000']

# TestResult数据的上下限
TESTRESULT_UPPER_LIMIT = ['10', '10', '89', '110200', 'None', '100', '100200', 'None', '100', '70200', 'None', '100', '100200', 'None', '100', '100200', 'None', '100', '37', 'None', '0.5', '37', 'None', '0.5', '37', 'None', '0.5', '27', 'None', '0.5', '27', 'None', '0.5', '1.2', '3', '1', '1', '0.25', '100', '100', '10', '10', '200', '0.5', 'None', 'None', 'None', 'None', 'None', 'None']

TESTRESULT_LOWER_LIMIT = ['0.5', '0.5', '30', '109800', 'None', '-100', '99800', 'None', '-100', '69800', 'None', '-100', '99800', 'None', '-100', '99800', 'None', '-100', '33', 'None', '-0.5', '33', 'None', '-0.5', '33', 'None', '-0.5', '23', 'None', '-0.5', '23', 'None', '-0.5', '0.25', '0.5', '-1', '-1', '-0.25', '-100', '-100', '-10', '-10', '-200', '-0.5', 'None', 'None', 'None', 'None', 'None', 'None']

# 默认工作站配置
DEFAULT_FOLDERS = [
    "TU1_Station0", "TU1_Station1", "TU2_Station0",
    "TU2_Station1", "TU3_Station0", "TU3_Station1"
]
