#!/usr/bin/env python3
"""
Gossip算法动态可视化项目
主程序入口

作者: AI Assistant
版本: 1.0.0
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from visualization import GossipVisualization
except ImportError as e:
    print(f"导入错误: {e}")
    print("请确保所有必要的文件都在正确的位置")
    sys.exit(1)


def main():
    """主函数"""
    try:
        # 创建主窗口
        root = tk.Tk()
        
        # 设置窗口图标和属性
        root.resizable(True, True)
        root.minsize(1000, 700)
        
        # 创建应用实例
        app = GossipVisualization(root)
        
        # 设置窗口关闭事件
        def on_closing():
            if messagebox.askokcancel("退出", "确定要退出Gossip算法可视化程序吗？"):
                app.is_running = False
                root.destroy()
        
        root.protocol("WM_DELETE_WINDOW", on_closing)
        
        # 显示欢迎信息
        messagebox.showinfo(
            "欢迎", 
            "欢迎使用Gossip算法动态可视化工具！\n\n"
            "功能说明：\n"
            "• 点击'开始模拟'开始传播过程\n"
            "• 使用滑块调节各种参数\n"
            "• 观察不同参数对传播效果的影响\n"
            "• 绿色=易感染，红色=已感染，灰色=已移除"
        )
        
        # 启动GUI主循环
        root.mainloop()
        
    except Exception as e:
        error_msg = f"程序运行出错: {str(e)}"
        print(error_msg)
        if 'root' in locals():
            messagebox.showerror("错误", error_msg)
        sys.exit(1)


if __name__ == "__main__":
    main()