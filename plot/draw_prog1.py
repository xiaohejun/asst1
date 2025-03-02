import subprocess
import json
import os
from pathlib import Path
import multiprocessing
import re
import matplotlib.pyplot as plt
import numpy as np
import datetime

PROG1_DIR_NAME = "prog1_mandelbrot_threads"
PROG1_NAME = "mandelbrot"

def ShellCommand(command):
    # 调用 Shell 命令
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0 or len(result.stderr) > 0:
        raise RuntimeError(f"""Something Wrong When 
            exec shell command {command}, 
            returncode: {result.returncode}, 
            stderr: {result.stderr},
            stdout: {result.stdout}""")
    print(f"Exec command:\n {command}")
    # print(f"Stdout:\n {result.stdout}")
    return result

def GetWorkDir():
    # 获取当前脚本的绝对路径
    current_file_path = Path(__file__).resolve()
    # 获取当前脚本所在的目录
    current_dir = current_file_path.parent
    # 获取上一层的目录
    parent_dir = current_dir.parent
    return parent_dir

def CompileProg(prog_dir):
    ret = ShellCommand(f"cd {os.path.join(GetWorkDir(), prog_dir)} && make")
    print("compile prog finished .....")
    return ret

def ParseResult1(text : str):
    numbers = []
    for line in text.split():
        match = re.search(r'\[(\d+\.\d+)\]', line)
        if match:
            number = match.group(0)
            numbers.append(float(number[1:-1]))
    if len(numbers) != 2:
        raise RuntimeError(f"ParseResult Failed! text {text}, numbers {numbers}")
    return numbers

def RunProg1():
    data = {
        "v1": {
            "t": [],
            "s": [],
            "m": [],
            "sp": []
        },
        "v2": {
            "t": [],
            "s": [],
            "m": [],
            "sp": []
        }
    }
    max_thread_num = multiprocessing.cpu_count() * 3 + 1
    prog1 = f"{os.path.join(GetWorkDir(), PROG1_DIR_NAME, PROG1_NAME)}"
    for v in range(1, 3):
        for t in range(2, max_thread_num):
            result = ShellCommand(f"{prog1} -v {v} -t {t}")
            exec_time =  ParseResult1(result.stdout)
            data[f"v{v}"]["t"].append(t)
            data[f"v{v}"]["s"].append(exec_time[0])
            data[f"v{v}"]["m"].append(exec_time[1])
            data[f"v{v}"]["sp"].append(round(exec_time[0] / exec_time[1], 2))
    print("run prog finished .....")
    return data

def PlotProg1Info(data):
    # data = {'v1': {'t': [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15], 's': [676.718, 672.819, 673.478, 673.188, 673.319, 673.086, 673.396, 672.928, 673.058, 672.917, 673.229, 673.97, 673.233, 672.908], 'm': [340.23, 410.912, 274.266, 269.888, 205.341, 196.242, 165.416, 154.483, 136.19, 128.4, 119.579, 115.227, 110.101, 105.635], 'sp': [1.99, 1.64, 2.46, 2.49, 3.28, 3.43, 4.07, 4.36, 4.94, 5.24, 5.63, 5.85, 6.11, 6.37]}, 'v2': {'t': [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15], 's': [354.81, 354.891, 355.306, 354.912, 355.201, 354.893, 354.727, 354.406, 354.124, 354.905, 354.512, 354.826, 354.772, 354.825], 'm': [213.691, 168.085, 144.637, 127.017, 112.412, 99.02, 90.206, 82.856, 79.135, 78.364, 72.074, 77.985, 67.433, 69.675], 'sp': [1.66, 2.11, 2.46, 2.79, 3.16, 3.58, 3.93, 4.28, 4.47, 4.53, 4.92, 4.55, 5.26, 5.09]}}
    # 获取当前时间
    now = datetime.datetime.now()
    # 格式化当前时间为字符串，包含秒
    timestamp = now.strftime("%Y-%m-%d_%H:%M:%S")
    # 创建文件名
    data_file = f"prog1_data_{timestamp}.txt"
    img_file = f"prog1_img_{timestamp}.jpg"
    # 记录数据
    with open(data_file, 'w') as f:
        json.dump(data, f, indent=4)

    print(data)
    data_v1 = data["v1"]
    data_v2 = data["v2"]

    # 理想状态
    plt.plot(data_v1["t"], data_v1["t"], "r^-", label="ideal")

    # 绘制 v1 的数据，用绿色三角形和实线连接
    plt.plot(data_v1["t"], data_v1["sp"], "g^-", label="view1")

    # 绘制 v2 的数据，用蓝色圆点和实线连接
    plt.plot(data_v2["t"], data_v2["sp"], "bo-", label="view2")

    # 设置 x 轴刻度
    # all_ticks = sorted(set(data_v1["t"] + data_v2["t"]))  # 合并并去重
    # plt.xticks(all_ticks)
    # 设置 x 轴刻度（间距为 1）
    x_ticks = np.arange(min(data_v1["t"] + data_v2["t"]), max(data_v1["t"] + data_v2["t"]) + 2, 1)
    plt.xticks(x_ticks)
    # 设置 y 轴刻度（间距为 1）
    plt.yticks(x_ticks)

    # 添加网格线
    plt.grid(True)

    # 添加图例
    plt.legend()

    # 添加标题和标签
    plt.title(f"{timestamp} \n Prog1 Speedup vs Number of threads")
    plt.xlabel("Number of threads, np")
    plt.ylabel(r"$\text{Speedup} = \frac{T_{\text{1}}}{T_{\text{np}}}$")

    # 保存图像
    plt.savefig(img_file)

def Main():
    try:
        CompileProg(PROG1_DIR_NAME)
        data = RunProg1()
        # data = {}
        PlotProg1Info(data)
    except Exception as e:
        print(e)

if __name__ == '__main__':
    Main()