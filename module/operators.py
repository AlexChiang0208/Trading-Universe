import pandas as pd
import numpy as np
import bottleneck as bn
from numba import jit
import operator

# Credit by Dean Lin, YL Chen, Alex Chiang

def ts_zscore(data, window):
    return (data - data.rolling(window).mean()) / data.rolling(window).std()


def ts_rank(data, window):
    return data.rolling(window).rank(pct=True)


def ts_ema(data, window):
    return data.ewm(span=window).mean()


def ts_continuous_atr(high, low, window):
    return (high - low).ewm(span=window).mean()


def delta(data, window=1):
    return data.diff(window)


def delay(data, window=1):
    return data.shift(window)


def pct_chg(data, window):
    if window >= 0:
        return delta(data, window)/delay(data, window).abs()
    else:
        return delta(data, window)/data.abs()


def div(data1, data2):

    result = (data1 / data2).replace([np.inf, -np.inf], np.NaN)
    result[(data1 == 0) | (data2 == 0)] = 0
    
    return result


def add(data1:pd.DataFrame, data2:pd.DataFrame)->pd.DataFrame:
    return operator.add(data1, data2)


def sub(data1:pd.DataFrame, data2:pd.DataFrame)->pd.DataFrame:
    return operator.sub(data1, data2)


def mul(data1:pd.DataFrame, data2:pd.DataFrame)->pd.DataFrame:
    return operator.mul(data1, data2)


def square(data:pd.DataFrame)->pd.DataFrame:
    return data*data


def curt(data:pd.DataFrame)->pd.DataFrame:
    return data*data*data


def log(data:pd.DataFrame)->pd.DataFrame:
    return np.log(data)


def log2(data:pd.DataFrame)->pd.DataFrame:
    return np.log2(data)


def log10(data:pd.DataFrame)->pd.DataFrame:
    return np.log10(data)


def data_abs(data:pd.DataFrame)->pd.DataFrame:
    return data.abs()


def rdiv(data:pd.DataFrame)->pd.DataFrame:
    return 1/data


def AdaptiveMovingAverage(data, window, fast, slow):
    """
    計算Adaptive Moving Average (AMA)指標
    :param data: 資料序列
    :param window: 計算AMA所需的時間窗口長度
    :param fast: 快速平滑指數加權平均數的權重
    :param slow: 慢速平滑指數加權平均數的權重
    :return: AMA指標序列
    ---
    Dean 說可能存在 bug, 需要檢查
    """
    use_index=data.index
    volatility = abs(data.diff(1)).rolling(window).sum().values  # 計算收盤價變化率
    direction=data.diff(window).values
    fastsc = 2 / (fast + 1)  # 計算快速平滑指數加權平均數的平滑因子
    slowsc = 2 / (slow + 1)  # 計算慢速平滑指數加權平均數的平滑因子
    sc = np.zeros(len(data))  # 初始化平滑因子序列
    ama = np.zeros(len(data))  # 初始化AMA指標序列

    er_array = abs(direction/volatility)
    for i in range(window, len(data)):

        er = er_array[i]

        sc[i] = (er * (fastsc - slowsc) + slowsc) ** 2  # 計算平滑因子
        ama[i] = (sc[i] * data[i] + (1 - sc[i]) * ama[i-1])  # 計算AMA指標

    ama_series=pd.Series(ama,index=use_index)
    return ama_series


def RSI(data, window):
    """
    計算相對強弱指數(RSI)指標
    :param data: 資料序列
    :param window: 計算RSI所需的週期
    :return: RSI指標序列
    """
    diff=data.diff()
    up_diff=pd.Series(diff[diff>0],diff.index).fillna(0)
    down_diff=abs(pd.Series(diff[diff<0],diff.index).fillna(0))

    up_rolling_mean=up_diff.ewm(com=window-1).mean()
    down_rolling_mean=down_diff.ewm(com=window-1).mean()

    RS_value=up_rolling_mean/down_rolling_mean
    RSI_value=(100 - 100/ (1 + RS_value)).round(2)

    return RSI_value


def Stoch_RSI(data, rsi_window, window):

    rsi_values = RSI(data, rsi_window)
    rsi_max = rsi_values.rolling(window).max()
    rsi_min = rsi_values.rolling(window).min()
    StochRSI = (rsi_values-rsi_min)/(rsi_max-rsi_min)*100

    return StochRSI


def KD_indicator(close, high, low, smoothK, smoothD):

    highest=high.rolling(smoothK).max()
    lowest=low.rolling(smoothK).min()
    rsv=(close-lowest)/(highest-lowest)*100

    K= rsv.rolling(smoothK).mean()
    D = K.rolling(smoothD).mean()

    return K, D


def ts_rank_jit(data:pd.DataFrame, window=10)->pd.DataFrame:
    # 育理神奇的rank算法
    #@jit(nopython=True, nogil=True,cache = True,parallel=False)#建議此方法，但不是每個終端機都可以運行
    @jit(nopython=True, nogil=True,cache = False,parallel=False)
    def ts_rank_jit(x:np.array, window:int, min_count:int, pct:bool)->np.array:
        if window == 1:window=2
        res = np.full((min_count-1, x.shape[1]),np.nan)
        n,m=np.shape(x)
        for i in range(min_count,n+1):
            if i < window:
                start = 0
            else:
                start = i-window
            
            #rank_2d_array
            ranks = np.copy(x[start:i])
            for row in range(m):
                ranks[:,row]=ranks[:,row].argsort().argsort()
            ranks = (ranks+1)[-1].reshape(1,m)
            
            #add in to res:np.array #這裡將方法直接刻死成 pct = Fasle方案，可以再降一些轉譯時間
            if pct :
                res = np.append(res,ranks/window,axis=0)
            else:
                res = np.append(res,ranks,axis=0)
        return res
    return pd.DataFrame(ts_rank_jit(x = data.values,
                                    window = window,
                                    min_count = window//2,
                                    pct = False),
                         index = data.index,
                         columns = data.columns)


def ts_mean_bn(data:pd.DataFrame, window:int=10)->pd.DataFrame:
    if window == 1:window=2
    return pd.DataFrame(bn.move_mean(data, window=window, min_count=window//2,axis=0),columns = data.columns,index = data.index)


def ts_std_bn(data:pd.DataFrame, window:int=10)->pd.DataFrame:
    return pd.DataFrame(bn.move_std(data, window=window, min_count=window//2,axis=0 , ddof = 1),columns = data.columns,index = data.index)


def ts_max_bn(data:pd.DataFrame, window:int=10)->pd.DataFrame:
    return pd.DataFrame(bn.move_max(data, window=window, min_count=window//2,axis=0),columns = data.columns,index = data.index)


def ts_min_bn(data:pd.DataFrame, window:int=10)->pd.DataFrame:
    return pd.DataFrame(bn.move_min(data, window=window, min_count=window//2,axis=0),columns = data.columns,index = data.index)


def ts_argmax_bn(data:pd.DataFrame, window:int=10)->pd.DataFrame:

    deduction = np.array([range(1,data.shape[0]+1)]).T
    deduction[deduction > window]=window

    return pd.DataFrame(deduction - bn.move_argmax(data, window=window,min_count=window//2,axis=0),columns = data.columns,index = data.index)


def ts_argmin_bn(data:pd.DataFrame, window:int=10)->pd.DataFrame:

    deduction = np.array([range(1,data.shape[0]+1)]).T
    deduction[deduction > window]=window

    return pd.DataFrame(deduction - bn.move_argmin(data, window=window,min_count=window//2,axis=0),columns = data.columns,index = data.index)


def ts_corr_np(data_1:pd.DataFrame,data_2:pd.DataFrame,window = 10)->pd.DataFrame:
    
    def corr2_coeff_rowwise2(A,B):
        with np.errstate(all="ignore"):
            A_mA = (A - A.mean(1)[:,None])
            B_mB = (B - B.mean(1)[:,None])
            ssA = (np.einsum('ij,ij->i',A_mA,A_mA))
            ssB = (np.einsum('ij,ij->i',B_mB,B_mB))
            out = np.einsum('ij,ij->i',A_mA,B_mB)/np.sqrt(ssA*ssB)
        return out
    
    data_1 = data_1 + data_2*0
    data_2 = data_1*0 + data_2
    x = data_1.values
    y = data_2.values
    min_count = window//2
    n,m=np.shape(x)
    corr_result_list = [[]]*(min_count-1)

    for index in range(min_count,n+1):
        if index < window:
            start = 0
        else:
            start = index-window
        corr_result_list.append(corr2_coeff_rowwise2(x[start:index].T,y[start:index].T))

    return pd.DataFrame(corr_result_list,index = data_1.index,columns = data_2.columns)


def ts_corr_bn(data_1:pd.DataFrame,data_2:pd.DataFrame,window = 10)->pd.DataFrame:
    
    with np.errstate(all="ignore"):
        x = np.array(data_1)
        y = np.array(data_2)
        x = x + 0 * y
        y = y + 0 * x
        min_count = window//2
        mean_x_y = bn.move_mean(x*y, window=window, min_count=min_count,axis=0)
        mean_x = bn.move_mean(x, window=window, min_count=min_count,axis=0)
        mean_y = bn.move_mean(y, window=window, min_count=min_count,axis=0)
        count_x_y = bn.move_sum((np.isnan(x+y) == 0).astype(int), window=window, min_count=window//2,axis=0)
        x_var = bn.move_var(x, window=window, min_count=min_count,axis=0 , ddof = 1)
        y_var = bn.move_var(y, window=window, min_count=min_count,axis=0 , ddof = 1)

        numerator = (mean_x_y - mean_x * mean_y) * (
            count_x_y / (count_x_y - 1)
        )
        denominator = (x_var * y_var) ** 0.5
        result = numerator / denominator

    return pd.DataFrame(result,index = data_1.index,columns = data_1.columns)


def ts_cov(data_x:pd.DataFrame, data_y:pd.DataFrame, window:int=10)->pd.DataFrame:
    return data_x.rolling(window, min_periods=window//2).cov(data_y)


def cs_rank(data):
    return data.rank(axis=1, pct=True)


def cs_zscore(data):
    return ((data.T - data.mean(axis = 1)) / data.std(axis = 1)).T


def ts_zscore_bn(data:pd.DataFrame, window:int=10)->pd.DataFrame:

    mean = bn.move_mean(data, window=window, min_count=window//2,axis=0)
    std = bn.move_std(data, window=window, min_count=window//2,axis=0 , ddof = 1)

    return pd.DataFrame((data - mean)/std , columns = data.columns,index = data.index)


def decay_linear(data:pd.DataFrame, window:int=10)->pd.DataFrame:

    if data.isnull().values.any():
        data = data.ffill()
        data = data.bfill()
        data = data.fillna(0)
    na_lwma = np.zeros_like(data)
    na_lwma[:window, :] = data.iloc[:window, :]
    na_series = data.values

    divisor = window * (window + 1) / 2
    y = (np.arange(window) + 1) * 1.0 / divisor
    for row in range(window - 1, data.shape[0]):
        x = na_series[row - window + 1: row + 1, :]
        na_lwma[row, :] = (np.dot(x.T, y))

    return pd.DataFrame(na_lwma, index=data.index, columns=data.columns)


