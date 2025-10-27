"""
Gossip算法可视化界面
使用tkinter实现交互式图形界面
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import math
from typing import Dict, List, Tuple
from gossip_algorithm import GossipSimulator, NodeState


class GossipVisualization:
    """Gossip算法可视化类"""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Gossip算法动态可视化")
        self.root.geometry("1200x800")
        
        # 模拟器
        self.simulator = GossipSimulator(num_nodes=50, width=800, height=600)
        
        # 可视化参数
        self.node_radius = 8
        self.colors = {
            NodeState.SUSCEPTIBLE: "#4CAF50",  # 绿色
            NodeState.INFECTED: "#F44336",     # 红色
            NodeState.REMOVED: "#9E9E9E"       # 灰色
        }
        
        # 动画控制
        self.is_running = False
        self.animation_speed = 100  # 毫秒
        
        # GUI组件
        self.canvas = None
        self.control_frame = None
        self.stats_frame = None
        
        self._setup_gui()
        self._draw_initial_network()
        
    def _setup_gui(self):
        """设置GUI界面"""
        # 主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 左侧控制面板
        self.control_frame = ttk.LabelFrame(main_frame, text="控制面板", width=350)
        self.control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        self.control_frame.pack_propagate(False)
        
        # 右侧可视化区域
        viz_frame = ttk.Frame(main_frame)
        viz_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # 画布
        self.canvas = tk.Canvas(viz_frame, bg="white", width=800, height=600)
        self.canvas.pack(pady=(0, 10))
        
        # 统计信息框架
        self.stats_frame = ttk.LabelFrame(viz_frame, text="统计信息")
        self.stats_frame.pack(fill=tk.X)
        
        self._setup_controls()
        self._setup_stats_display()
        
    def _setup_controls(self):
        """设置控制面板"""
        # 基本控制
        basic_frame = ttk.LabelFrame(self.control_frame, text="基本控制")
        basic_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(basic_frame, text="开始模拟", command=self.start_simulation).pack(pady=2, fill=tk.X)
        ttk.Button(basic_frame, text="暂停/继续", command=self.toggle_simulation).pack(pady=2, fill=tk.X)
        ttk.Button(basic_frame, text="单步执行", command=self.step_simulation).pack(pady=2, fill=tk.X)
        ttk.Button(basic_frame, text="重置", command=self.reset_simulation).pack(pady=2, fill=tk.X)
        
        # 参数调节
        params_frame = ttk.LabelFrame(self.control_frame, text="参数调节")
        params_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 节点数量
        ttk.Label(params_frame, text="节点数量:").pack(anchor=tk.W)
        self.nodes_var = tk.IntVar(value=50)
        nodes_scale = ttk.Scale(params_frame, from_=10, to=100, variable=self.nodes_var, 
                               orient=tk.HORIZONTAL, command=self._update_node_count)
        nodes_scale.pack(fill=tk.X, pady=2)
        self.nodes_label = ttk.Label(params_frame, text="50")
        self.nodes_label.pack(anchor=tk.W)
        
        # 感染概率
        ttk.Label(params_frame, text="感染概率:").pack(anchor=tk.W, pady=(10, 0))
        self.infection_var = tk.DoubleVar(value=0.1)
        infection_scale = ttk.Scale(params_frame, from_=0.01, to=1.0, variable=self.infection_var,
                                   orient=tk.HORIZONTAL, command=self._update_infection_prob)
        infection_scale.pack(fill=tk.X, pady=2)
        self.infection_label = ttk.Label(params_frame, text="0.10")
        self.infection_label.pack(anchor=tk.W)
        
        # 恢复概率
        ttk.Label(params_frame, text="恢复概率:").pack(anchor=tk.W, pady=(10, 0))
        self.recovery_var = tk.DoubleVar(value=0.05)
        recovery_scale = ttk.Scale(params_frame, from_=0.01, to=0.5, variable=self.recovery_var,
                                  orient=tk.HORIZONTAL, command=self._update_recovery_prob)
        recovery_scale.pack(fill=tk.X, pady=2)
        self.recovery_label = ttk.Label(params_frame, text="0.05")
        self.recovery_label.pack(anchor=tk.W)
        
        # 传播扇出
        ttk.Label(params_frame, text="传播扇出:").pack(anchor=tk.W, pady=(10, 0))
        self.fanout_var = tk.IntVar(value=3)
        fanout_scale = ttk.Scale(params_frame, from_=1, to=10, variable=self.fanout_var,
                                orient=tk.HORIZONTAL, command=self._update_fanout)
        fanout_scale.pack(fill=tk.X, pady=2)
        self.fanout_label = ttk.Label(params_frame, text="3")
        self.fanout_label.pack(anchor=tk.W)
        
        # 传输成功率
        ttk.Label(params_frame, text="传输成功率:").pack(anchor=tk.W, pady=(10, 0))
        self.transmission_var = tk.DoubleVar(value=0.8)
        transmission_scale = ttk.Scale(params_frame, from_=0.1, to=1.0, variable=self.transmission_var,
                                      orient=tk.HORIZONTAL, command=self._update_transmission_prob)
        transmission_scale.pack(fill=tk.X, pady=2)
        self.transmission_label = ttk.Label(params_frame, text="0.80")
        self.transmission_label.pack(anchor=tk.W)
        
        # 动画速度
        ttk.Label(params_frame, text="动画速度:").pack(anchor=tk.W, pady=(10, 0))
        self.speed_var = tk.IntVar(value=100)
        speed_scale = ttk.Scale(params_frame, from_=10, to=1000, variable=self.speed_var,
                               orient=tk.HORIZONTAL, command=self._update_speed)
        speed_scale.pack(fill=tk.X, pady=2)
        self.speed_label = ttk.Label(params_frame, text="100ms")
        self.speed_label.pack(anchor=tk.W)
        
    def _setup_stats_display(self):
        """设置统计信息显示"""
        # 创建统计标签
        self.step_label = ttk.Label(self.stats_frame, text="步数: 0")
        self.step_label.grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
        
        self.susceptible_label = ttk.Label(self.stats_frame, text="易感染: 0", foreground="#4CAF50")
        self.susceptible_label.grid(row=0, column=1, padx=10, pady=5, sticky=tk.W)
        
        self.infected_label = ttk.Label(self.stats_frame, text="已感染: 0", foreground="#F44336")
        self.infected_label.grid(row=0, column=2, padx=10, pady=5, sticky=tk.W)
        
        self.removed_label = ttk.Label(self.stats_frame, text="已移除: 0", foreground="#9E9E9E")
        self.removed_label.grid(row=0, column=3, padx=10, pady=5, sticky=tk.W)
        
        self.messages_label = ttk.Label(self.stats_frame, text="消息总数: 0")
        self.messages_label.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky=tk.W)
        
    def _draw_initial_network(self):
        """绘制初始网络"""
        self.canvas.delete("all")
        
        # 绘制连接线
        for node_id, node in self.simulator.nodes.items():
            for neighbor_id in node.neighbors:
                if neighbor_id > node_id:  # 避免重复绘制
                    neighbor = self.simulator.nodes[neighbor_id]
                    self.canvas.create_line(
                        node.x, node.y, neighbor.x, neighbor.y,
                        fill="#E0E0E0", width=1, tags="edge"
                    )
        
        # 绘制节点
        for node_id, node in self.simulator.nodes.items():
            color = self.colors[node.state]
            self.canvas.create_oval(
                node.x - self.node_radius, node.y - self.node_radius,
                node.x + self.node_radius, node.y + self.node_radius,
                fill=color, outline="black", width=1,
                tags=f"node_{node_id}"
            )
            
            # 节点标签
            self.canvas.create_text(
                node.x, node.y, text=str(node_id),
                font=("Arial", 8), tags=f"label_{node_id}"
            )
            
    def _update_visualization(self):
        """更新可视化"""
        # 更新节点颜色
        for node_id, node in self.simulator.nodes.items():
            color = self.colors[node.state]
            self.canvas.itemconfig(f"node_{node_id}", fill=color)
            
        # 更新统计信息
        stats = self.simulator.get_statistics()
        self.step_label.config(text=f"步数: {stats['step']}")
        self.susceptible_label.config(text=f"易感染: {stats['susceptible']}")
        self.infected_label.config(text=f"已感染: {stats['infected']}")
        self.removed_label.config(text=f"已移除: {stats['removed']}")
        self.messages_label.config(text=f"消息总数: {stats['total_messages']}")
        
    def start_simulation(self):
        """开始模拟"""
        self.simulator.start_gossip([0])  # 从节点0开始
        self.is_running = True
        self._animate()
        
    def toggle_simulation(self):
        """暂停/继续模拟"""
        self.is_running = not self.is_running
        if self.is_running:
            self._animate()
            
    def step_simulation(self):
        """单步执行"""
        self.simulator.step()
        self._update_visualization()
        
    def reset_simulation(self):
        """重置模拟"""
        self.is_running = False
        self.simulator.reset_simulation()
        self._update_visualization()
        
    def _animate(self):
        """动画循环"""
        if self.is_running and self.simulator.running:
            self.simulator.step()
            self._update_visualization()
            self.root.after(self.animation_speed, self._animate)
        else:
            self.is_running = False
            
    # 参数更新回调函数
    def _update_node_count(self, value):
        """更新节点数量"""
        count = int(float(value))
        self.nodes_label.config(text=str(count))
        if not self.is_running:
            self.simulator = GossipSimulator(num_nodes=count, width=800, height=600)
            self._draw_initial_network()
            
    def _update_infection_prob(self, value):
        """更新感染概率"""
        prob = float(value)
        self.infection_label.config(text=f"{prob:.2f}")
        self.simulator.update_parameters(infection_probability=prob)
        
    def _update_recovery_prob(self, value):
        """更新恢复概率"""
        prob = float(value)
        self.recovery_label.config(text=f"{prob:.2f}")
        self.simulator.update_parameters(recovery_probability=prob)
        
    def _update_fanout(self, value):
        """更新传播扇出"""
        fanout = int(float(value))
        self.fanout_label.config(text=str(fanout))
        self.simulator.update_parameters(gossip_fanout=fanout)
        
    def _update_transmission_prob(self, value):
        """更新传输成功率"""
        prob = float(value)
        self.transmission_label.config(text=f"{prob:.2f}")
        self.simulator.update_parameters(transmission_probability=prob)
        
    def _update_speed(self, value):
        """更新动画速度"""
        speed = int(float(value))
        self.speed_label.config(text=f"{speed}ms")
        self.animation_speed = speed


def main():
    """主函数"""
    root = tk.Tk()
    app = GossipVisualization(root)
    
    # 设置窗口关闭事件
    def on_closing():
        app.is_running = False
        root.destroy()
        
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()