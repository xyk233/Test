# -*- coding: utf-8 -*-
"""GUM数据处理核心模块"""

import os
import re
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.ticker import MultipleLocator

from config import (
    SKIP_COLUMNS, SET_TEMPERATURE, SET_PRESSURE, SET_HUMIDITY, SENSOR_MODE,
    DRIFT_UPPER_LIMIT, DRIFT_LOWER_LIMIT, TESTRESULT_UPPER_LIMIT, TESTRESULT_LOWER_LIMIT,
    DEFAULT_FOLDERS
)


def validate_config():
    """验证配置参数长度一致性"""
    assert len(SKIP_COLUMNS) == len(SET_TEMPERATURE) == len(SET_PRESSURE) == \
           len(SET_HUMIDITY) == len(SENSOR_MODE), "参数列表长度不匹配"
    print(f"配置验证通过，共 {len(SKIP_COLUMNS)} 个参数列")


def scan_gum_data_folders(base_path):
    """
    扫描基础路径下所有包含GUM数据的日期文件夹
    
    Args:
        base_path: 基础路径 (如 E:\工作数据\Kibo3\GUM)
    
    Returns:
        list: 包含(日期名, 数据路径)的列表
    """
    date_folders = []
    
    # 匹配日期模式：文件夹名中包含日期 如 0318GUM, day1_0318 等
    date_pattern = re.compile(r'(\d{4})')
    
    for item in os.listdir(base_path):
        item_path = os.path.join(base_path, item)
        if os.path.isdir(item_path):
            # 检查是否包含日期标识
            date_match = date_pattern.search(item)
            if date_match:
                # 检查该文件夹下是否有工作站数据
                has_station_data = False
                for root, dirs, files in os.walk(item_path):
                    for d in dirs:
                        if 'Station' in d:
                            has_station_data = True
                            break
                    if has_station_data:
                        break
                
                if has_station_data:
                    date_folders.append((item, item_path))
                    print(f"  发现数据: {item} -> {item_path}")
    
    # 按日期排序
    date_folders.sort(key=lambda x: x[0])
    return date_folders


def merge_csv_files(base_path, folders=None, output_path=None, date_str="", day_num=1):
    """
    合并多个文件夹中的TestResult和Drift CSV文件

    Args:
        base_path: 基础路径
        folders: 文件夹名称列表
        output_path: 输出路径
        date_str: 日期字符串 (如 0318)
        day_num: 天数编号 (如 1, 2)
    """
    if folders is None:
        folders = DEFAULT_FOLDERS

    if output_path is None:
        output_path = base_path

    testresult_dfs = []
    drift_dfs = []

    for folder_index, search_string in enumerate(folders):
        folder_path = None
        for root, dirs, files in os.walk(base_path):
            for dir_name in dirs:
                if search_string in dir_name:
                    folder_path = os.path.join(root, dir_name)
                    print(f"找到文件夹: {folder_path}")
                    break
            if folder_path:
                break

        if not folder_path:
            print(f"警告: 未找到包含 '{search_string}' 的文件夹")
            continue

        # 查找TestResult和Drift文件
        try:
            testresult_file = next(f for f in os.listdir(folder_path) if "TestResult" in f)
            drift_file = next(f for f in os.listdir(folder_path) if "Drift" in f)
        except StopIteration:
            print(f"警告: {folder_path} 中未找到TestResult或Drift文件")
            continue

        # 读取TestResult文件
        testresult_path = os.path.join(folder_path, testresult_file)
        testresult_df = None
        for encoding in ['gbk', 'utf-8', 'latin-1', 'cp1252']:
            try:
                testresult_df = pd.read_csv(testresult_path, skiprows=19, encoding=encoding)
                break
            except (UnicodeDecodeError, pd.errors.ParserError):
                continue
        if testresult_df is None:
            print(f"警告: 无法读取 {testresult_file}，跳过")
            continue
        if folder_index == 0:
            testresult_df_1 = testresult_df.drop(index=range(0, 10))
        else:
            testresult_df_1 = testresult_df.drop(index=range(10))
        testresult_df_1 = testresult_df_1.drop(testresult_df_1.columns[1:23], axis=1)
        testresult_dfs.append(testresult_df_1)

        # 读取Drift文件
        drift_path = os.path.join(folder_path, drift_file)
        drift_df = None
        for encoding in ['gbk', 'utf-8', 'latin-1', 'cp1252']:
            try:
                drift_df = pd.read_csv(drift_path, skiprows=19, encoding=encoding)
                break
            except (UnicodeDecodeError, pd.errors.ParserError):
                continue
        if drift_df is None:
            print(f"警告: 无法读取 {drift_file}，跳过")
            continue
        if folder_index == 0:
            drift_df_1 = drift_df.drop(index=range(0, 10))
        else:
            drift_df_1 = drift_df.drop(index=range(10))
        drift_df_1 = drift_df_1.drop(drift_df_1.columns[1:23], axis=1)
        drift_dfs.append(drift_df_1)

    if not testresult_dfs or not drift_dfs:
        print("错误: 没有找到有效的数据文件")
        return None, None

    # 合并文件
    combined_testresult = pd.concat(testresult_dfs, ignore_index=True)
    combined_drift = pd.concat(drift_dfs, ignore_index=True)

    # 保存文件 - 格式: combined_drift_day1_0318.csv
    testresult_output = os.path.join(output_path, f"combined_testresult_day{day_num}_{date_str}.csv")
    drift_output = os.path.join(output_path, f"combined_drift_day{day_num}_{date_str}.csv")

    combined_testresult.to_csv(testresult_output, index=False)
    combined_drift.to_csv(drift_output, index=False)

    print(f"合并完成:")
    print(f"  - {testresult_output}")
    print(f"  - {drift_output}")

    return combined_testresult, combined_drift


def subtract_csv_files(folder_path, file_type="testresult"):
    """
    对CSV文件进行相减计算（后续天减去第一天）

    Args:
        folder_path: CSV文件所在文件夹
        file_type: 文件类型 (testresult/drift)
    """
    # 只选择匹配类型的合并文件
    prefix = f"combined_{file_type}"
    csv_files = [f for f in os.listdir(folder_path) 
                 if f.endswith('.csv') and f.startswith(prefix)]

    if len(csv_files) < 2:
        print(f"错误: 在 {folder_path} 中只找到 {len(csv_files)} 个 {prefix}*.csv 文件")
        print(f"提示: 需要先执行'合并CSV文件'操作生成 combined_{file_type}_xxxx.csv 文件")
        return

    # 提取日期字符串并排序
    def extract_date_str(filename):
        # 优先匹配 day1_0318 格式
        match = re.search(r'(day\d+_\d+)', filename)
        if match:
            return match.group(1)
        # 其次匹配 _0318 格式
        match = re.search(r'_(\d{4})(?:\.csv)?$', filename)
        if match:
            return match.group(1)
        return "0000"

    def extract_date_num(filename):
        """用于排序的数值"""
        date_str = extract_date_str(filename)
        # 提取纯数字
        nums = re.findall(r'\d+', date_str)
        return int(''.join(nums)) if nums else 0

    csv_files.sort(key=extract_date_num)
    print(f"找到 {len(csv_files)} 个CSV文件:")
    for f in csv_files:
        print(f"  - {f}")

    # 提取基准文件的日期
    base_date = extract_date_str(csv_files[0])
    # 尝试多种编码读取基准文件
    df1 = None
    for encoding in ['gbk', 'utf-8', 'latin-1', 'cp1252']:
        try:
            df1 = pd.read_csv(os.path.join(folder_path, csv_files[0]), encoding=encoding)
            break
        except (UnicodeDecodeError, pd.errors.ParserError):
            continue
    if df1 is None:
        print(f"错误: 无法读取基准文件 {csv_files[0]}")
        return
    print(f"\n基准文件: {csv_files[0]} (日期: {base_date})")

    for i in range(1, len(csv_files)):
        # 尝试多种编码读取当前文件
        df2 = None
        for encoding in ['gbk', 'utf-8', 'latin-1', 'cp1252']:
            try:
                df2 = pd.read_csv(os.path.join(folder_path, csv_files[i]), encoding=encoding)
                break
            except (UnicodeDecodeError, pd.errors.ParserError):
                continue
        if df2 is None:
            print(f"警告: 无法读取文件 {csv_files[i]}，跳过")
            continue

        # 提取当前文件的日期
        current_date = extract_date_str(csv_files[i])

        if df1.columns.equals(df2.columns):
            result = df2 - df1
            # 格式: drift_day2_0319-day1_0318.csv 或 drift_day0319-day0318.csv
            # 如果日期已包含day前缀则直接使用，否则添加day前缀
            current_suffix = current_date if current_date.startswith('day') else f'day{current_date}'
            base_suffix = base_date if base_date.startswith('day') else f'day{base_date}'
            output_file = os.path.join(folder_path, f'{file_type}_{current_suffix}-{base_suffix}.csv')
            result.to_csv(output_file, index=False)
            print(f"已保存: {output_file}")
        else:
            print(f"警告: {csv_files[i]} 的列与基准文件不匹配，跳过")


def plot_data_to_pdf(csv_files, output_pdf, data_type="drift"):
    """
    将CSV数据绘制为PDF图表

    Args:
        csv_files: CSV文件路径列表
        output_pdf: 输出PDF文件路径
        data_type: 数据类型 (drift/testresult)
    """
    upper_limits = DRIFT_UPPER_LIMIT if data_type == "drift" else TESTRESULT_UPPER_LIMIT
    lower_limits = DRIFT_LOWER_LIMIT if data_type == "drift" else TESTRESULT_LOWER_LIMIT

    with PdfPages(output_pdf) as pdf:
        for col in SKIP_COLUMNS:
            plt.figure(figsize=(12, 6))

            upper_limit = upper_limits[SKIP_COLUMNS.index(col)]
            lower_limit = lower_limits[SKIP_COLUMNS.index(col)]

            for file in csv_files:
                csv_name = os.path.basename(file)
                # 尝试多种编码读取文件
                df = None
                for encoding in ['gbk', 'utf-8', 'latin-1', 'cp1252']:
                    try:
                        df = pd.read_csv(file, encoding=encoding)
                        break
                    except (UnicodeDecodeError, pd.errors.ParserError):
                        continue
                    except Exception as e:
                        print(f"警告: 读取文件 {csv_name} 时出错: {e}")
                        continue

                if df is None:
                    print(f"警告: 无法读取文件 {csv_name}，已跳过")
                    continue

                if col in df.columns:
                    data = df[col].fillna(0)

                    if upper_limit != 'None' and lower_limit != 'None':
                        data = np.clip(data, float(lower_limit), float(upper_limit))

                    plt.plot(data, label=csv_name)

            if upper_limit != 'None' and lower_limit != 'None':
                up = float(upper_limit) + 0.5
                down = float(lower_limit) - 0.5
                plt.ylim(down, up)
                plt.axhline(y=float(upper_limit), color='g', linestyle='--',
                           label=f"Upper limit: {upper_limit}")
                plt.axhline(y=float(lower_limit), color='r', linestyle='--',
                           label=f"Lower limit: {lower_limit}")

            plt.title(f"Column: {col}\n"
                     f"Temp: {SET_TEMPERATURE[SKIP_COLUMNS.index(col)]}°C, "
                     f"Pressure: {SET_PRESSURE[SKIP_COLUMNS.index(col)]}Pa, "
                     f"Humidity: {SET_HUMIDITY[SKIP_COLUMNS.index(col)]}%, "
                     f"Mode: {SENSOR_MODE[SKIP_COLUMNS.index(col)]}")
            plt.xlabel('Sample Index')
            plt.ylabel('Value')

            ax = plt.gca()
            ax.xaxis.set_major_locator(MultipleLocator(128))
            ax.xaxis.set_minor_locator(MultipleLocator(16))
            ax.xaxis.set_minor_formatter(plt.FormatStrFormatter('%d'))
            ax.tick_params(axis='x', which='major', labelsize=8)
            ax.tick_params(axis='x', which='minor', labelsize=4)

            plt.xticks(rotation=45)
            plt.legend(loc='upper left', bbox_to_anchor=(1, 1))
            plt.tight_layout()
            pdf.savefig()
            plt.close()

    print(f"PDF已生成: {output_pdf}")


def plot_diff_to_pdf(csv_files, output_pdf, data_type="drift"):
    """
    将差值数据绘制为PDF图表

    Args:
        csv_files: 差值CSV文件路径列表（支持多个文件）
        output_pdf: 输出PDF文件路径
        data_type: 数据类型 (drift/testresult)
    """
    # 兼容旧版本：如果传入单个字符串路径，转为列表
    if isinstance(csv_files, str):
        csv_files = [csv_files]

    # 差值数据始终使用DRIFT的门限
    upper_limits = DRIFT_UPPER_LIMIT
    lower_limits = DRIFT_LOWER_LIMIT

    with PdfPages(output_pdf) as pdf:
        for col in SKIP_COLUMNS:
            plt.figure(figsize=(12, 6))

            upper_limit = upper_limits[SKIP_COLUMNS.index(col)]
            lower_limit = lower_limits[SKIP_COLUMNS.index(col)]

            # 遍历所有差值文件
            for csv_file in csv_files:
                csv_name = os.path.basename(csv_file)
                # 尝试多种编码读取文件
                df = None
                for encoding in ['gbk', 'utf-8', 'latin-1', 'cp1252']:
                    try:
                        df = pd.read_csv(csv_file, encoding=encoding)
                        break
                    except (UnicodeDecodeError, pd.errors.ParserError):
                        continue
                    except Exception as e:
                        print(f"警告: 读取文件 {csv_name} 时出错: {e}")
                        continue

                if df is None:
                    print(f"警告: 无法读取文件 {csv_name}，已跳过")
                    continue

                if col in df.columns:
                    data = df[col].fillna(0)

                    if upper_limit != 'None' and lower_limit != 'None':
                        data = np.clip(data, float(lower_limit), float(upper_limit))

                    plt.plot(data, label=csv_name)

            if upper_limit != 'None' and lower_limit != 'None':
                up = float(upper_limit) + 0.5
                down = float(lower_limit) - 0.5
                plt.ylim(down, up)
                plt.axhline(y=float(upper_limit), color='g', linestyle='--',
                           label=f"Upper limit: {upper_limit}")
                plt.axhline(y=float(lower_limit), color='r', linestyle='--',
                           label=f"Lower limit: {lower_limit}")

            plt.title(f"Column: {col}\n"
                     f"Temp: {SET_TEMPERATURE[SKIP_COLUMNS.index(col)]}°C, "
                     f"Pressure: {SET_PRESSURE[SKIP_COLUMNS.index(col)]}Pa, "
                     f"Humidity: {SET_HUMIDITY[SKIP_COLUMNS.index(col)]}%, "
                     f"Mode: {SENSOR_MODE[SKIP_COLUMNS.index(col)]}")
            plt.xlabel('Sample Index')
            plt.ylabel('Value')

            ax = plt.gca()
            ax.xaxis.set_major_locator(MultipleLocator(128))
            ax.xaxis.set_minor_locator(MultipleLocator(16))
            ax.xaxis.set_minor_formatter(plt.FormatStrFormatter('%d'))
            ax.tick_params(axis='x', which='major', labelsize=8)
            ax.tick_params(axis='x', which='minor', labelsize=4)

            plt.xticks(rotation=45)
            plt.legend(loc='upper left', bbox_to_anchor=(1, 1))
            plt.tight_layout()
            pdf.savefig()
            plt.close()

    print(f"PDF已生成: {output_pdf}")
