#!/usr/bin/env python3
"""
化学麻将游戏辅助脚本
用于处理出牌、吃碰等操作
"""

import sys
sys.path.insert(0, '/Users/yehonghao/.qclaw/workspace/chemical_mahjong')
from game import WinChecker, CardType, Card, CardDeck
import random
import pickle

def remove_one_card(hand, card_name):
    """从手牌中移除一张指定名称的牌"""
    new_hand = []
    removed = False
    for c in hand:
        if str(c) == card_name and not removed:
            removed = True
            continue
        new_hand.append(c)
    return new_hand

def get_card_by_name(hand, card_name):
    """获取手牌中第一张指定名称的牌"""
    for c in hand:
        if str(c) == card_name:
            return c
    return None

def print_hand(hand):
    """打印手牌"""
    by_type = {}
    for card in hand:
        if card.card_type not in by_type:
            by_type[card.card_type] = []
        by_type[card.card_type].append(card)
    
    type_names = {CardType.ELEMENT: "元素", CardType.ION: "离子", CardType.MOLECULE: "分子", CardType.CONDITION: "条件", CardType.STATE: "状态"}
    
    for ct in CardType:
        if ct in by_type:
            print(f"| **{type_names[ct]}** | {', '.join(str(c) for c in by_type[ct])} |")

def get_discard_suggestion(hand, valence, combo):
    """获取出牌建议"""
    reactants = ["H2", "O2", "KMnO4", "KClO3", "H2O2", "Na2O2", "Cl2"]
    condition_cards = [c for c in hand if c.card_type == CardType.CONDITION]
    state_cards = [c for c in hand if c.card_type == CardType.STATE]
    
    # 检查废牌
    has_reactant = any(str(c) in reactants for c in hand)
    waste_cards = []
    for card in condition_cards + state_cards:
        if not has_reactant:
            waste_cards.append(card)
    
    if waste_cards:
        return waste_cards[0], f"废牌，无法组成方程式"
    
    # 按化合价调整
    best_card = None
    best_val = 0
    for elem, val in combo.items():
        if valence > 0 and val > 0:
            if abs(val) > abs(best_val):
                best_val = val
                best_card = elem
        elif valence < 0 and val < 0:
            if abs(val) > abs(best_val):
                best_val = val
                best_card = elem
    
    if best_card:
        for c in hand:
            if str(c) == best_card:
                return c, f"{best_val:+d}"
    
    return None, "无建议"

if __name__ == "__main__":
    print("化学麻将辅助脚本加载成功")
