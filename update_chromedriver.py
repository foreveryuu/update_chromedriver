"""
脚本功能说明：
----------------
本脚本用于自动下载并更新 ChromeDriver，以匹配指定的 Chrome 浏览器版本前缀。脚本从 Google 官方提供的
JSON 文件中查找最接近指定版本的 ChromeDriver 下载链接，下载并解压 ChromeDriver 到本地，最后返回该
ChromeDriver 的路径。

核心功能：
1. 根据当前操作系统（Windows、macOS、Linux）确定 ChromeDriver 对应的版本。
2. 根据指定的 Chrome 浏览器版本前缀查找最接近的 ChromeDriver 版本。
3. 下载并解压找到的 ChromeDriver 文件。
4. 提供解压后的 ChromeDriver 可执行文件路径，用于后续自动化任务。

优化点：
----------------
1. **平台检测**：通过 platform 模块自动识别系统，确保下载对应系统的 ChromeDriver。
2. **版本匹配**：根据 Chrome 版本前缀查找最接近的 ChromeDriver 版本，避免版本不兼容问题。
3. **自动下载和解压**：实现下载后自动解压文件，并删除临时压缩包。
4. **异常处理**：增加了详细的异常处理，以应对网络、解压、文件系统等可能出现的错误。

脚本运行要求：
----------------
- 安装 requests 库用于网络请求。
- 安装 zipfile 库用于解压文件（Python 自带）。
- 正确配置 Chrome 浏览器版本前缀。
"""


import requests
import os
import zipfile
import platform

def get_platform_name():
    """返回当前操作系统的名称"""
    system = platform.system()
    if system == 'Windows':
        return 'win32'
    elif system == 'Darwin':
        return 'mac-arm64'
    elif system == 'Linux':
        return 'linux64'
    else:
        raise RuntimeError(f'不支持的操作系统: {system}')

def fetch_closest_chromedriver_url(chrome_version_prefix):
    """根据 Chrome 版本前缀获取最接近的 ChromeDriver 下载链接"""
    json_url = 'https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json'
    try:
        response = requests.get(json_url)
        response.raise_for_status()  # 检查请求是否成功
        data = response.json()
        # 输出获取到的 JSON 数据
        platform_name = get_platform_name()
        print(f'平台名称: {platform_name}')  # 打印平台名称

        for version_info in data['versions']:
            if version_info['version'].startswith(chrome_version_prefix):
                for download in version_info['downloads']['chromedriver']:
                    if platform_name in download['platform']:
                        print(f'找到匹配的 ChromeDriver 下载链接: {download["url"]}')
                        return download['url'], version_info['version']
        print(f'未找到匹配的 ChromeDriver。')
    except requests.RequestException as e:
        print(f'请求错误: {e}')
    except Exception as e:
        print(f'发生错误: {e}')
    return None, None

def download_and_update_chromedriver(version_prefix='128'):
    """下载并更新 ChromeDriver"""
    driver_url, actual_version = fetch_closest_chromedriver_url(version_prefix)
    if not driver_url:
        print(f'未找到适合 Chrome 版本前缀 {version_prefix} 的 ChromeDriver！')
        return ''

    base_path = os.path.dirname(os.path.abspath(__file__))  # 当前脚本所在目录
    zip_path = os.path.join(base_path, f'chromedriver_{actual_version}.zip')
    extract_dir = os.path.join(base_path, f'chromedriver_{actual_version}')

    print(f'下载 ChromeDriver {actual_version}...')
    try:
        response = requests.get(driver_url)
        response.raise_for_status()  # 检查请求是否成功
        with open(zip_path, 'wb') as f:
            f.write(response.content)
        print(f'ChromeDriver {actual_version} 下载成功！')

        print(f'解压 ChromeDriver {actual_version}...')
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)

        driver_file = None
        for root, dirs, files in os.walk(extract_dir):
            for file in files:
                if file.startswith('chromedriver'):
                    driver_file = os.path.join(root, file)
                    break
            if driver_file:
                break

        if driver_file:
            os.remove(zip_path)
            print(f'ChromeDriver 文件路径: {driver_file}')
            return driver_file
        else:
            print('未能找到解压后的 chromedriver 文件。')
            return ''
    except requests.RequestException as e:
        print(f'下载错误: {e}')
    except zipfile.BadZipFile:
        print('解压错误: 文件格式不正确或损坏')
    except Exception as e:
        print(f'发生错误: {e}')
    return ''


if __name__ == "__main__":
    print("脚本开始执行")
    download_and_update_chromedriver()