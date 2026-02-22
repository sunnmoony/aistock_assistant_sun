from typing import Dict, Any


class Stock:
    """股票数据模型"""
    
    def __init__(self, code: str, name: str, price: float, 
                 change: float, volume: int):
        self.code = code
        self.name = name
        self.price = price
        self.change = change
        self.volume = volume
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "code": self.code,
            "name": self.name,
            "price": self.price,
            "change": self.change,
            "volume": self.volume
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Stock':
        """从字典创建实例"""
        return cls(
            code=data.get("code", ""),
            name=data.get("name", ""),
            price=data.get("price", 0),
            change=data.get("change", 0),
            volume=data.get("volume", 0)
        )


class StockAnalysis:
    """股票分析结果模型"""
    
    def __init__(self, stock_code: str, trend: str, 
                 support: float, resistance: float, 
                 recommendation: str, reasoning: str):
        self.stock_code = stock_code
        self.trend = trend
        self.support = support
        self.resistance = resistance
        self.recommendation = recommendation
        self.reasoning = reasoning
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "stock_code": self.stock_code,
            "trend": self.trend,
            "support": self.support,
            "resistance": self.resistance,
            "recommendation": self.recommendation,
            "reasoning": self.reasoning
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StockAnalysis':
        """从字典创建实例"""
        return cls(
            stock_code=data.get("stock_code", ""),
            trend=data.get("trend", ""),
            support=data.get("support", 0),
            resistance=data.get("resistance", 0),
            recommendation=data.get("recommendation", ""),
            reasoning=data.get("reasoning", "")
        )
