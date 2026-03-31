"""
化学麻将 - 文字版游戏引擎
Chemical Mahjong - Text-based Game Engine
"""

from enum import Enum
from typing import List, Dict, Tuple, Set
from dataclasses import dataclass
import random

# ============ 牌的定义 ============

class CardType(Enum):
    """牌的类型"""
    ELEMENT = "元素"      # 元素牌
    ION = "离子"          # 离子牌
    MOLECULE = "分子"     # 分子牌
    CONDITION = "条件"    # 反应条件牌
    STATE = "状态"        # 产物状态牌


@dataclass
class Card:
    """牌的定义"""
    name: str              # 牌名（如 "Na", "Cl⁻¹", "H₂O"）
    card_type: CardType    # 牌的类型
    valence: int = 0       # 化合价（0表示无化合价）
    
    def __repr__(self):
        return f"{self.name}"
    
    def __eq__(self, other):
        return self.name == other.name and self.card_type == other.card_type
    
    def __hash__(self):
        return hash((self.name, self.card_type))


# ============ 牌库初始化 ============

class CardDeck:
    """牌库管理"""
    
    def __init__(self):
        self.cards: List[Card] = []
        self._init_cards()
    
    def _init_cards(self):
        """初始化144张牌"""
        
        # 元素牌（68张）：17种元素 × 4张
        # 注意：多化合价元素使用最常见化合价，但在计算时会枚举所有可能
        elements = [
            ("Na", 1), ("Mg", 2), ("Al", 3), ("K", 1), ("Ca", 2),
            ("Fe", 2), ("Cu", 2), ("Zn", 2), ("Ba", 2), ("Ag", 1),
            ("H", 1), ("P", 5), ("S", -2), ("Cl", -1), ("C", 4),
            ("N", -3), ("O", -2)
        ]
        for elem, valence in elements:
            for _ in range(4):
                self.cards.append(Card(elem, CardType.ELEMENT, valence))
        
        # 离子牌（24张）：6种离子 × 4张
        ions = [
            ("NO3⁻¹", -1),
            ("OH⁻¹", -1),
            ("NH4⁺¹", 1),
            ("PO4⁻³", -3),
            ("CO3⁻²", -2),
            ("SO4⁻²", -2)
        ]
        for ion, valence in ions:
            for _ in range(4):
                self.cards.append(Card(ion, CardType.ION, valence))
        
        # 分子牌（32张）：8种分子 × 4张
        molecules = [
            "KMnO4", "K2MnO4", "MnO2", "CO2",
            "H2O", "H2", "O2", "Cl2"
        ]
        for mol in molecules:
            for _ in range(4):
                self.cards.append(Card(mol, CardType.MOLECULE, 0))
        
        # 反应条件牌（16张）：4种条件 × 4张
        conditions = ["点燃", "加热", "高温", "电解"]
        for cond in conditions:
            for _ in range(4):
                self.cards.append(Card(cond, CardType.CONDITION, 0))
        
        # 产物状态牌（4张）：2种状态 × 2张
        states = ["气体", "沉淀"]
        for state in states:
            for _ in range(2):
                self.cards.append(Card(state, CardType.STATE, 0))
    
    def shuffle(self):
        """洗牌"""
        random.shuffle(self.cards)
    
    def draw(self, count: int) -> List[Card]:
        """抽取指定数量的牌"""
        drawn = self.cards[:count]
        self.cards = self.cards[count:]
        return drawn


# ============ 和牌判断 ============

class WinChecker:
    """和牌检查器"""
    
    # 元素周期表顺序（用于顺子检查）
    ELEMENT_ORDER = [
        "H", "C", "N", "O", "P", "S", "Cl",  # 非金属
        "Na", "Mg", "Al", "K", "Ca", "Fe", "Cu", "Zn", "Ba", "Ag"  # 金属
    ]
    
    # 元素的所有可能化合价
    ELEMENT_VALENCES = {
        "Na": [1],
        "Mg": [2],
        "Al": [3],
        "K": [1],
        "Ca": [2],
        "Fe": [2, 3],
        "Cu": [1, 2],
        "Zn": [2],
        "Ba": [2],
        "Ag": [1],
        "H": [1, -1],
        "P": [-3, 3, 5],
        "S": [-2, 2, 4, 6],
        "Cl": [-1, 1, 3, 5, 7],
        "C": [-4, 2, 4],
        "N": [-3, 1, 2, 3, 4, 5],
        "O": [-2],
    }
    
    # 可组成的现实中存在的物质
    VALID_COMPOUNDS = {
        "Na": ["Na2S", "NaCl", "Na2O", "NaNO3", "NaOH", "Na2HPO4", "NaH2PO4", 
               "Na3PO4", "Na2CO3", "NaHCO3", "Na2SO4", "NaHSO4"],
        "Mg": ["MgS", "MgCl2", "MgO", "Mg(NO3)2", "Mg(OH)2", "MgHPO4", "Mg(H2PO4)2",
               "Mg3(PO4)2", "MgCO3", "Mg(HCO3)2", "MgSO4", "Mg(HSO4)2"],
        "Al": ["Al2S3", "AlCl3", "Al2O3", "Al(NO3)3", "Al(OH)3", "Al2(HPO4)3",
               "Al(H2PO4)3", "AlPO4", "Al2(SO4)3", "Al(HSO4)3"],
        "K": ["K2S", "KCl", "K2O", "KNO3", "KOH", "K2HPO4", "KH2PO4",
              "K3PO4", "K2CO3", "KHCO3", "K2SO4", "KHSO4"],
        "Ca": ["CaS", "CaCl2", "CaO", "Ca(NO3)2", "Ca(OH)2", "CaHPO4", "Ca(H2PO4)2",
               "Ca3(PO4)2", "CaCO3", "Ca(HCO3)2", "CaSO4", "Ca(HSO4)2"],
        "Fe": ["FeS", "FeCl2", "FeCl3", "FeO", "Fe2O3", "Fe3O4", "Fe(NO3)2", "Fe(NO3)3",
               "Fe(OH)2", "Fe(OH)3", "Fe3(PO4)2", "FePO4", "FeHPO4", "Fe(H2PO4)3",
               "Fe(H2PO4)2", "FeCO3", "Fe2(CO3)3", "Fe(HCO3)2", "FeSO4", "Fe2(SO4)3",
               "Fe(HSO4)2", "Fe(HSO4)3"],
        "Cu": ["CuS", "CuCl2", "CuO", "Cu(NO3)2", "Cu(OH)2", "CuCO3", "CuSO4",
               "Cu(HSO4)2", "Cu3(PO4)2", "CuHPO4"],
        "Zn": ["ZnS", "ZnCl2", "ZnO", "Zn(NO3)2", "Zn(OH)2", "ZnCO3", "ZnSO4",
               "Zn3(PO4)2"],
        "Ag": ["Ag2S", "AgCl", "Ag2O", "AgNO3", "Ag3PO4", "Ag2CO3", "Ag2SO4"],
        "H": ["H2S", "HCl", "NH3", "CH4", "HNO3", "H3PO4", "H2CO3", "H2SO4", "PH3"],
        "S": ["SO2"],
        "N": ["NO", "NO2", "N2O4", "N2O5"],
        "P": [],
        "C": [],
        "O": [],
        "Ba": [],
    }
    
    @staticmethod
    def check_pair(card1: Card, card2: Card) -> Tuple[bool, str]:
        """检查两张牌是否能成对子
        
        规则：
        1. 化合价数值相等、符号相反
        2. 组成的物质必须现实中存在
        3. 分子牌、条件牌、状态牌不能成对子（无化合价）
        """
        # 检查1：必须有化合价
        if card1.valence == 0 or card2.valence == 0:
            return False, "分子牌、条件牌、状态牌不能成对子"
        
        # 检查2：化合价数值相等
        if abs(card1.valence) != abs(card2.valence):
            return False, f"化合价数值不等：{abs(card1.valence)} ≠ {abs(card2.valence)}"
        
        # 检查3：化合价符号相反
        if card1.valence * card2.valence >= 0:  # 同号
            return False, f"化合价符号相同：{card1.valence} 和 {card2.valence}"
        
        # 检查4：组成的物质是否存在
        # 简化版：检查是否能组成有效化合物
        compound = WinChecker._form_compound(card1, card2)
        if compound and WinChecker._is_valid_compound(compound):
            return True, f"可成对子：{card1} + {card2} = {compound}"
        
        return False, f"组成的物质不存在：{card1} + {card2}"
    
    @staticmethod
    def _form_compound(card1: Card, card2: Card) -> str:
        """根据两张牌的化合价组成化合物"""
        # 获取元素名（去掉化合价标记）
        elem1 = card1.name.replace("⁺", "").replace("⁻", "").replace("¹", "").replace("²", "").replace("³", "")
        elem2 = card2.name.replace("⁺", "").replace("⁻", "").replace("¹", "").replace("²", "").replace("³", "")
        
        val1 = abs(card1.valence)
        val2 = abs(card2.valence)
        
        # 按化合价比例组成化合物
        if val1 == val2:
            return f"{elem1}{elem2}"
        else:
            # 最小公倍数
            from math import gcd
            lcm = (val1 * val2) // gcd(val1, val2)
            count1 = lcm // val1
            count2 = lcm // val2
            return f"{elem1}{count1}{elem2}{count2}" if count1 > 1 or count2 > 1 else f"{elem1}{elem2}"
    
    @staticmethod
    def _is_valid_compound(compound: str) -> bool:
        """检查化合物是否现实中存在（简化版）"""
        # 这里可以扩展为完整的化合物数据库
        # 暂时返回 True（假设所有化合价正确的组合都存在）
        return True
    
    @staticmethod
    def check_sequence(card1: Card, card2: Card, card3: Card) -> Tuple[bool, str]:
        """检查三张牌是否能成顺子
        
        规则：
        1. 必须都是元素牌
        2. 在元素周期表上排序连续
        3. 顺序：H, C, N, O, P, S, Cl, Na, Mg, Al, K, Ca, Fe, Cu, Zn, Ba, Ag
        """
        # 检查1：必须都是元素牌
        if card1.card_type != CardType.ELEMENT or card2.card_type != CardType.ELEMENT or card3.card_type != CardType.ELEMENT:
            return False, "顺子必须都是元素牌"
        
        # 获取三张牌在周期表中的位置
        try:
            pos1 = WinChecker.ELEMENT_ORDER.index(card1.name)
            pos2 = WinChecker.ELEMENT_ORDER.index(card2.name)
            pos3 = WinChecker.ELEMENT_ORDER.index(card3.name)
        except ValueError:
            return False, "包含未知元素"
        
        # 排序
        positions = sorted([pos1, pos2, pos3])
        
        # 检查2：是否连续
        if positions[1] == positions[0] + 1 and positions[2] == positions[1] + 1:
            elements = [WinChecker.ELEMENT_ORDER[p] for p in positions]
            return True, f"可成顺子：{elements[0]} - {elements[1]} - {elements[2]}"
        else:
            return False, f"元素不连续：位置 {positions}"
    
    @staticmethod
    def check_triplet(card1: Card, card2: Card, card3: Card) -> Tuple[bool, str]:
        """检查三张牌是否能成刻子
        
        规则：
        1. 三张牌必须完全相同（名称和类型都相同）
        """
        # 检查三张牌是否相同
        if card1 == card2 == card3:
            return True, f"可成刻子：{card1} × 3"
        else:
            # 详细说明为什么不能成刻子
            if card1.name != card2.name or card2.name != card3.name:
                return False, f"牌名不同：{card1.name}, {card2.name}, {card3.name}"
            elif card1.card_type != card2.card_type or card2.card_type != card3.card_type:
                return False, f"牌型不同：{card1.card_type.value}, {card2.card_type.value}, {card3.card_type.value}"
            else:
                return False, "三张牌不相同"
    
    @staticmethod
    def check_win(hand: List[Card]) -> Tuple[bool, str]:
        """检查是否和牌
        
        和牌条件：
        1. 化合价总和为0
        2. 如果有条件牌/状态牌，必须能组成化学方程式
        3. 如果没有条件牌/状态牌，只需化合价为0
        """
        if len(hand) != 14:
            return False, "手牌必须14张"
        
        # 计算最优化合价总和
        total_valence, best_combo = WinChecker.calculate_optimal_valence(hand)
        
        if total_valence != 0:
            return False, f"化合价总和为{total_valence}，未和牌"
        
        # 检查是否有条件牌/状态牌
        condition_cards = [c for c in hand if c.card_type == CardType.CONDITION]
        state_cards = [c for c in hand if c.card_type == CardType.STATE]
        
        # 如果有条件牌/状态牌，必须全部用于组成化学方程式才能和牌
        if condition_cards or state_cards:
            # 检查是否能与手牌中的其他牌组成化学方程式
            # 条件牌/状态牌必须全部有用，否则是废牌
            reactants = ["H2", "O2", "KMnO4", "KClO3", "H2O2", "Na2O2", "Cl2"]
            conditions = ["点燃", "加热", "高温", "电解"]
            states = ["气体", "沉淀"]
            
            # 检查每张条件牌/状态牌是否都有对应的反应物
            for card in condition_cards + state_cards:
                card_name = str(card)
                # 简化判断：检查是否有对应的反应物
                has_match = False
                for c in hand:
                    if str(c) in reactants:
                        has_match = True
                        break
                if not has_match:
                    return False, f"有废牌{card_name}，无法组成化学方程式，不能和牌"
        
        return True, "和牌！化合价总和为0"
    
    @staticmethod
    def can_win(hand: List[Card]) -> Tuple[bool, str]:
        """检查是否能和牌（不考虑吃碰区）"""
        if len(hand) != 14:
            return False, "手牌必须14张"
        
        total_valence, best_combo = WinChecker.calculate_optimal_valence(hand)
        
        if total_valence != 0:
            return False, f"化合价{total_valence}，需调整为0"
        
        # 检查条件牌/状态牌是否都是有用牌
        condition_cards = [c for c in hand if c.card_type == CardType.CONDITION]
        state_cards = [c for c in hand if c.card_type == CardType.STATE]
        
        if condition_cards or state_cards:
            reactants = ["H2", "O2", "KMnO4", "KClO3", "H2O2", "Na2O2", "Cl2"]
            conditions = ["点燃", "加热", "高温", "电解"]
            states = ["气体", "沉淀"]
            
            for card in condition_cards + state_cards:
                has_match = any(str(c) in reactants for c in hand)
                if not has_match:
                    return False, f"有废牌{card}，无法组成方程式"
        
        return True, "可以听牌"
    
    @staticmethod
    def calculate_optimal_valence(hand: List[Card]) -> Tuple[int, Dict[str, int]]:
        """计算最优的化合价总和（枚举多化合价元素的所有可能）
        
        返回：(最接近0的化合价总和, 最优化的化合价组合)
        """
        from itertools import product
        
        # 分离元素牌和其他牌
        element_cards = [c for c in hand if c.card_type == CardType.ELEMENT]
        other_cards = [c for c in hand if c.card_type != CardType.ELEMENT]
        
        # 其他牌的化合价是固定的
        other_valence = sum(c.valence for c in other_cards)
        
        if not element_cards:
            return other_valence, {}
        
        # 枚举所有可能的化合价组合
        valence_options = []
        for card in element_cards:
            if card.name in WinChecker.ELEMENT_VALENCES:
                valence_options.append(WinChecker.ELEMENT_VALENCES[card.name])
            else:
                valence_options.append([card.valence])  # 使用默认值
        
        best_valence = float('inf')
        best_combo = {}
        
        # 枚举所有组合
        for combo in product(*valence_options):
            total = sum(combo) + other_valence
            if abs(total) < abs(best_valence):
                best_valence = total
                best_combo = {element_cards[i].name: combo[i] for i in range(len(element_cards))}
        
        return int(best_valence), best_combo


# ============ 游戏主类 ============

class ChemicalMahjongGame:
    """化学麻将游戏"""
    
    def __init__(self, num_players: int = 4):
        self.num_players = num_players
        self.deck = CardDeck()
        self.players: List[List[Card]] = [[] for _ in range(num_players)]
        self.discard_pile: List[Card] = []
        self.current_player = 0
        self.win_checker = WinChecker()
    
    def start_game(self):
        """开始游戏"""
        print("=" * 50)
        print("化学麻将 - 文字版游戏")
        print("=" * 50)
        
        # 洗牌
        self.deck.shuffle()
        
        # 发牌：每人14张（庄家）或13张（闲家）
        for i in range(self.num_players):
            cards = self.deck.draw(14 if i == 0 else 13)
            self.players[i] = sorted(cards, key=lambda c: (c.card_type.value, c.name))
        
        print(f"\n游戏开始！共{self.num_players}人")
        print(f"庄家：玩家1（14张牌）")
        print(f"闲家：玩家2-4（各13张牌）\n")
        
        self.show_player_hand(0)
    
    def show_player_hand(self, player_id: int):
        """显示玩家手牌"""
        hand = self.players[player_id]
        print(f"\n玩家{player_id + 1}的手牌（共{len(hand)}张）：")
        
        # 按类型分组显示
        by_type = {}
        for card in hand:
            if card.card_type not in by_type:
                by_type[card.card_type] = []
            by_type[card.card_type].append(card)
        
        for card_type in CardType:
            if card_type in by_type:
                cards_str = " ".join(str(c) for c in by_type[card_type])
                print(f"  {card_type.value}：{cards_str}")
        
        # 显示化合价总和
        total_valence = sum(card.valence for card in hand)
        print(f"  化合价总和：{total_valence}")
    
    def check_win_condition(self, player_id: int) -> Tuple[bool, str]:
        """检查玩家是否和牌"""
        hand = self.players[player_id]
        return self.win_checker.check_win(hand)
    
    def get_ai_suggestion(self, player_id: int) -> Dict:
        """获取 AI 出牌建议
        
        返回：
        {
            'current_valence': int,           # 当前化合价总和
            'target_valence': int,            # 目标化合价（0）
            'need_to_discard': int,           # 需要打出的化合价
            'suggestions': [                  # 出牌建议列表
                {
                    'card': Card,
                    'reason': str,
                    'priority': int            # 优先级（1-10，10最高）
                }
            ],
            'is_listening': bool,             # 是否已听牌
            'win_probability': float          # 和牌概率（0-1）
        }
        """
        hand = self.players[player_id]
        current_valence = sum(card.valence for card in hand)
        target_valence = 0
        need_to_discard = current_valence - target_valence
        
        suggestions = []
        
        # 分析每张牌的出牌价值
        for card in hand:
            reason = ""
            priority = 5  # 默认优先级
            
            # 规则1：打出无化合价的牌（分子、条件、状态）
            if card.valence == 0:
                reason = "无化合价，不影响和牌"
                priority = 3
            
            # 规则2：打出能减少化合价差距的牌
            elif card.valence > 0 and need_to_discard > 0:
                # 需要减少正化合价
                reason = f"打出正化合价{card.valence}，减少差距"
                priority = min(10, 5 + abs(card.valence))
            
            elif card.valence < 0 and need_to_discard < 0:
                # 需要减少负化合价
                reason = f"打出负化合价{card.valence}，减少差距"
                priority = min(10, 5 + abs(card.valence))
            
            # 规则3：打出不能成对子/顺子/刻子的牌
            else:
                # 检查这张牌是否能和其他牌组合
                can_pair = False
                can_sequence = False
                can_triplet = False
                
                for other_card in hand:
                    if other_card == card:
                        continue
                    
                    # 检查对子
                    if not can_pair:
                        is_pair, _ = self.win_checker.check_pair(card, other_card)
                        if is_pair:
                            can_pair = True
                    
                    # 检查顺子
                    if not can_sequence:
                        for third_card in hand:
                            if third_card == card or third_card == other_card:
                                continue
                            is_seq, _ = self.win_checker.check_sequence(card, other_card, third_card)
                            if is_seq:
                                can_sequence = True
                                break
                    
                    # 检查刻子
                    if not can_triplet:
                        for third_card in hand:
                            if third_card == card or third_card == other_card:
                                continue
                            is_triplet, _ = self.win_checker.check_triplet(card, other_card, third_card)
                            if is_triplet:
                                can_triplet = True
                                break
                
                if not can_pair and not can_sequence and not can_triplet:
                    reason = "无法组合，建议打出"
                    priority = 8
                else:
                    reason = "可以组合，保留"
                    priority = 2
            
            suggestions.append({
                'card': card,
                'reason': reason,
                'priority': priority
            })
        
        # 按优先级排序
        suggestions.sort(key=lambda x: x['priority'], reverse=True)
        
        # 检查是否已听牌
        is_listening = need_to_discard == 0
        
        # 计算和牌概率（简化版：基于剩余牌数）
        remaining_cards = len(self.deck.cards)
        matching_cards = 0
        
        # 统计能帮助和牌的牌
        for card in self.deck.cards:
            if card.valence == -need_to_discard:
                matching_cards += 1
        
        win_probability = matching_cards / max(remaining_cards, 1) if remaining_cards > 0 else 0
        
        return {
            'current_valence': current_valence,
            'target_valence': target_valence,
            'need_to_discard': need_to_discard,
            'suggestions': suggestions,
            'is_listening': is_listening,
            'win_probability': win_probability
        }
    
    def show_ai_suggestion(self, player_id: int):
        """显示 AI 出牌建议"""
        suggestion = self.get_ai_suggestion(player_id)
        
        print(f"\n【玩家{player_id + 1}的 AI 建议】")
        print(f"当前化合价：{suggestion['current_valence']}")
        print(f"目标化合价：{suggestion['target_valence']}")
        print(f"需要调整：{suggestion['need_to_discard']}")
        
        if suggestion['is_listening']:
            print("✅ 已听牌！")
        else:
            print(f"❌ 未听牌，还需调整{abs(suggestion['need_to_discard'])}")
        
        print(f"和牌概率：{suggestion['win_probability']:.1%}")
        
        print("\n出牌建议（按优先级排序）：")
        for i, sug in enumerate(suggestion['suggestions'][:5], 1):  # 只显示前5个
            card = sug['card']
            reason = sug['reason']
            priority = sug['priority']
            print(f"  {i}. {card} (优先级{priority}/10) - {reason}")
    
    def get_eat_peng_suggestions(self, player_id: int, discard_card: Card, discard_player_id: int = None) -> Dict:
        """获取吃碰牌建议
        
        参数：
            player_id: 当前玩家ID
            discard_card: 对方打出的牌
            discard_player_id: 打出牌的玩家ID（用于判断是否是上家）
        
        返回：
        {
            'can_peng': bool,              # 是否可以碰
            'peng_info': {                 # 碰的信息
                'card': Card,
                'new_valence': int,        # 碰后的化合价
                'benefit': str             # 碰的好处
            },
            'can_eat': bool,               # 是否可以吃
            'eat_suggestions': [           # 吃的建议列表
                {
                    'cards': [Card, Card, Card],  # 吃的三张牌
                    'new_valence': int,
                    'benefit': str
                }
            ],
            'recommendation': str          # 总体建议
        }
        """
        hand = self.players[player_id]
        result = {
            'can_peng': False,
            'peng_info': None,
            'can_eat': False,
            'eat_suggestions': [],
            'recommendation': ""
        }
        
        # 判断是否是上家
        # 逆时针顺序：玩家0 <- 玩家1 <- 玩家2 <- 玩家3 <- 玩家0
        # 所以上家是 (player_id - 1) % num_players
        if discard_player_id is None:
            discard_player_id = (player_id - 1) % self.num_players
        
        is_upstream = (discard_player_id == (player_id - 1) % self.num_players)
        
        # 检查是否可以碰（任意家都可以碰）
        peng_count = sum(1 for card in hand if card == discard_card)
        if peng_count >= 2:
            # 可以碰
            new_valence = sum(card.valence for card in hand) + discard_card.valence
            result['can_peng'] = True
            result['peng_info'] = {
                'card': discard_card,
                'new_valence': new_valence,
                'benefit': f"碰{discard_card}，化合价变为{new_valence}"
            }
        
        # 检查是否可以吃（只能吃上家的牌）
        if is_upstream and discard_card.card_type == CardType.ELEMENT:
            # 获取对方牌在周期表中的位置
            try:
                discard_pos = WinChecker.ELEMENT_ORDER.index(discard_card.name)
            except ValueError:
                discard_pos = -1
            
            if discard_pos >= 0:
                # 检查所有可能的吃法
                for i, card1 in enumerate(hand):
                    if card1.card_type != CardType.ELEMENT:
                        continue
                    
                    for j, card2 in enumerate(hand):
                        if j <= i or card2.card_type != CardType.ELEMENT:
                            continue
                        
                        # 尝试组成顺子
                        is_seq, _ = self.win_checker.check_sequence(card1, card2, discard_card)
                        if is_seq:
                            # 可以吃
                            new_hand = hand.copy()
                            new_hand.remove(card1)
                            new_hand.remove(card2)
                            new_valence = sum(card.valence for card in new_hand) + discard_card.valence
                            
                            result['can_eat'] = True
                            result['eat_suggestions'].append({
                                'cards': sorted([card1, card2, discard_card], 
                                              key=lambda c: WinChecker.ELEMENT_ORDER.index(c.name)),
                                'new_valence': new_valence,
                                'benefit': f"吃{card1}-{card2}-{discard_card}，化合价变为{new_valence}"
                            })
        
        # 生成总体建议
        if result['can_peng'] and result['can_eat']:
            result['recommendation'] = "可以碰或吃，建议根据化合价选择"
        elif result['can_peng']:
            result['recommendation'] = "可以碰"
        elif result['can_eat']:
            result['recommendation'] = "可以吃"
        else:
            if not is_upstream and discard_card.card_type == CardType.ELEMENT:
                result['recommendation'] = "不是上家的牌，只能碰（但手牌不足）"
            else:
                result['recommendation'] = "无法吃碰"
        
        return result
    
    def show_eat_peng_suggestions(self, player_id: int, discard_card: Card, discard_player_id: int = None):
        """显示吃碰牌建议"""
        suggestion = self.get_eat_peng_suggestions(player_id, discard_card, discard_player_id)
        
        # 判断是否是上家
        if discard_player_id is None:
            discard_player_id = (player_id - 1) % self.num_players
        
        is_upstream = (discard_player_id == (player_id - 1) % self.num_players)
        
        print(f"\n【玩家{player_id + 1}的吃碰建议】")
        print(f"玩家{discard_player_id + 1}打出：{discard_card}" + (" (上家)" if is_upstream else " (非上家)"))
        print(f"建议：{suggestion['recommendation']}")
        
        if suggestion['can_peng']:
            peng = suggestion['peng_info']
            print(f"\n✅ 可以碰（任意家都可碰）：")
            print(f"   {peng['card']} × 3")
            print(f"   {peng['benefit']}")
        
        if suggestion['can_eat']:
            print(f"\n✅ 可以吃（只能吃上家）：")
            for i, eat in enumerate(suggestion['eat_suggestions'], 1):
                cards_str = " - ".join(str(c) for c in eat['cards'])
                print(f"   {i}. {cards_str}")
                print(f"      {eat['benefit']}")
        
        if not suggestion['can_peng'] and not suggestion['can_eat']:
            if not is_upstream and discard_card.card_type == CardType.ELEMENT:
                print(f"\n❌ 不是上家的牌，无法吃（只能碰，但手牌不足）")
    
    def play_turn(self, player_id: int, card_index: int):
        """玩家出牌"""
        if card_index < 0 or card_index >= len(self.players[player_id]):
            print("出牌索引错误！")
            return False
        
        card = self.players[player_id].pop(card_index)
        self.discard_pile.append(card)
        print(f"玩家{player_id + 1}出牌：{card}")
        
        # 检查是否和牌
        is_win, msg = self.check_win_condition(player_id)
        if is_win:
            print(f"玩家{player_id + 1} {msg}")
            return True
        
        return False


# ============ 测试 ============

if __name__ == "__main__":
    game = ChemicalMahjongGame(num_players=4)
    game.start_game()
    
    # 显示玩家1的 AI 建议
    game.show_ai_suggestion(0)
    
    # 测试吃碰建议
    print("\n" + "=" * 50)
    print("测试吃碰建议")
    print("=" * 50)
    
    # 创建一个特定的手牌用于测试吃碰
    test_hand = [
        Card("H", CardType.ELEMENT, 1),
        Card("C", CardType.ELEMENT, 4),
        Card("N", CardType.ELEMENT, 3),
        Card("O", CardType.ELEMENT, 2),
        Card("Na", CardType.ELEMENT, 1),
        Card("Na", CardType.ELEMENT, 1),
        Card("Cl⁻¹", CardType.ION, -1),
        Card("Cl⁻¹", CardType.ION, -1),
        Card("H2O", CardType.MOLECULE, 0),
        Card("H2O", CardType.MOLECULE, 0),
        Card("H2O", CardType.MOLECULE, 0),
        Card("H2O", CardType.MOLECULE, 0),
        Card("Ca", CardType.ELEMENT, 2),
        Card("SO4⁻²", CardType.ION, -2),
    ]
    game.players[0] = test_hand
    
    print("\n玩家1的手牌：")
    game.show_player_hand(0)
    
    # 测试碰（任意家都可碰）
    print("\n【测试碰 - 玩家2打出Na】")
    discard_card = Card("Na", CardType.ELEMENT, 1)
    game.show_eat_peng_suggestions(0, discard_card, discard_player_id=1)  # 玩家2打出
    
    # 测试吃（只能吃上家）
    print("\n【测试吃 - 玩家4(上家)打出P】")
    discard_card = Card("P", CardType.ELEMENT, 3)
    game.show_eat_peng_suggestions(0, discard_card, discard_player_id=3)  # 玩家4是玩家1的上家
    
    # 测试吃失败（不是上家）
    print("\n【测试吃失败 - 玩家2(非上家)打出P】")
    discard_card = Card("P", CardType.ELEMENT, 3)
    game.show_eat_peng_suggestions(0, discard_card, discard_player_id=1)  # 玩家2不是上家
    
    # 测试无法吃碰
    print("\n【测试无法吃碰 - 玩家4打出Ba】")
    discard_card = Card("Ba", CardType.ELEMENT, 2)
    game.show_eat_peng_suggestions(0, discard_card, discard_player_id=3)
    
    # 测试对子检查
    print("\n" + "=" * 50)
    print("测试对子检查")
    print("=" * 50)
    
    test_pairs = [
        (Card("Na", CardType.ELEMENT, 1), Card("Cl⁻¹", CardType.ION, -1)),
        (Card("H", CardType.ELEMENT, 1), Card("OH⁻¹", CardType.ION, -1)),
        (Card("Ca", CardType.ELEMENT, 2), Card("SO4⁻²", CardType.ION, -2)),
        (Card("Fe", CardType.ELEMENT, 2), Card("PO4⁻³", CardType.ION, -3)),  # 化合价不等
        (Card("Na", CardType.ELEMENT, 1), Card("K", CardType.ELEMENT, 1)),    # 同号
        (Card("H2O", CardType.MOLECULE, 0), Card("H2O", CardType.MOLECULE, 0)),  # 无化合价
    ]
    
    for card1, card2 in test_pairs:
        is_pair, msg = game.win_checker.check_pair(card1, card2)
        status = "✅" if is_pair else "❌"
        print(f"{status} {card1} + {card2}：{msg}")
    
    # 测试顺子检查
    print("\n" + "=" * 50)
    print("测试顺子检查")
    print("=" * 50)
    
    test_sequences = [
        (Card("H", CardType.ELEMENT, 1), Card("C", CardType.ELEMENT, 4), Card("N", CardType.ELEMENT, 3)),
        (Card("C", CardType.ELEMENT, 4), Card("N", CardType.ELEMENT, 3), Card("O", CardType.ELEMENT, 2)),
        (Card("Na", CardType.ELEMENT, 1), Card("Mg", CardType.ELEMENT, 2), Card("Al", CardType.ELEMENT, 3)),
        (Card("H", CardType.ELEMENT, 1), Card("N", CardType.ELEMENT, 3), Card("O", CardType.ELEMENT, 2)),  # 不连续
        (Card("H", CardType.ELEMENT, 1), Card("C", CardType.ELEMENT, 4), Card("H2O", CardType.MOLECULE, 0)),  # 混合牌型
        (Card("Na", CardType.ELEMENT, 1), Card("K", CardType.ELEMENT, 1), Card("Ca", CardType.ELEMENT, 2)),  # 不连续
    ]
    
    for card1, card2, card3 in test_sequences:
        is_seq, msg = game.win_checker.check_sequence(card1, card2, card3)
        status = "✅" if is_seq else "❌"
        print(f"{status} {card1} + {card2} + {card3}：{msg}")
    
    # 测试刻子检查
    print("\n" + "=" * 50)
    print("测试刻子检查")
    print("=" * 50)
    
    test_triplets = [
        (Card("Na", CardType.ELEMENT, 1), Card("Na", CardType.ELEMENT, 1), Card("Na", CardType.ELEMENT, 1)),
        (Card("H2O", CardType.MOLECULE, 0), Card("H2O", CardType.MOLECULE, 0), Card("H2O", CardType.MOLECULE, 0)),
        (Card("Cl⁻¹", CardType.ION, -1), Card("Cl⁻¹", CardType.ION, -1), Card("Cl⁻¹", CardType.ION, -1)),
        (Card("Na", CardType.ELEMENT, 1), Card("Na", CardType.ELEMENT, 1), Card("K", CardType.ELEMENT, 1)),  # 牌名不同
        (Card("Na", CardType.ELEMENT, 1), Card("Na", CardType.ELEMENT, 1), Card("Cl⁻¹", CardType.ION, -1)),  # 牌型不同
        (Card("H", CardType.ELEMENT, 1), Card("C", CardType.ELEMENT, 4), Card("N", CardType.ELEMENT, 3)),  # 都不同
    ]
    
    for card1, card2, card3 in test_triplets:
        is_triplet, msg = game.win_checker.check_triplet(card1, card2, card3)
        status = "✅" if is_triplet else "❌"
        print(f"{status} {card1} + {card2} + {card3}：{msg}")
    
    # 测试和牌检查
    print("\n" + "=" * 50)
    print("测试和牌检查")
    print("=" * 50)
    
    # 创建一个和牌的手牌示例
    test_hand_win = [
        Card("Na", CardType.ELEMENT, 1),
        Card("Cl⁻¹", CardType.ION, -1),
        Card("Na", CardType.ELEMENT, 1),
        Card("Cl⁻¹", CardType.ION, -1),
        Card("H", CardType.ELEMENT, 1),
        Card("OH⁻¹", CardType.ION, -1),
        Card("H", CardType.ELEMENT, 1),
        Card("OH⁻¹", CardType.ION, -1),
        Card("H2O", CardType.MOLECULE, 0),
        Card("H2O", CardType.MOLECULE, 0),
        Card("H2O", CardType.MOLECULE, 0),
        Card("H2O", CardType.MOLECULE, 0),
        Card("Ca", CardType.ELEMENT, 2),
        Card("SO4⁻²", CardType.ION, -2),
    ]
    
    is_win, msg = game.win_checker.check_win(test_hand_win)
    print(f"\n测试手牌：{[str(c) for c in test_hand_win]}")
    print(f"化合价总和：{sum(c.valence for c in test_hand_win)}")
    print(f"结果：{msg}")
