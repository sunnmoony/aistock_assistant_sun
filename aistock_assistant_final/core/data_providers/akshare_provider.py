# -*- coding: utf-8 -*-
"""
===================================
A股智能分析系统 - AkShare数据提供者
===================================

职责:
1. 提供A股实时行情数据
2. 提供历史K线数据
3. 提供财务数据
4. 提供指数数据
5. 支持多数据源切换（AkShare/硅基流动/火山云）
6. 优先级: 0 (最高优先级)
"""

from typing import Dict, List, Optional, Any
import logging
import os
import pandas as pd

os.environ.pop('HTTP_PROXY', None)
os.environ.pop('HTTPS_PROXY', None)
os.environ.pop('http_proxy', None)
os.environ.pop('https_proxy', None)

logger = logging.getLogger(__name__)


class AkShareProvider:
    """AkShare数据提供者 - 优先级0"""

    def __init__(self):
        """初始化AkShare数据提供者"""
        self.cache = {}
        self.cache_timeout = 60
        self.current_source = "akshare"
        self._setup_akshare()
        logger.info("AkShare数据提供者初始化完成")

    def _setup_akshare(self):
        """设置AkShare库"""
        try:
            import akshare as ak
            self.ak = ak
            logger.info("AkShare库加载成功")
        except ImportError:
            logger.error("AkShare库未安装，请运行: pip install akshare")
            raise ImportError("AkShare库未安装")

    def _setup_siliconflow(self):
        """设置硅基流动库"""
        try:
            from siliconflow import StockData
            self.siliconflow = StockData()
            logger.info("硅基流动库加载成功")
        except ImportError:
            logger.warning("硅基流动库未安装，请运行: pip install siliconflow")
            self.siliconflow = None

    def _setup_volcano(self):
        """设置火山云库"""
        try:
            from volcano import StockData
            self.volcano = StockData()
            logger.info("火山云库加载成功")
        except ImportError:
            logger.warning("火山云库未安装，请运行: pip install volcano")
            self.volcano = None

    def set_data_source(self, source: str = "akshare"):
        """
        设置数据源
        
        参数：
            source: 数据源（akshare/siliconflow/volcano）
        """
        self.current_source = source
        logger.info(f"数据源已切换为: {source}")

    def get_name(self) -> str:
        """获取数据源名称"""
        source_names = {
            "akshare": "AkShare",
            "siliconflow": "硅基流动",
            "volcano": "火山云"
        }
        return source_names.get(self.current_source, "AkShare")

    def health_check(self) -> bool:
        """健康检查"""
        try:
            if self.current_source == "akshare":
                df = self.get_stock_realtime("000001")
            elif self.current_source == "siliconflow":
                df = self._get_stock_realtime_siliconflow("000001")
            elif self.current_source == "volcano":
                df = self._get_stock_realtime_volcano("000001")
            else:
                df = self.get_stock_realtime("000001")
            
            return df is not None
        except Exception as e:
            logger.error(f"健康检查失败: {e}")
            return False

    def get_stock_realtime(self, stock_code: str) -> Optional[Dict[str, Any]]:
        """
        获取股票实时行情

        Args:
            stock_code: 股票代码

        Returns:
            股票实时数据字典
        """
        try:
            if self.current_source == "akshare":
                return self._get_stock_realtime_akshare(stock_code)
            elif self.current_source == "siliconflow":
                return self._get_stock_realtime_siliconflow(stock_code)
            elif self.current_source == "volcano":
                return self._get_stock_realtime_volcano(stock_code)
            else:
                return self._get_stock_realtime_akshare(stock_code)
        except Exception as e:
            logger.error(f"获取股票 {stock_code} 实时数据失败: {e}")
            return None

    def _get_stock_realtime_akshare(self, stock_code: str) -> Optional[Dict[str, Any]]:
        """使用AkShare获取实时行情"""
        try:
            import pandas as pd
            
            symbol = self._convert_symbol(stock_code)
            
            df = self.ak.stock_zh_a_spot_em()
            
            if df is None or df.empty:
                logger.warning(f"AkShare未找到股票 {stock_code} 的数据")
                return None
            
            stock_data = df[df['代码'] == symbol]
            
            if stock_data.empty:
                logger.warning(f"AkShare未找到股票 {stock_code} ({symbol}) 的数据")
                return None
            
            row = stock_data.iloc[0]
            
            pre_close = float(row.get('昨收', 0))
            price = float(row.get('最新价', 0))
            change = price - pre_close
            change_percent = (change / pre_close * 100) if pre_close > 0 else 0
            
            return {
                "code": stock_code,
                "name": row.get('名称', f"股票{stock_code}"),
                "price": price,
                "change": change,
                "change_percent": change_percent,
                "open": float(row.get('今开', 0)),
                "high": float(row.get('最高', 0)),
                "low": float(row.get('最低', 0)),
                "pre_close": pre_close,
                "volume": int(row.get('成交量', 0)),
                "turnover": float(row.get('成交额', 0)),
                "amplitude": 0,
                "pe": float(row.get('市盈率-动态', 0)) if pd.notna(row.get('市盈率-动态')) else 0,
                "market_cap": float(row.get('总市值', 0)) if pd.notna(row.get('总市值')) else 0
            }
        except Exception as e:
            logger.error(f"AkShare获取股票 {stock_code} 实时数据失败: {e}")
            return None

    def _get_stock_realtime_siliconflow(self, stock_code: str) -> Optional[Dict[str, Any]]:
        """使用硅基流动获取实时行情"""
        try:
            if not self.siliconflow:
                logger.warning("硅基流动库未初始化")
                return None
            
            data = self.siliconflow.get_stock_realtime(stock_code)
            
            if data:
                logger.debug(f"硅基流动获取股票 {stock_code} 数据成功")
                return data
            else:
                logger.warning(f"硅基流动未找到股票 {stock_code} 的数据")
                return None
        except Exception as e:
            logger.error(f"硅基流动获取股票 {stock_code} 实时数据失败: {e}")
            return None

    def _get_stock_realtime_volcano(self, stock_code: str) -> Optional[Dict[str, Any]]:
        """使用火山云获取实时行情"""
        try:
            if not self.volcano:
                logger.warning("火山云库未初始化")
                return None
            
            data = self.volcano.get_stock_realtime(stock_code)
            
            if data:
                logger.debug(f"火山云获取股票 {stock_code} 数据成功")
                return data
            else:
                logger.warning(f"火山云未找到股票 {stock_code} 的数据")
                return None
        except Exception as e:
            logger.error(f"火山云获取股票 {stock_code} 实时数据失败: {e}")
            return None

    def get_stock_history(self, stock_code: str, period: str = "daily",
                        start_date: str = None, end_date: str = None) -> Any:
        """
        获取股票历史K线数据

        Args:
            stock_code: 股票代码
            period: 周期(daily=日线, weekly=周线, monthly=月线)
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            K线数据DataFrame
        """
        try:
            if self.current_source == "akshare":
                return self._get_stock_history_akshare(stock_code, period, start_date, end_date)
            elif self.current_source == "siliconflow":
                return self._get_stock_history_siliconflow(stock_code, period, start_date, end_date)
            elif self.current_source == "volcano":
                return self._get_stock_history_volcano(stock_code, period, start_date, end_date)
            else:
                return self._get_stock_history_akshare(stock_code, period, start_date, end_date)
        except Exception as e:
            logger.error(f"获取股票 {stock_code} 历史数据失败: {e}")
            import pandas as pd
            return pd.DataFrame()

    def _get_stock_history_akshare(self, stock_code: str, period: str,
                                start_date: str = None, end_date: str = None) -> Any:
        """使用AkShare获取历史K线数据"""
        try:
            import pandas as pd
            from datetime import datetime, timedelta
            
            symbol = self._convert_symbol(stock_code)
            
            if not start_date:
                start_date = (datetime.now() - timedelta(days=365)).strftime("%Y%m%d")
            else:
                start_date = start_date.replace("-", "")
            
            if not end_date:
                end_date = datetime.now().strftime("%Y%m%d")
            else:
                end_date = end_date.replace("-", "")
            
            period_map = {
                'daily': 'daily',
                'weekly': 'weekly',
                'monthly': 'monthly'
            }
            ak_period = period_map.get(period, 'daily')
            
            df = self.ak.stock_zh_a_hist(
                symbol=symbol,
                period=ak_period,
                start_date=start_date,
                end_date=end_date,
                adjust="qfq"
            )
            
            if df is None or df.empty:
                logger.warning(f"AkShare未找到股票 {stock_code} 的历史数据")
                return pd.DataFrame()
            
            df = df.rename(columns={
                '日期': 'date',
                '开盘': 'open',
                '收盘': 'close',
                '最高': 'high',
                '最低': 'low',
                '成交量': 'volume',
                '成交额': 'amount'
            })
            
            df = df[['date', 'open', 'high', 'low', 'close', 'volume', 'amount']]
            
            logger.debug(f"AkShare获取股票 {stock_code} 历史数据成功: {len(df)}条记录")
            return df
        except Exception as e:
            logger.error(f"AkShare获取股票 {stock_code} 历史数据失败: {e}")
            import pandas as pd
            return pd.DataFrame()

    def _get_stock_history_siliconflow(self, stock_code: str, period: str,
                                     start_date: str = None, end_date: str = None) -> Any:
        """使用硅基流动获取历史K线数据"""
        try:
            if not self.siliconflow:
                logger.warning("硅基流动库未初始化")
                return pd.DataFrame()
            
            df = self.siliconflow.get_stock_history(stock_code, period, start_date, end_date)
            
            if df is None or df.empty:
                logger.warning(f"硅基流动未找到股票 {stock_code} 的历史数据")
                return pd.DataFrame()
            
            logger.debug(f"硅基流动获取股票 {stock_code} 历史数据成功: {len(df)}条记录")
            return df
        except Exception as e:
            logger.error(f"硅基流动获取股票 {stock_code} 历史数据失败: {e}")
            import pandas as pd
            return pd.DataFrame()

    def _get_stock_history_volcano(self, stock_code: str, period: str,
                                   start_date: str = None, end_date: str = None) -> Any:
        """使用火山云获取历史K线数据"""
        try:
            if not self.volcano:
                logger.warning("火山云库未初始化")
                return pd.DataFrame()
            
            df = self.volcano.get_stock_history(stock_code, period, start_date, end_date)
            
            if df is None or df.empty:
                logger.warning(f"火山云未找到股票 {stock_code} 的历史数据")
                return pd.DataFrame()
            
            logger.debug(f"火山云获取股票 {stock_code} 历史数据成功: {len(df)}条记录")
            return df
        except Exception as e:
            logger.error(f"火山云获取股票 {stock_code} 历史数据失败: {e}")
            import pandas as pd
            return pd.DataFrame()

    def get_index_data(self, index_code: str = "000001") -> Optional[Dict[str, Any]]:
        """
        获取指数数据

        Args:
            index_code: 指数代码

        Returns:
            指数数据字典
        """
        try:
            if self.current_source == "akshare":
                return self._get_index_data_akshare(index_code)
            elif self.current_source == "siliconflow":
                return self._get_index_data_siliconflow(index_code)
            elif self.current_source == "volcano":
                return self._get_index_data_volcano(index_code)
            else:
                return self._get_index_data_akshare(index_code)
        except Exception as e:
            logger.error(f"获取指数 {index_code} 数据失败: {e}")
            return None

    def _get_index_data_akshare(self, index_code: str) -> Optional[Dict[str, Any]]:
        """使用AkShare获取指数数据"""
        try:
            import pandas as pd
            
            index_map = {
                "000001": "上证指数",
                "399001": "深证成指",
                "399006": "创业板指",
                "688981": "科创50"
            }
            
            try:
                df = self.ak.stock_zh_index_spot_em(symbol="上证系列指数")
            except Exception:
                try:
                    df = self.ak.index_zh_a_hist_min_em(symbol=index_code, period="1", adjust="")
                    if df is not None and not df.empty:
                        row = df.iloc[-1]
                        return {
                            "code": index_code,
                            "name": index_map.get(index_code, f"指数{index_code}"),
                            "price": float(row.get('收盘', 0)),
                            "change": 0,
                            "change_percent": 0,
                            "open": float(row.get('开盘', 0)),
                            "high": float(row.get('最高', 0)),
                            "low": float(row.get('最低', 0)),
                            "pre_close": float(row.get('收盘', 0)),
                            "volume": int(row.get('成交量', 0)),
                            "turnover": 0
                        }
                except Exception as e2:
                    logger.error(f"AkShare获取指数 {index_code} 数据失败(备用方法): {e2}")
                    return None
            
            if df is None or df.empty:
                logger.warning(f"AkShare未找到指数数据")
                return None
            
            index_data = df[df['代码'] == index_code]
            
            if index_data.empty:
                logger.warning(f"AkShare未找到指数 {index_code} 的数据")
                return None
            
            row = index_data.iloc[0]
            
            pre_close = float(row.get('昨收', 0))
            price = float(row.get('最新价', 0))
            change = price - pre_close
            change_percent = (change / pre_close * 100) if pre_close > 0 else 0
            
            return {
                "code": index_code,
                "name": index_map.get(index_code, f"指数{index_code}"),
                "price": price,
                "change": change,
                "change_percent": change_percent,
                "open": float(row.get('今开', 0)),
                "high": float(row.get('最高', 0)),
                "low": float(row.get('最低', 0)),
                "pre_close": pre_close,
                "volume": int(row.get('成交量', 0)),
                "turnover": float(row.get('成交额', 0))
            }
        except Exception as e:
            logger.error(f"AkShare获取指数 {index_code} 数据失败: {e}")
            return None

    def _get_index_data_siliconflow(self, index_code: str) -> Optional[Dict[str, Any]]:
        """使用硅基流动获取指数数据"""
        try:
            if not self.siliconflow:
                logger.warning("硅基流动库未初始化")
                return None
            
            data = self.siliconflow.get_index_data(index_code)
            
            if data:
                logger.debug(f"硅基流动获取指数 {index_code} 数据成功")
                return data
            else:
                logger.warning(f"硅基流动未找到指数 {index_code} 的数据")
                return None
        except Exception as e:
            logger.error(f"硅基流动获取指数 {index_code} 数据失败: {e}")
            return None

    def _get_index_data_volcano(self, index_code: str) -> Optional[Dict[str, Any]]:
        """使用火山云获取指数数据"""
        try:
            if not self.volcano:
                logger.warning("火山云库未初始化")
                return None
            
            data = self.volcano.get_index_data(index_code)
            
            if data:
                logger.debug(f"火山云获取指数 {index_code} 数据成功")
                return data
            else:
                logger.warning(f"火山云未找到指数 {index_code} 的数据")
                return None
        except Exception as e:
            logger.error(f"火山云获取指数 {index_code} 数据失败: {e}")
            return None

    def get_all_indices(self) -> List[Dict[str, Any]]:
        """获取主要指数数据"""
        try:
            if self.current_source == "akshare":
                return self._get_all_indices_akshare()
            elif self.current_source == "siliconflow":
                return self._get_all_indices_siliconflow()
            elif self.current_source == "volcano":
                return self._get_all_indices_volcano()
            else:
                return self._get_all_indices_akshare()
        except Exception as e:
            logger.error(f"获取主要指数数据失败: {e}")
            return []

    def _get_all_indices_akshare(self) -> List[Dict[str, Any]]:
        """使用AkShare获取主要指数数据"""
        try:
            indices = []
            index_codes = {
                "000001": "上证指数",
                "399001": "深证成指",
                "399006": "创业板指",
                "688981": "科创50"
            }
            
            for code, name in index_codes.items():
                data = self.get_index_data(code)
                if data:
                    indices.append(data)
            
            if indices:
                logger.debug(f"获取主要指数数据成功: {len(indices)}个指数")
            else:
                logger.warning("未获取到主要指数数据")
            
            return indices
        except Exception as e:
            logger.error(f"获取主要指数数据失败: {e}")
            return []

    def _get_all_indices_siliconflow(self) -> List[Dict[str, Any]]:
        """使用硅基流动获取主要指数数据"""
        try:
            if not self.siliconflow:
                logger.warning("硅基流动库未初始化")
                return []
            
            indices = self.siliconflow.get_all_indices()
            
            if indices:
                logger.debug(f"获取主要指数数据成功: {len(indices)}个指数")
            else:
                logger.warning("未获取到主要指数数据")
            
            return indices
        except Exception as e:
            logger.error(f"获取主要指数数据失败: {e}")
            return []

    def _get_all_indices_volcano(self) -> List[Dict[str, Any]]:
        """使用火山云获取主要指数数据"""
        try:
            if not self.volcano:
                logger.warning("火山云库未初始化")
                return []
            
            indices = self.volcano.get_all_indices()
            
            if indices:
                logger.debug(f"获取主要指数数据成功: {len(indices)}个指数")
            else:
                logger.warning("未获取到主要指数数据")
            
            return indices
        except Exception as e:
            logger.error(f"获取主要指数数据失败: {e}")
            return []

    def get_market_summary(self) -> Dict[str, Any]:
        """获取市场概况"""
        try:
            indices = self.get_all_indices()
            
            if not indices:
                return {}
            
            rise_count = sum(1 for idx in indices if idx.get('change_percent', 0) > 0)
            fall_count = sum(1 for idx in indices if idx.get('change_percent', 0) < 0)
            flat_count = len(indices) - rise_count - fall_count
            
            return {
                "rise_count": rise_count,
                "fall_count": fall_count,
                "flat_count": flat_count,
                "total_turnover": sum(idx.get('turnover', 0) for idx in indices)
            }
        except Exception as e:
            logger.error(f"AkShare获取市场概况失败: {e}")
            return {}

    def search_stock(self, keyword: str) -> List[Dict[str, Any]]:
        """搜索股票"""
        try:
            import pandas as pd
            
            df = self.ak.stock_zh_a_spot_em()
            
            if df is None or df.empty:
                return []
            
            results = df[df['名称'].str.contains(keyword, na=False) | 
                       df['代码'].str.contains(keyword, na=False)]
            
            if results.empty:
                return []
            
            search_results = []
            for _, row in results.head(50).iterrows():
                search_results.append({
                    "code": row.get('代码', ''),
                    "name": row.get('名称', '')
                })
            
            return search_results
        except Exception as e:
            logger.error(f"AkShare搜索股票失败: {e}")
            return []

    def get_financial_data(self, stock_code: str) -> Dict[str, Any]:
        """
        获取财务数据

        Args:
            stock_code: 股票代码

        Returns:
            财务数据字典
        """
        try:
            import pandas as pd
            
            symbol = self._convert_symbol(stock_code)
            
            df = self.ak.stock_individual_info_em(symbol=symbol)
            
            if df is None or df.empty:
                logger.warning(f"AkShare未找到股票 {stock_code} 的财务数据")
                return {}
            
            row = df.iloc[0]
            
            return {
                "code": stock_code,
                "name": row.get('股票简称', ''),
                "pe": float(row.get('市盈率-动态', 0)) if pd.notna(row.get('市盈率-动态')) else 0,
                "pb": float(row.get('市净率', 0)) if pd.notna(row.get('市净率')) else 0,
                "roe": float(row.get('净资产收益率', 0)) if pd.notna(row.get('净资产收益率')) else 0,
                "total_assets": float(row.get('总资产', 0)) if pd.notna(row.get('总资产')) else 0,
                "total_liabilities": float(row.get('总负债', 0)) if pd.notna(row.get('总负债')) else 0,
                "revenue": float(row.get('营业总收入', 0)) if pd.notna(row.get('营业总收入')) else 0,
                "net_profit": float(row.get('净利润', 0)) if pd.notna(row.get('净利润')) else 0,
            }
        except Exception as e:
            logger.error(f"AkShare获取股票 {stock_code} 财务数据失败: {e}")
            return {}

    def get_sector_data(self) -> List[Dict[str, Any]]:
        """获取板块数据"""
        try:
            import pandas as pd
            
            df = self.ak.stock_board_industry_name_em()
            
            if df is None or df.empty:
                return []
            
            sectors = []
            for _, row in df.head(50).iterrows():
                sectors.append({
                    "name": row.get('板块名称', ''),
                    "code": row.get('板块代码', '')
                })
            
            return sectors
        except Exception as e:
            logger.error(f"AkShare获取板块数据失败: {e}")
            return []

    def get_sector_stocks(self, sector_name: str) -> List[Dict[str, Any]]:
        """获取板块内股票列表"""
        try:
            import pandas as pd
            
            df = self.ak.stock_board_industry_cons_em(symbol=sector_name)
            
            if df is None or df.empty:
                return []
            
            stocks = []
            for _, row in df.head(100).iterrows():
                stocks.append({
                    "code": row.get('代码', ''),
                    "name": row.get('名称', '')
                })
            
            return stocks
        except Exception as e:
            logger.error(f"AkShare获取板块 {sector_name} 股票列表失败: {e}")
            return []

    def get_sector_rank(self) -> List[Dict[str, Any]]:
        """获取板块涨跌幅排行"""
        try:
            import pandas as pd
            
            df = self.ak.stock_board_industry_name_em()
            
            if df is None or df.empty:
                return []
            
            ranks = []
            for _, row in df.head(50).iterrows():
                ranks.append({
                    "name": row.get('板块名称', ''),
                    "code": row.get('板块代码', ''),
                    "change_percent": 0
                })
            
            return ranks
        except Exception as e:
            logger.error(f"AkShare获取板块排行失败: {e}")
            return []

    def get_fund_flow(self, stock_code: str = None) -> List[Dict[str, Any]]:
        """获取资金流向数据"""
        try:
            import pandas as pd
            
            if stock_code:
                symbol = self._convert_symbol(stock_code)
                df = self.ak.stock_individual_fund_flow_em(stock=symbol, market="sh" if symbol.startswith('6') else "sz")
            else:
                df = self.ak.stock_market_fund_flow_em()
            
            if df is None or df.empty:
                return []
            
            flows = []
            for _, row in df.head(50).iterrows():
                flows.append({
                    "code": row.get('代码', ''),
                    "name": row.get('名称', ''),
                    "main_in": float(row.get('主力净流入', 0)) if pd.notna(row.get('主力净流入')) else 0,
                    "main_out": float(row.get('主力净流出', 0)) if pd.notna(row.get('主力净流出')) else 0,
                    "net_inflow": float(row.get('净流入', 0)) if pd.notna(row.get('净流入')) else 0
                })
            
            return flows
        except Exception as e:
            logger.error(f"AkShare获取资金流向数据失败: {e}")
            return []

    def get_stock_list(self, market: str = "SH") -> List[Dict[str, Any]]:
        """获取股票列表"""
        try:
            import pandas as pd
            
            df = self.ak.stock_zh_a_spot_em()
            
            if df is None or df.empty:
                return []
            
            if market == "SH":
                stocks_df = df[df['代码'].str.startswith('6')]
            else:
                stocks_df = df[df['代码'].str.startswith(('0', '3'))]
            
            stocks = []
            for _, row in stocks_df.head(1000).iterrows():
                stocks.append({
                    "code": row.get('代码', ''),
                    "name": row.get('名称', '')
                })
            
            return stocks
        except Exception as e:
            logger.error(f"AkShare获取股票列表失败: {e}")
            return []

    def _convert_symbol(self, stock_code: str) -> str:
        """
        转换股票代码为AkShare格式

        Args:
            stock_code: 股票代码(6位数字)

        Returns:
            AkShare格式的股票代码
        """
        if not stock_code or len(stock_code) != 6:
            return stock_code
        
        if stock_code.startswith('6'):
            return f"sh{stock_code}"
        elif stock_code.startswith(('0', '3')):
            return f"sz{stock_code}"
        else:
            return stock_code
