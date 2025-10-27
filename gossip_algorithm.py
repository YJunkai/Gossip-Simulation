"""
Gossip算法核心实现
实现了基于推送和拉取的Gossip协议
"""

import random
import time
import threading
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class NodeState(Enum):
    """节点状态枚举"""
    SUSCEPTIBLE = "susceptible"  # 易感染状态
    INFECTED = "infected"        # 已感染状态
    REMOVED = "removed"          # 移除状态


@dataclass
class Message:
    """消息数据结构"""
    id: str
    content: str
    timestamp: float
    source_node: int
    hop_count: int = 0


class GossipNode:
    """Gossip协议节点"""
    
    def __init__(self, node_id: int, x: float, y: float):
        self.node_id = node_id
        self.x = x
        self.y = y
        self.state = NodeState.SUSCEPTIBLE
        self.messages: Dict[str, Message] = {}
        self.neighbors: Set[int] = set()
        self.infection_probability = 0.1
        self.recovery_probability = 0.05
        self.is_active = True
        self.message_history: List[Message] = []
        
    def add_neighbor(self, neighbor_id: int):
        """添加邻居节点"""
        self.neighbors.add(neighbor_id)
        
    def remove_neighbor(self, neighbor_id: int):
        """移除邻居节点"""
        self.neighbors.discard(neighbor_id)
        
    def infect(self):
        """感染节点"""
        if self.state == NodeState.SUSCEPTIBLE:
            self.state = NodeState.INFECTED
            
    def recover(self):
        """节点恢复"""
        if self.state == NodeState.INFECTED and random.random() < self.recovery_probability:
            self.state = NodeState.REMOVED
            
    def receive_message(self, message: Message):
        """接收消息"""
        if message.id not in self.messages:
            self.messages[message.id] = message
            self.message_history.append(message)
            # 如果是易感染状态，有概率被感染
            if self.state == NodeState.SUSCEPTIBLE and random.random() < self.infection_probability:
                self.infect()


class GossipSimulator:
    """Gossip算法模拟器"""
    
    def __init__(self, num_nodes: int = 50, width: int = 800, height: int = 600):
        self.num_nodes = num_nodes
        self.width = width
        self.height = height
        self.nodes: Dict[int, GossipNode] = {}
        self.running = False
        self.step_count = 0
        self.message_counter = 0
        
        # 可调参数
        self.gossip_fanout = 3  # 每轮传播的邻居数量
        self.transmission_probability = 0.8  # 传输成功概率
        self.max_hop_count = 10  # 最大跳数
        self.simulation_speed = 1.0  # 模拟速度
        
        self._initialize_nodes()
        self._build_network_topology()
        
    def _initialize_nodes(self):
        """初始化节点"""
        for i in range(self.num_nodes):
            x = random.uniform(50, self.width - 50)
            y = random.uniform(50, self.height - 50)
            self.nodes[i] = GossipNode(i, x, y)
            
    def _build_network_topology(self):
        """构建网络拓扑"""
        # 创建随机几何图
        connection_radius = min(self.width, self.height) * 0.15
        
        for i in range(self.num_nodes):
            for j in range(i + 1, self.num_nodes):
                node1 = self.nodes[i]
                node2 = self.nodes[j]
                
                # 计算欧几里得距离
                distance = ((node1.x - node2.x) ** 2 + (node1.y - node2.y) ** 2) ** 0.5
                
                if distance <= connection_radius:
                    node1.add_neighbor(j)
                    node2.add_neighbor(i)
                    
        # 确保网络连通性
        self._ensure_connectivity()
        
    def _ensure_connectivity(self):
        """确保网络连通性"""
        # 简单的连通性检查和修复
        visited = set()
        
        def dfs(node_id):
            if node_id in visited:
                return
            visited.add(node_id)
            for neighbor in self.nodes[node_id].neighbors:
                dfs(neighbor)
                
        if self.nodes:
            dfs(0)
            
        # 如果有未访问的节点，随机连接到已访问的节点
        unvisited = set(range(self.num_nodes)) - visited
        for node_id in unvisited:
            if visited:
                target = random.choice(list(visited))
                self.nodes[node_id].add_neighbor(target)
                self.nodes[target].add_neighbor(node_id)
                visited.add(node_id)
                
    def start_gossip(self, initial_infected: List[int] = None):
        """开始Gossip传播"""
        if initial_infected is None:
            initial_infected = [0]  # 默认从节点0开始
            
        # 重置所有节点状态
        for node in self.nodes.values():
            node.state = NodeState.SUSCEPTIBLE
            node.messages.clear()
            node.message_history.clear()
            
        # 感染初始节点
        for node_id in initial_infected:
            if node_id in self.nodes:
                self.nodes[node_id].infect()
                
        self.step_count = 0
        self.running = True
        
    def step(self):
        """执行一步模拟"""
        if not self.running:
            return
            
        self.step_count += 1
        
        # 获取所有感染节点
        infected_nodes = [node for node in self.nodes.values() 
                         if node.state == NodeState.INFECTED]
        
        if not infected_nodes:
            self.running = False
            return
            
        # 每个感染节点尝试传播
        for node in infected_nodes:
            self._gossip_step(node)
            
        # 节点恢复检查
        for node in self.nodes.values():
            node.recover()
            
    def _gossip_step(self, node: GossipNode):
        """单个节点的Gossip步骤"""
        if not node.neighbors:
            return
            
        # 选择要传播的邻居
        available_neighbors = list(node.neighbors)
        num_targets = min(self.gossip_fanout, len(available_neighbors))
        targets = random.sample(available_neighbors, num_targets)
        
        # 创建消息
        message = Message(
            id=f"msg_{self.message_counter}_{node.node_id}",
            content=f"Gossip from node {node.node_id}",
            timestamp=time.time(),
            source_node=node.node_id,
            hop_count=0
        )
        self.message_counter += 1
        
        # 向选中的邻居传播
        for target_id in targets:
            if (target_id in self.nodes and 
                random.random() < self.transmission_probability and
                message.hop_count < self.max_hop_count):
                
                target_node = self.nodes[target_id]
                message.hop_count += 1
                target_node.receive_message(message)
                
    def get_statistics(self) -> Dict:
        """获取模拟统计信息"""
        susceptible = sum(1 for node in self.nodes.values() 
                         if node.state == NodeState.SUSCEPTIBLE)
        infected = sum(1 for node in self.nodes.values() 
                      if node.state == NodeState.INFECTED)
        removed = sum(1 for node in self.nodes.values() 
                     if node.state == NodeState.REMOVED)
        
        total_messages = sum(len(node.messages) for node in self.nodes.values())
        
        return {
            'step': self.step_count,
            'susceptible': susceptible,
            'infected': infected,
            'removed': removed,
            'total_messages': total_messages,
            'running': self.running
        }
        
    def update_parameters(self, **kwargs):
        """更新模拟参数"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
                
        # 更新节点参数
        if 'infection_probability' in kwargs:
            for node in self.nodes.values():
                node.infection_probability = kwargs['infection_probability']
                
        if 'recovery_probability' in kwargs:
            for node in self.nodes.values():
                node.recovery_probability = kwargs['recovery_probability']
                
    def reset_simulation(self):
        """重置模拟"""
        self.running = False
        self.step_count = 0
        self.message_counter = 0
        
        for node in self.nodes.values():
            node.state = NodeState.SUSCEPTIBLE
            node.messages.clear()
            node.message_history.clear()