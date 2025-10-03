# launch.py
import webbrowser
import time
import tkinter as tk
from tkinter import messagebox

def main():
    """
    主函数，用于打开下载链接并显示提示信息。
    """
    download_url = "http://118.145.185.2:3000/release/cognipath-0.9.0.exe"
    
    # 创建一个隐藏的Tkinter根窗口，这样消息框才能弹出
    root = tk.Tk()
    root.withdraw() # 隐藏主窗口

    try:
        print(f"正在尝试打开浏览器并访问下载链接: {download_url}")
        
        # 在默认浏览器中打开下载链接
        webbrowser.open(download_url)
        
        # 显示一个成功的提示框给用户
        messagebox.showinfo(
            "知语AI 下载启动器", 
            "已为您在默认浏览器中打开下载页面。\n\n请在浏览器中完成 CogniPath AI 客户端的下载和安装。\n\n感谢您的使用！"
        )
        
    except Exception as e:
        print(f"发生错误: {e}")
        # 如果出错，也给用户一个提示
        messagebox.showerror(
            "错误",
            f"无法自动打开浏览器。\n\n请手动复制以下链接到您的浏览器地址栏进行下载：\n\n{download_url}"
        )
    finally:
        root.destroy()

if __name__ == "__main__":
    main()
