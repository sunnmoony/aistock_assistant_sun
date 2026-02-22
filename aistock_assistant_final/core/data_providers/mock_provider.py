from typing import Dict, List, Optional, Any
import logging
import random
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class MockProvider:
    """@模拟数据提供者 - 离线模式使用"""

    def __init__(self):
        self.cache = {}
        self.last_update = datetime.now()

    def get_name(self) -> str:
        """@获取数据源名称"""
        return "Mock(模拟数据)"

    def health_check(self) -> bool:
        """@健康检查"""
        return True

    def get_stock_realtime(self, stock_code: str) -> Optional[Dict[str, Any]]:
        """
        @获取股票实时行情 - 模拟数据
        """
        try:
            # 模拟数据生成
            base_price = 5.0
            change_percent = random.uniform(-5, 5)
            change = base_price * change_percent / 100
            
            return {
                "code": stock_code,
                "name": self._get_stock_name(stock_code),
                "price": round(base_price + change, 2),
                "change": round(change, 2),
                "change_percent": round(change_percent, 2),
                "open": round(base_price + change * 0.5, 2),
                "high": round(base_price + change * 1.2, 2),
                "low": round(base_price + change * 0.8, 2),
                "pre_close": base_price,
                "volume": random.randint(100000, 10000000),
                "turnover": random.randint(50000000, 500000000),
                "amplitude": round(abs(change_percent) * 2, 2),
                "pe": round(random.uniform(10, 50), 2),
                "market_cap": round(random.uniform(50, 200), 2)
            }
        except Exception as e:
            logger.error(f"模拟数据获取失败 {stock_code}: {e}")
            return None

    def get_stock_history(self, stock_code: str, period: str = "daily",
                        start_date: str = None, end_date: str = None):
        """
        @获取股票历史K线数据 - 模拟数据
        """
        try:
            import pandas as pd
            
            # 生成模拟历史数据
            days = 100
            dates = pd.date_range(
                start=pd.Timestamp.now() - pd.Timedelta(days=days),
                end=pd.Timestamp.now(),
                freq='D'
            )
            
            base_price = 5.0
            data = []
            
            for i, date in enumerate(dates):
                price = base_price + random.uniform(-1, 1)
                change_percent = random.uniform(-5, 5)
                
                data.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'open': round(price, 2),
                    'high': round(price * 1.05, 2),
                    'low': round(price * 0.95, 2),
                    'close': round(price + change_percent / 100, 2),
                    'volume': random.randint(100000, 10000000),
                    'amount': random.randint(50000000, 500000000)
                })
            
            df = pd.DataFrame(data)
            df = df[['date', 'open', 'high', 'low', 'close', 'volume', 'amount']]
            
            return df
        except Exception as e:
            logger.error(f"模拟历史数据获取失败 {stock_code}: {e}")
            import pandas as pd
            return pd.DataFrame()

    def get_index_data(self, index_code: str = "000001") -> Optional[Dict[str, Any]]:
        """
        @获取指数实时数据 - 模拟数据
        """
        try:
            base_price = 3000
            change_percent = random.uniform(-2, 2)
            change = base_price * change_percent / 100
            
            return {
                "code": index_code,
                "name": self._get_index_name(index_code),
                "price": round(base_price + change, 2),
                "change": round(change, 2),
                "change_percent": round(change_percent, 2),
                "open": round(base_price + change * 0.3, 2),
                "high": round(base_price + change * 1.1, 2),
                "low": round(base_price + change * 0.9, 2),
                "pre_close": base_price,
                "volume": random.randint(1000000000, 5000000000),
                "turnover": random.randint(50000000000, 500000000000)
            }
        except Exception as e:
            logger.error(f"模拟指数数据获取失败 {index_code}: {e}")
            return None

    def get_all_indices(self) -> List[Dict[str, Any]]:
        """
        @获取主要指数数据 - 模拟数据
        """
        try:
            indices = [
                {"code": "000001", "name": "上证指数"},
                {"code": "399001", "name": "深证成指"},
                {"code": "399006", "name": "创业板指"},
                {"code": "688981", "name": "科创50"}
            ]
            
            result = []
            for index_info in indices:
                base_price = 3000 if index_info["code"] == "000001" else 10000
                change_percent = random.uniform(-2, 2)
                change = base_price * change_percent / 100
                
                result.append({
                    "code": index_info["code"],
                    "name": index_info["name"],
                    "price": round(base_price + change, 2),
                    "change": round(change, 2),
                    "change_percent": round(change_percent, 2),
                    "volume": random.randint(1000000000, 5000000000),
                    "turnover": random.randint(50000000000, 500000000000)
                })
            
            return result
        except Exception as e:
            logger.error(f"模拟指数列表获取失败: {e}")
            return []

    def get_sector_data(self) -> List[Dict[str, Any]]:
        """
        @获取板块数据 - 模拟数据
        """
        try:
            sectors = [
                {"name": "新能源", "change": random.uniform(-3, 5)},
                {"name": "半导体", "change": random.uniform(-3, 5)},
                {"name": "医药生物", "change": random.uniform(-3, 5)},
                {"name": "白酒", "change": random.uniform(-3, 5)},
                {"name": "银行", "change": random.uniform(-3, 5)},
                {"name": "房地产", "change": random.uniform(-3, 5)},
                {"name": "钢铁", "change": random.uniform(-3, 5)}
            ]
            
            return sectors
        except Exception as e:
            logger.error(f"模拟板块数据获取失败: {e}")
            return []

    def get_sector_stocks(self, sector_name: str) -> List[Dict[str, Any]]:
        """
        @获取板块内股票列表 - 模拟数据
        """
        try:
            stocks = []
            for i in range(10):
                base_price = random.uniform(5, 50)
                change_percent = random.uniform(-5, 5)
                
                stocks.append({
                    "code": f"{random.randint(600000, 609999)}",
                    "name": f"模拟股票{i}",
                    "price": round(base_price, 2),
                    "change_percent": round(change_percent, 2),
                    "volume": random.randint(100000, 10000000),
                    "turnover": random.randint(50000000, 500000000)
                })
            
            return stocks
        except Exception as e:
            logger.error(f"模拟板块股票获取失败: {e}")
            return []

    def get_sector_rank(self) -> List[Dict[str, Any]]:
        """
        @获取板块涨跌幅排行 - 模拟数据
        """
        try:
            sectors = [
                {"name": "新能源", "change": random.uniform(-3, 5), "leading_stock": "宁德时代"},
                {"name": "半导体", "change": random.uniform(-3, 5), "leading_stock": "中芯国际"},
                {"name": "医药生物", "change": random.uniform(-3, 5), "leading_stock": "恒瑞医药"},
                {"name": "白酒", "change": random.uniform(-3, 5), "leading_stock": "贵州茅台"},
                {"name": "银行", "change": random.uniform(-3, 5), "leading_stock": "招商银行"},
                {"name": "房地产", "change": random.uniform(-3, 5), "leading_stock": "万科A"},
                {"name": "钢铁", "change": random.uniform(-3, 5), "leading_stock": "宝钢股份"}
            ]
            
            # 按涨跌幅排序
            sectors.sort(key=lambda x: x["change"], reverse=True)
            
            return sectors[:20]
        except Exception as e:
            logger.error(f"模拟板块排行获取失败: {e}")
            return []

    def get_fund_flow(self, stock_code: str = None) -> List[Dict[str, Any]]:
        """
        @获取资金流向数据 - 模拟数据
        """
        try:
            flows = []
            stocks = ["贵州茅台", "五粮液", "招商银行", "中国平安", "平安银行", "恒瑞医药"]
            
            for i, stock in enumerate(stocks):
                flow = random.uniform(-100000000, 100000000)
                flows.append({
                    "rank": i + 1,
                    "code": f"{random.randint(600000, 609999)}",
                    "name": stock,
                    "flow": flow,
                    "price": random.uniform(10, 200)
                })
            
            # 按资金流向排序
            flows.sort(key=lambda x: x["flow"], reverse=True)
            
            return flows[:10]
        except Exception as e:
            logger.error(f"模拟资金流向获取失败: {e}")
            return []

    def get_stock_list(self, market: str = "SH") -> List[Dict[str, Any]]:
        """
        @获取股票列表 - 模拟数据
        """
        try:
            stocks = []
            for i in range(100):
                code = f"{random.randint(600000, 609999)}" if market == "SH" else f"{random.randint(000000, 999999)}"
                stocks.append({
                    "code": code,
                    "name": f"模拟股票{i}"
                })
            
            return stocks
        except Exception as e:
            logger.error(f"模拟股票列表获取失败: {e}")
            return []

    def search_stock(self, keyword: str) -> List[Dict[str, Any]]:
        """
        @搜索股票 - 模拟数据
        """
        try:
            results = []
            for i in range(10):
                code = f"{random.randint(600000, 609999)}"
                name = f"模拟股票{i}"
                
                if keyword in code or keyword in name:
                    results.append({
                        "code": code,
                        "name": name
                    })
            
            return results
        except Exception as e:
            logger.error(f"模拟股票搜索失败: {e}")
            return []

    def get_market_summary(self) -> Dict[str, Any]:
        """
        @获取市场概况 - 模拟数据
        """
        try:
            return {
                "rise_count": random.randint(2000, 4000),
                "fall_count": random.randint(1500, 3000),
                "flat_count": random.randint(100, 500),
                "limit_up_count": random.randint(50, 200),
                "limit_down_count": random.randint(30, 100),
                "total_turnover": random.randint(50000000000, 100000000000)
            }
        except Exception as e:
            logger.error(f"模拟市场概况获取失败: {e}")
            return {}

    def get_financial_data(self, stock_code: str) -> Dict[str, Any]:
        """
        @获取财务数据 - 模拟数据
        """
        try:
            return {
                "pe": round(random.uniform(10, 50), 2),
                "pb": round(random.uniform(0.5, 5), 2),
                "roe": round(random.uniform(5, 25), 2),
                "revenue": round(random.uniform(1000000000, 10000000000), 2),
                "profit": round(random.uniform(50000000, 500000000), 2),
                "debt_ratio": round(random.uniform(30, 70), 2)
            }
        except Exception as e:
            logger.error(f"模拟财务数据获取失败 {stock_code}: {e}")
            return {}

    def _get_stock_name(self, stock_code: str) -> str:
        """@根据股票代码获取模拟名称"""
        stock_names = {
            "600519": "贵州茅台",
            "000858": "五粮液",
            "600036": "招商银行",
            "000001": "平安银行",
            "600276": "恒瑞医药",
            "000333": "美的集团",
            "600887": "伊利股份",
            "000651": "格力电器",
            "601318": "中国平安",
            "600722": "金牛化工"
        }
        return stock_names.get(stock_code, f"股票{stock_code}")

    def _get_index_name(self, index_code: str) -> str:
        """@根据指数代码获取模拟名称"""
        index_names = {
            "000001": "上证指数",
            "399001": "深证成指",
            "399006": "创业板指",
            "688981": "科创50"
        }
        return index_names.get(index_code, f"指数{index_code}")
