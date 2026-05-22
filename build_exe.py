"""一键打包脚本 —— 使用 PyInstaller 打包为单文件 EXE"""

import os
import sys
import shutil


def build():
    # 清理旧构建
    for d in ["build", "dist"]:
        if os.path.exists(d):
            shutil.rmtree(d)

    spec_file = "PID仿真系统.spec"

    if os.path.exists(spec_file):
        cmd = f'pyinstaller "{spec_file}"'
    else:
        cmd = (
            'pyinstaller --onefile --windowed '
            '--name "PID温度控制仿真系统" '
            '--add-data "assets;assets" '
            '--add-data "data;data" '
            '--hidden-import pyqtgraph '
            '--hidden-import numpy '
            'src/main.py'
        )

    print(f"执行: {cmd}")
    result = os.system(cmd)

    if result == 0:
        print("\n打包完成！输出文件: dist/PID温度控制仿真系统.exe")
    else:
        print(f"\n打包失败，错误码: {result}")
        sys.exit(1)


if __name__ == "__main__":
    build()
