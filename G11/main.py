# -*- coding: utf-8 -*-
"""
GUM数据处理工具 - 主程序
整合了CSV合并、相减计算、PDF绘图等功能
支持自动扫描路径下所有日期的数据
"""

import os
import sys
import re
from gum_tools import (
    validate_config, merge_csv_files, subtract_csv_files,
    plot_data_to_pdf, plot_diff_to_pdf, scan_gum_data_folders
)


def clear_screen():
    """清屏"""
    os.system('cls' if os.name == 'nt' else 'clear')


def extract_date_range_from_filenames(filenames):
    """
    从文件名列表中提取日期范围
    
    Args:
        filenames: 文件名列表 (如 ['combined_drift_day1_0318.csv', 'combined_drift_day2_0319.csv'])
                   或差值文件名 (如 ['drift_day2_0319-day1_0318.csv'])
    
    Returns:
        tuple: (起始日期, 结束日期) 如 ('0318', '0319')
    """
    dates = []
    for filename in filenames:
        # 匹配 4位数字日期
        found_dates = re.findall(r'(\d{4})', filename)
        dates.extend(found_dates)
    
    # 去重并排序
    unique_dates = sorted(list(set(dates)))
    
    if len(unique_dates) >= 2:
        return (unique_dates[0], unique_dates[-1])
    elif len(unique_dates) == 1:
        return (unique_dates[0], unique_dates[0])
    return ('0000', '0000')


def print_menu():
    """打印主菜单"""
    print("\n" + "=" * 60)
    print("         GUM 数据处理工具 v2.1")
    print("=" * 60)
    print("  1. 自动扫描并合并CSV文件 (推荐)")
    print("  2. 手动合并CSV文件 (TestResult + Drift)")
    print("  3. CSV文件相减计算 (后续天 - 第一天)")
    print("  4. 绘制数据PDF图表")
    print("  5. 绘制差值PDF图表")
    print("  6. 完整流程 (自动扫描 → 合并 → 相减 → 绘图)")
    print("  0. 退出")
    print("=" * 60)


def get_input_path(prompt, default=None):
    """获取输入路径"""
    if default:
        user_input = input(f"{prompt} [默认: {default}]: ").strip()
        return user_input if user_input else default
    return input(f"{prompt}: ").strip()


def select_stations():
    """选择工作站配置"""
    print("\n请选择工作站配置:")
    print("  1. TU1-TU3 全部工作站 (默认)")
    print("  2. TU3 工作站")
    print("  3. 自定义")
    choice = input("请选择 [1-3]: ").strip()

    if choice == "2":
        return ["TU3_Station0", "TU3_Station1"]
    elif choice == "3":
        folder_input = input("请输入工作站名称(用逗号分隔): ").strip()
        return [f.strip() for f in folder_input.split(",")]
    return None


def option_auto_scan_merge():
    """选项1: 自动扫描并合并"""
    print("\n--- 自动扫描并合并CSV文件 ---")
    base_path = get_input_path("请输入GUM数据根路径 (如 E:\\工作数据\\Kibo3\\GUM)")
    if not base_path or not os.path.exists(base_path):
        print("错误: 路径不存在")
        return

    print(f"\n正在扫描 {base_path} 下的GUM数据...")
    date_folders = scan_gum_data_folders(base_path)

    if not date_folders:
        print("未找到包含GUM数据的日期文件夹")
        return

    print(f"\n共发现 {len(date_folders)} 个日期的数据:")
    for i, (name, path) in enumerate(date_folders, 1):
        print(f"  {i}. {name}")

    # 选择工作站
    folders = select_stations()

    # 输出路径
    output_path = get_input_path("\n请输入输出路径", base_path)

    # 处理每个日期，自动分配day编号
    print("\n开始处理...")
    for day_idx, (date_name, date_path) in enumerate(date_folders, start=1):
        # 从日期名提取日期 (如 0318GUM -> 0318)
        date_match = re.search(r'(\d{4})', date_name)
        date_str = date_match.group(1) if date_match else date_name

        print(f"\n处理 Day{day_idx}: {date_name}")
        merge_csv_files(date_path, folders, output_path, date_str, day_idx)


def option_manual_merge():
    """选项2: 手动合并"""
    print("\n--- 手动合并CSV文件 ---")
    base_path = get_input_path("请输入源数据文件夹路径")
    if not base_path or not os.path.exists(base_path):
        print("错误: 路径不存在")
        return

    output_path = get_input_path("请输入输出路径", base_path)
    folders = select_stations()
    date_str = get_input_path("请输入日期 (如 0318)", "0318")
    day_num = get_input_path("请输入天数编号 (如 1, 2)", "1")

    try:
        day_num = int(day_num)
    except ValueError:
        day_num = 1

    merge_csv_files(base_path, folders, output_path, date_str, day_num)


def option_subtract():
    """选项3: CSV文件相减"""
    print("\n--- CSV文件相减 ---")
    print("提示: 请输入包含合并后CSV文件的文件夹")
    print("      (如执行合并后输出路径，包含 combined_testresult_xxxx.csv 等文件)")
    folder_path = get_input_path("请输入CSV文件所在文件夹路径")
    if not folder_path or not os.path.exists(folder_path):
        print("错误: 路径不存在")
        return

    print("\n请选择文件类型:")
    print("  1. TestResult")
    print("  2. Drift")
    choice = input("请选择 [1-2]: ").strip()

    file_type = "drift" if choice == "2" else "testresult"
    subtract_csv_files(folder_path, file_type)


def option_plot():
    """选项4: 绘制数据PDF图表"""
    print("\n--- 绘制数据PDF图表 ---")
    folder_path = get_input_path("请输入CSV文件所在文件夹路径")
    if not folder_path or not os.path.exists(folder_path):
        print("错误: 路径不存在")
        return

    print("\n请选择数据类型:")
    print("  1. TestResult")
    print("  2. Drift")
    choice = input("请选择 [1-2]: ").strip()

    data_type = "drift" if choice == "2" else "testresult"
    prefix = f"combined_{data_type}"

    # 扫描文件夹中的合并文件
    csv_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path)
                 if f.endswith('.csv') and f.startswith(prefix)]

    if not csv_files:
        print(f"错误: 未找到 {prefix}*.csv 文件")
        return

    print(f"\n找到 {len(csv_files)} 个文件:")
    for i, f in enumerate(csv_files, 1):
        print(f"  {i}. {os.path.basename(f)}")

    # 选择文件
    print("\n请选择要绑制的文件:")
    print("  0. 全部绘制")
    for i, f in enumerate(csv_files, 1):
        print(f"  {i}. {os.path.basename(f)}")

    select = input("请选择 [0-{}] (多个用逗号分隔): ".format(len(csv_files))).strip()

    if select == "0":
        selected_files = csv_files
    else:
        try:
            indices = [int(x.strip()) - 1 for x in select.split(",")]
            selected_files = [csv_files[i] for i in indices if 0 <= i < len(csv_files)]
        except (ValueError, IndexError):
            print("输入无效，将绑制全部文件")
            selected_files = csv_files

    # 提取日期范围生成文件名
    start_date, end_date = extract_date_range_from_filenames(
        [os.path.basename(f) for f in selected_files]
    )
    default_pdf_name = f"{data_type}_{start_date}_{end_date}.pdf"
    output_pdf = get_input_path("\n请输入输出PDF文件名", default_pdf_name)

    plot_data_to_pdf(selected_files, output_pdf, data_type)


def option_plot_diff():
    """选项5: 绘制差值PDF图表"""
    print("\n--- 绘制差值PDF图表 ---")
    folder_path = get_input_path("请输入CSV文件所在文件夹路径")
    if not folder_path or not os.path.exists(folder_path):
        print("错误: 路径不存在")
        return

    print("\n请选择数据类型:")
    print("  1. TestResult")
    print("  2. Drift")
    choice = input("请选择 [1-2]: ").strip()

    data_type = "drift" if choice == "2" else "testresult"

    # 扫描差值文件 (如 testresult_day2_0319-day1_0318.csv)
    diff_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path)
                  if f.endswith('.csv') and f.startswith(data_type) and '-day' in f]

    if not diff_files:
        print(f"错误: 未找到 {data_type}*_day*-day*.csv 差值文件")
        return

    print(f"\n找到 {len(diff_files)} 个差值文件:")
    for i, f in enumerate(diff_files, 1):
        print(f"  {i}. {os.path.basename(f)}")

    # 选择文件
    print("\n请选择要绑制的文件:")
    print("  0. 全部绘制")
    for i, f in enumerate(diff_files, 1):
        print(f"  {i}. {os.path.basename(f)}")

    select = input("请选择 [0-{}] (多个用逗号分隔): ".format(len(diff_files))).strip()

    if select == "0":
        selected_files = diff_files
    else:
        try:
            indices = [int(x.strip()) - 1 for x in select.split(",")]
            selected_files = [diff_files[i] for i in indices if 0 <= i < len(diff_files)]
        except (ValueError, IndexError):
            print("输入无效，将绑制全部文件")
            selected_files = diff_files

    # 提取日期范围生成文件名
    start_date, end_date = extract_date_range_from_filenames(
        [os.path.basename(f) for f in selected_files]
    )
    default_pdf_name = f"{data_type}-day1_{start_date}_{end_date}.pdf"
    output_pdf = get_input_path("\n请输入输出PDF文件名", default_pdf_name)

    plot_diff_to_pdf(selected_files, output_pdf, data_type)


def option_full_workflow():
    """选项6: 完整流程"""
    print("\n--- 完整流程 ---")
    print("此流程将依次执行: 自动扫描 → 合并CSV → 相减计算 → 绘制PDF")

    # 步骤1: 扫描数据
    print("\n[步骤1] 扫描GUM数据")
    base_path = get_input_path("请输入GUM数据根路径 (如 E:\\工作数据\\Kibo3\\GUM)")
    if not base_path or not os.path.exists(base_path):
        print("错误: 路径不存在")
        return

    print(f"\n正在扫描 {base_path} 下的GUM数据...")
    date_folders = scan_gum_data_folders(base_path)

    if not date_folders:
        print("未找到包含GUM数据的日期文件夹")
        return

    print(f"\n共发现 {len(date_folders)} 个日期的数据:")
    for i, (name, path) in enumerate(date_folders, 1):
        print(f"  {i}. {name}")

    # 选择工作站和输出路径
    folders = select_stations()
    output_path = get_input_path("\n请输入输出路径", base_path)

    # 步骤2: 合并CSV
    print("\n[步骤2] 合并CSV文件")
    combined_files = {"testresult": [], "drift": []}

    for day_idx, (date_name, date_path) in enumerate(date_folders, start=1):
        date_match = re.search(r'(\d{4})', date_name)
        date_str = date_match.group(1) if date_match else date_name

        print(f"\n处理 Day{day_idx}: {date_name}")
        merge_csv_files(date_path, folders, output_path, date_str, day_idx)

        # 记录生成的文件路径
        combined_files["testresult"].append(
            os.path.join(output_path, f"combined_testresult_day{day_idx}_{date_str}.csv"))
        combined_files["drift"].append(
            os.path.join(output_path, f"combined_drift_day{day_idx}_{date_str}.csv"))

    # 步骤3: 相减计算
    print("\n[步骤3] 相减计算")
    testresult_folder = output_path
    drift_folder = output_path

    subtract_csv_files(testresult_folder, "testresult")
    subtract_csv_files(drift_folder, "drift")

    # 步骤4: 绘制PDF
    print("\n[步骤4] 绘制PDF图表")

    # 提取日期范围
    all_dates = []
    for date_name, _ in date_folders:
        date_match = re.search(r'(\d{4})', date_name)
        if date_match:
            all_dates.append(date_match.group(1))
    start_date = all_dates[0] if all_dates else '0000'
    end_date = all_dates[-1] if all_dates else '0000'

    # 查找差值文件（所有差值文件）
    testresult_diff_files = []
    drift_diff_files = []

    if os.path.exists(testresult_folder):
        testresult_diff_files = [os.path.join(testresult_folder, f)
                                 for f in os.listdir(testresult_folder)
                                 if f.startswith("testresult") and '-day' in f]
    if os.path.exists(drift_folder):
        drift_diff_files = [os.path.join(drift_folder, f)
                           for f in os.listdir(drift_folder)
                           if f.startswith("drift") and '-day' in f]

    # 绘制合并数据图表
    valid_testresult = [f for f in combined_files["testresult"] if os.path.exists(f)]
    valid_drift = [f for f in combined_files["drift"] if os.path.exists(f)]

    if valid_testresult:
        plot_data_to_pdf(valid_testresult,
                        os.path.join(output_path, f"testresult_{start_date}_{end_date}.pdf"),
                        "testresult")
    if valid_drift:
        plot_data_to_pdf(valid_drift,
                        os.path.join(output_path, f"drift_{start_date}_{end_date}.pdf"),
                        "drift")

    # 绘制差值图表（传入所有差值文件列表）
    if testresult_diff_files:
        plot_diff_to_pdf(testresult_diff_files,
                        os.path.join(output_path, f"testresult-day1_{start_date}_{end_date}.pdf"),
                        "testresult")
    if drift_diff_files:
        plot_diff_to_pdf(drift_diff_files,
                        os.path.join(output_path, f"drift-day1_{start_date}_{end_date}.pdf"),
                        "drift")

    print("\n" + "=" * 50)
    print("完整流程执行完毕!")
    print(f"输出目录: {output_path}")
    print("=" * 50)


def main():
    """主函数"""
    validate_config()

    while True:
        print_menu()
        choice = input("请选择操作 [0-6]: ").strip()

        if choice == "0":
            print("再见!")
            break
        elif choice == "1":
            option_auto_scan_merge()
        elif choice == "2":
            option_manual_merge()
        elif choice == "3":
            option_subtract()
        elif choice == "4":
            option_plot()
        elif choice == "5":
            option_plot_diff()
        elif choice == "6":
            option_full_workflow()
        else:
            print("无效选择，请重新输入")

        input("\n按回车键继续...")


if __name__ == "__main__":
    main()
