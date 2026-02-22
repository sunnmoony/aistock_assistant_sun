from typing import Dict, List, Optional, Any
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)


class TechnicalIndicators:
    """技术指标计算器"""

    @staticmethod
    def calculate_ma(df: pd.DataFrame, periods: List[int] = [5, 10, 20, 60]) -> pd.DataFrame:
        """
        计算移动平均线（MA）

        Args:
            df: K线数据DataFrame（需包含close列）
            periods: 周期列表

        Returns:
            包含MA列的DataFrame
        """
        try:
            result_df = df.copy()

            for period in periods:
                result_df[f'MA{period}'] = df['close'].rolling(window=period).mean()

            logger.info(f"计算MA指标: {periods}")
            return result_df
        except Exception as e:
            logger.error(f"计算MA指标失败: {e}")
            return df

    @staticmethod
    def calculate_macd(df: pd.DataFrame, fast: int = 12, slow: int = 26, 
                     signal: int = 9) -> pd.DataFrame:
        """
        计算MACD指标

        Args:
            df: K线数据DataFrame
            fast: 快线周期
            slow: 慢线周期
            signal: 信号线周期

        Returns:
            包含MACD列的DataFrame
        """
        try:
            result_df = df.copy()

            ema_fast = df['close'].ewm(span=fast, adjust=False).mean()
            ema_slow = df['close'].ewm(span=slow, adjust=False).mean()

            result_df['DIF'] = ema_fast - ema_slow
            result_df['DEA'] = result_df['DIF'].ewm(span=signal, adjust=False).mean()
            result_df['MACD'] = (result_df['DIF'] - result_df['DEA']) * 2

            logger.info(f"计算MACD指标: fast={fast}, slow={slow}, signal={signal}")
            return result_df
        except Exception as e:
            logger.error(f"计算MACD指标失败: {e}")
            return df

    @staticmethod
    def calculate_rsi(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """
        计算RSI指标（相对强弱指标）

        Args:
            df: K线数据DataFrame
            period: 周期

        Returns:
            包含RSI列的DataFrame
        """
        try:
            result_df = df.copy()

            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

            rs = gain / loss
            result_df['RSI'] = 100 - (100 / (1 + rs))

            logger.info(f"计算RSI指标: period={period}")
            return result_df
        except Exception as e:
            logger.error(f"计算RSI指标失败: {e}")
            return df

    @staticmethod
    def calculate_kdj(df: pd.DataFrame, n: int = 9, m1: int = 3, m2: int = 3) -> pd.DataFrame:
        """
        计算KDJ指标（随机指标）

        Args:
            df: K线数据DataFrame
            n: 周期
            m1: K值平滑周期
            m2: D值平滑周期

        Returns:
            包含KDJ列的DataFrame
        """
        try:
            result_df = df.copy()

            low_list = df['low'].rolling(window=n, min_periods=1).min()
            high_list = df['high'].rolling(window=n, min_periods=1).max()

            rsv = (df['close'] - low_list) / (high_list - low_list) * 100

            result_df['K'] = rsv.ewm(com=m1 - 1, adjust=False).mean()
            result_df['D'] = result_df['K'].ewm(com=m2 - 1, adjust=False).mean()
            result_df['J'] = 3 * result_df['K'] - 2 * result_df['D']

            logger.info(f"计算KDJ指标: n={n}, m1={m1}, m2={m2}")
            return result_df
        except Exception as e:
            logger.error(f"计算KDJ指标失败: {e}")
            return df

    @staticmethod
    def calculate_boll(df: pd.DataFrame, period: int = 20, std_dev: float = 2.0) -> pd.DataFrame:
        """
        计算BOLL指标（布林带）

        Args:
            df: K线数据DataFrame
            period: 周期
            std_dev: 标准差倍数

        Returns:
            包含BOLL列的DataFrame
        """
        try:
            result_df = df.copy()

            result_df['BOLL_MID'] = df['close'].rolling(window=period).mean()
            std = df['close'].rolling(window=period).std()

            result_df['BOLL_UP'] = result_df['BOLL_MID'] + std * std_dev
            result_df['BOLL_LOW'] = result_df['BOLL_MID'] - std * std_dev

            logger.info(f"计算BOLL指标: period={period}, std_dev={std_dev}")
            return result_df
        except Exception as e:
            logger.error(f"计算BOLL指标失败: {e}")
            return df

    @staticmethod
    def calculate_obv(df: pd.DataFrame) -> pd.DataFrame:
        """
        计算OBV指标（能量潮）

        Args:
            df: K线数据DataFrame

        Returns:
            包含OBV列的DataFrame
        """
        try:
            result_df = df.copy()

            change = df['close'].diff()
            obv = (np.where(change > 0, df['volume'], 
                       np.where(change < 0, -df['volume'], 0))).cumsum()

            result_df['OBV'] = obv

            logger.info("计算OBV指标")
            return result_df
        except Exception as e:
            logger.error(f"计算OBV指标失败: {e}")
            return df

    @staticmethod
    def calculate_atr(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """
        计算ATR指标（真实波幅）

        Args:
            df: K线数据DataFrame
            period: 周期

        Returns:
            包含ATR列的DataFrame
        """
        try:
            result_df = df.copy()

            high_low = df['high'] - df['low']
            high_close = np.abs(df['high'] - df['close'].shift())
            low_close = np.abs(df['low'] - df['close'].shift())

            tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
            result_df['ATR'] = tr.rolling(window=period).mean()

            logger.info(f"计算ATR指标: period={period}")
            return result_df
        except Exception as e:
            logger.error(f"计算ATR指标失败: {e}")
            return df

    @staticmethod
    def calculate_cci(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """
        计算CCI指标（顺势指标）

        Args:
            df: K线数据DataFrame
            period: 周期

        Returns:
            包含CCI列的DataFrame
        """
        try:
            result_df = df.copy()

            tp = (df['high'] + df['low'] + df['close']) / 3
            ma_tp = tp.rolling(window=period).mean()
            md = tp.rolling(window=period).apply(lambda x: np.abs(x - x.mean()).mean())

            result_df['CCI'] = (tp - ma_tp) / (0.015 * md)

            logger.info(f"计算CCI指标: period={period}")
            return result_df
        except Exception as e:
            logger.error(f"计算CCI指标失败: {e}")
            return df

    @staticmethod
    def calculate_all(df: pd.DataFrame) -> pd.DataFrame:
        """
        计算所有技术指标

        Args:
            df: K线数据DataFrame

        Returns:
            包含所有指标的DataFrame
        """
        try:
            result_df = df.copy()

            result_df = TechnicalIndicators.calculate_ma(result_df)
            result_df = TechnicalIndicators.calculate_macd(result_df)
            result_df = TechnicalIndicators.calculate_rsi(result_df)
            result_df = TechnicalIndicators.calculate_kdj(result_df)
            result_df = TechnicalIndicators.calculate_boll(result_df)
            result_df = TechnicalIndicators.calculate_obv(result_df)
            result_df = TechnicalIndicators.calculate_atr(result_df)
            result_df = TechnicalIndicators.calculate_cci(result_df)

            logger.info("计算所有技术指标完成")
            return result_df
        except Exception as e:
            logger.error(f"计算所有技术指标失败: {e}")
            return df

    @staticmethod
    def get_latest_signals(df: pd.DataFrame) -> Dict[str, Any]:
        """
        获取最新技术指标信号

        Args:
            df: 包含技术指标的DataFrame

        Returns:
            技术指标信号字典
        """
        try:
            if df.empty:
                return {}

            latest = df.iloc[-1]

            signals = {
                'price': latest.get('close', 0),
                'ma5': latest.get('MA5', 0),
                'ma10': latest.get('MA10', 0),
                'ma20': latest.get('MA20', 0),
                'ma60': latest.get('MA60', 0),
                'macd_dif': latest.get('DIF', 0),
                'macd_dea': latest.get('DEA', 0),
                'macd': latest.get('MACD', 0),
                'rsi': latest.get('RSI', 50),
                'k': latest.get('K', 50),
                'd': latest.get('D', 50),
                'j': latest.get('J', 50),
                'boll_up': latest.get('BOLL_UP', 0),
                'boll_mid': latest.get('BOLL_MID', 0),
                'boll_low': latest.get('BOLL_LOW', 0),
                'atr': latest.get('ATR', 0),
                'cci': latest.get('CCI', 0)
            }

            signals['ma_trend'] = TechnicalIndicators._analyze_ma_trend(signals)
            signals['macd_signal'] = TechnicalIndicators._analyze_macd_signal(signals)
            signals['rsi_signal'] = TechnicalIndicators._analyze_rsi_signal(signals)
            signals['kdj_signal'] = TechnicalIndicators._analyze_kdj_signal(signals)
            signals['boll_signal'] = TechnicalIndicators._analyze_boll_signal(signals)

            return signals
        except Exception as e:
            logger.error(f"获取技术指标信号失败: {e}")
            return {}

    @staticmethod
    def _analyze_ma_trend(signals: Dict[str, Any]) -> str:
        """分析均线趋势"""
        try:
            ma5 = signals.get('ma5', 0)
            ma10 = signals.get('ma10', 0)
            ma20 = signals.get('ma20', 0)
            price = signals.get('price', 0)

            if ma5 > ma10 > ma20 and price > ma5:
                return "多头排列，强势上涨"
            elif ma5 < ma10 < ma20 and price < ma5:
                return "空头排列，弱势下跌"
            elif ma5 > ma10 and price > ma20:
                return "短期上涨，中期震荡"
            elif ma5 < ma10 and price < ma20:
                return "短期下跌，中期震荡"
            else:
                return "均线缠绕，方向不明"
        except Exception as e:
            logger.error(f"分析均线趋势失败: {e}")
            return "无法判断"

    @staticmethod
    def _analyze_macd_signal(signals: Dict[str, Any]) -> str:
        """分析MACD信号"""
        try:
            dif = signals.get('macd_dif', 0)
            dea = signals.get('macd_dea', 0)
            macd = signals.get('macd', 0)

            if dif > dea and macd > 0:
                return "金叉向上，买入信号"
            elif dif < dea and macd < 0:
                return "死叉向下，卖出信号"
            elif dif > dea and macd < 0:
                return "金叉但零下，观望"
            elif dif < dea and macd > 0:
                return "死叉但零上，观望"
            else:
                return "无明显信号"
        except Exception as e:
            logger.error(f"分析MACD信号失败: {e}")
            return "无法判断"

    @staticmethod
    def _analyze_rsi_signal(signals: Dict[str, Any]) -> str:
        """分析RSI信号"""
        try:
            rsi = signals.get('rsi', 50)

            if rsi > 80:
                return "严重超买，注意风险"
            elif rsi > 70:
                return "超买区域，谨慎持有"
            elif rsi < 20:
                return "严重超卖，关注机会"
            elif rsi < 30:
                return "超卖区域，可考虑买入"
            elif rsi > 50:
                return "强势区域"
            else:
                return "弱势区域"
        except Exception as e:
            logger.error(f"分析RSI信号失败: {e}")
            return "无法判断"

    @staticmethod
    def _analyze_kdj_signal(signals: Dict[str, Any]) -> str:
        """分析KDJ信号"""
        try:
            k = signals.get('k', 50)
            d = signals.get('d', 50)
            j = signals.get('j', 50)

            if k > d and j > 0:
                return "KDJ金叉，买入信号"
            elif k < d and j < 0:
                return "KDJ死叉，卖出信号"
            elif k > 80 and d > 80:
                return "KDJ高位，注意风险"
            elif k < 20 and d < 20:
                return "KDJ低位，关注机会"
            else:
                return "KDJ中性"
        except Exception as e:
            logger.error(f"分析KDJ信号失败: {e}")
            return "无法判断"

    @staticmethod
    def _analyze_boll_signal(signals: Dict[str, Any]) -> str:
        """分析BOLL信号"""
        try:
            price = signals.get('price', 0)
            boll_up = signals.get('boll_up', 0)
            boll_mid = signals.get('boll_mid', 0)
            boll_low = signals.get('boll_low', 0)

            if price > boll_up:
                return "突破上轨，强势上涨"
            elif price < boll_low:
                return "跌破下轨，弱势下跌"
            elif price > boll_mid:
                return "在中轨上方，偏强"
            elif price < boll_mid:
                return "在中轨下方，偏弱"
            else:
                return "在中轨附近，震荡"
        except Exception as e:
            logger.error(f"分析BOLL信号失败: {e}")
            return "无法判断"