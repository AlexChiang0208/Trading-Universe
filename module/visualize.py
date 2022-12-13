import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import gridspec
import seaborn as sns
import statsmodels.api as sm
plt.style.use("seaborn-whitegrid")


def calc_performance_index_func(percent_return_series, days_of_year=365):

    if str(percent_return_series.index.freq)!='<Day>':
        percent_return_series=percent_return_series.resample('1d').sum()

    cum_return_percent_data=percent_return_series.cumsum()

    mdd=(cum_return_percent_data.cummax()-cum_return_percent_data).max()

    return_std=(percent_return_series).std()
    return_downside_std=(percent_return_series * (percent_return_series<0)).std()
    if return_std!=0:
        sharpe_ratio=round(percent_return_series.mean()/return_std*(days_of_year**(1/2)),2)
    else:
        sharpe_ratio=None

    if return_downside_std!=0:
        sortino_ratio=round(percent_return_series.mean()/return_downside_std*(days_of_year**(1/2)),2)
    else:
        sortino_ratio=None
        
    if mdd!=0:
        rtomdd=round((cum_return_percent_data[-1])/mdd,2)
        calmar_ratio=round((rtomdd/len(percent_return_series))*days_of_year,2)
    else:
        rtomdd=None
        calmar_ratio=None

    performance_index_dict={
        "Cumulative Return":cum_return_percent_data[-1],
        "Sharpe Ratio":sharpe_ratio,
        "Sortino Ratio":sortino_ratio,
        "Calmar Ratio":calmar_ratio,
        "Return_MDD": rtomdd,
        "MDD":round(mdd,2)
    }
    return performance_index_dict


class PercentageReturnPlot:

    '''credit by Lin Jia Wei'''

    def __init__(self, percent_return_series):
        self.percent_return_series = percent_return_series

    def equity_plot(self, Name,text_position='2022-01-01',fillylim=None,ctoc=False):

        percent_return_series = self.percent_return_series
        fig = plt.figure(figsize=(16,9),constrained_layout=False)
        
        if ctoc==False:
            if str(percent_return_series.index.freq)!='<Day>':
                percent_return_series=percent_return_series.resample('1d').sum()

        performance_index_dict = calc_performance_index_func(percent_return_series)

        cum_return_percent_data=percent_return_series.cumsum()
        highest_cond=(cum_return_percent_data!=cum_return_percent_data.shift(1)) & (cum_return_percent_data==cum_return_percent_data.cummax()) & (cum_return_percent_data!=0)
        new_highest_index=list(highest_cond[highest_cond].index)

        mdd=performance_index_dict["MDD"]
        sortino_ratio=performance_index_dict["Sortino Ratio"]
        sharpe_ratio=performance_index_dict["Sharpe Ratio"]
        calmar_ratio=performance_index_dict["Calmar Ratio"]

        spec = gridspec.GridSpec(ncols=1, nrows=2,
                            height_ratios=[3, 1])

        ax0 = fig.add_subplot(spec[0])
        ax0.plot(cum_return_percent_data,label='Cumulative Return')

        ax0.scatter(new_highest_index,
            cum_return_percent_data.loc[new_highest_index], c='#02ff0f', s=50,alpha=1,edgecolor='green',label='New Equity High')

        ax0.text(pd.to_datetime(text_position),cum_return_percent_data.min(),'Return: {}%'.format((round((cum_return_percent_data[-1]),2)))+\
        '\nMDD:{0}%'.format(round(mdd,2))+\
        '\nSortino Ratio: {}'.format(sortino_ratio)+\
        '\nSharpe Ratio: {}'.format(sharpe_ratio)+\
        '\nCalmar Ratio:{}'.format(calmar_ratio),fontsize=16)

        plt.yticks(fontsize=12)
        plt.title('{} Return&MDD'.format(Name),fontsize=16)
        plt.legend(fontsize=16,loc=2)
        plt.ylabel('Return%')

        ax1 = fig.add_subplot(spec[1])
        fill_data=(-(cum_return_percent_data.cummax()-cum_return_percent_data))
        
        ax1.fill_between(x=fill_data.index,y1=fill_data,alpha=0.5,color='r',label='DD')
        ax1.plot(fill_data.index,fill_data,color='r')
        
        plt.legend(loc=3,fontsize=16)
        if fillylim!=None:
            plt.ylim(fillylim,0)
        else:
            plt.ylim(-mdd*1.1,0)
            
        plt.yticks(fontsize=12)
        plt.show();

    def Month_equity_plot(self, Name, text_position='2022-01-01',days_of_year=365):

        daily_return = self.percent_return_series

        fig,axes=plt.subplots(figsize=(16,6))
        cum_port_return=daily_return.resample('m').sum().cumsum()
        port_monthly_final_return=daily_return.resample('m').sum()
        port_weekly_final_return=daily_return.resample('w').sum()

        daily_mdd=round((daily_return.cumsum().cummax()-daily_return.cumsum()).max(),2)

        pos_return=daily_return.resample('m').sum()[daily_return.resample('m').sum()>0]
        neg_return=daily_return.resample('m').sum()[daily_return.resample('m').sum()<0]


        bar_return=pd.concat([pos_return,neg_return],axis=1,keys=['pos','neg']).fillna(0)

        bar_return=pd.DataFrame(bar_return,index=cum_port_return.index).fillna(0)

        bar_return.index=bar_return.index.strftime('%B-%Y')

        cum_port_return.index=cum_port_return.index.strftime('%B-%Y')

        ann_sharpe=(((daily_return.mean())/daily_return.std()))*(days_of_year**0.5)

        ann_sharpe=round(ann_sharpe,2)

        axes.bar(bar_return['pos'].index, height=bar_return['pos'], color='g')
        axes.bar(bar_return['neg'].index, height=bar_return['neg'], color='r')
        plt.ylabel('Return%',fontsize=16)
        plt.title(f'{Name} Month Return',fontsize=20)
        axes.plot(cum_port_return,marker='o')
        plt.xticks(rotation='vertical');

        plt.text(pd.to_datetime(text_position).strftime('%B-%Y'),cum_port_return.min()+25,
                 'Max Monthly Return: {}%'.format(bar_return.max()['pos'].round(2))+\
                '\nMax Monthly Loss:   {0}%'.format(bar_return.min()['neg'].round(2))+\
                '\n'+\
                '\nAnnualized Return:{0}%'.format(round((cum_port_return.diff(1).fillna(cum_port_return[0]).mean()*12),2))+\
                '\nAnnualized Shapre Ratio:{}'.format(ann_sharpe)
                ,fontsize=16);

    def Daily_Distribution_plot(self, Name, bins=40):

        percent_return_series = self.percent_return_series

        if str(percent_return_series.index.freq)!='<Day>':
            percent_return_series=percent_return_series.resample('1d').sum()
        fig,axes=plt.subplots(figsize=(10,8))

        kde = sm.nonparametric.KDEUnivariate(percent_return_series)
        kde.fit() # Estimate the densities

        axes.hist(percent_return_series,bins=bins,edgecolor='black',alpha=0.6,label='Daily Return Frequency');
        plt.xlabel('Return%')
        plt.ylabel('Frequency')
        plt.legend(loc=2)
        ax2 = axes.twinx()
        plt.plot(kde.support,kde.density,label='KDE(RHS)',alpha=1)
        VaR=percent_return_series.quantile(0.05)
        #var_list.append(VaR)

        min_daily_return=round(percent_return_series.min(),2)
        tail_probabily=kde.density[kde.support<VaR]
        downside_return=kde.support[kde.support<VaR]
        CVaR=percent_return_series[(percent_return_series<VaR)].mean()
        #downside_return_list.append(downside_return)
        plt.fill_between(downside_return,tail_probabily,facecolor='r',alpha=0.5,label='5% VaR')
        plt.ylim(0)
        plt.xlim((-7,7))
        plt.legend()

        # sns.kdeplot(percent_return_series,ax=ax2,label='KDE(RHS)')
        # plt.text(tail_probabily[-1],y=-0.05,s=str(round(tail_probabily[-1],2))+'%',horizontalalignment='center',
        #         verticalalignment='center',color='r')

        plt.ylabel('Probability Density')

        plt.title('{} Daily Return Hist Plot\n5%VaR={}%\n5%CVaR={}%\nmin Return={}%'.format(Name,abs(round(VaR,2)),abs(round(CVaR,2)),min_daily_return),fontsize=12)
        plt.grid()

        plt.tight_layout()


class Performance:

    def __init__(self, df_price, output_dict, time_index, fund=100, Name='Strategy'):
        self.Name = Name
        self.df_price = df_price
        self.buy = output_dict['buy']
        self.sell = output_dict['sell']
        self.sellshort = output_dict['sellshort']
        self.buytocover = output_dict['buytocover']
        self.profit_list = output_dict['profit_list']
        self.profit_fee_list = output_dict['profit_fee_list']
        self.profit_list_realized = output_dict['profit_list_realized']
        self.profit_fee_list_realized = output_dict['profit_fee_list_realized']
        self.profit_fee_list_realized_time = output_dict['profit_fee_list_realized_time']
        self.time_index = time_index
        self.equity = pd.DataFrame({'profit':np.cumsum(self.profit_list), 'profitfee':np.cumsum(self.profit_fee_list)}, index=time_index)
        self.equity_realized = pd.DataFrame({'profit': np.cumsum(self.profit_list_realized), 'profitfee': np.cumsum(self.profit_fee_list_realized)}, index=df_price.index[self.profit_fee_list_realized_time])
        self.equity['equity'] = self.equity['profitfee'] + fund
        self.return_series = (self.equity['equity'] / self.equity['equity'][0]) * 100
        self.percent_return_series = self.return_series - self.return_series.shift(1)
        self.equity['drawdown'] = self.equity['equity'] - self.equity['equity'].cummax()
        self.L_tradePeriod = [output_dict['sell'][num]-output_dict['buy'][num] for num in range(len(output_dict['sell']))]
        self.S_tradePeriod = [output_dict['buytocover'][num]-output_dict['sellshort'][num] for num in range(len(output_dict['buytocover']))]
        self.tradePeriod = self.L_tradePeriod + self.S_tradePeriod
        self.JiaWeiPlot = PercentageReturnPlot(self.percent_return_series)

    def draw_unrealized_profit(self):
        self.equity[['profit', 'profitfee']].plot(grid=True, figsize=(12, 5), title='Profit and Loss')
        plt.show();

    def draw_realized_profit(self):
        self.equity_realized[['profit', 'profitfee']].plot(grid=True, figsize=(12, 5), title='Profit and Loss (Realized)')
        plt.show();

    def draw_equity_curve(self, text_position='2022-01-01', fillylim=None, ctoc=False):
        return self.JiaWeiPlot.equity_plot(Name=self.Name, text_position=text_position, fillylim=fillylim, ctoc=ctoc)

    def draw_monthly_equity(self, text_position='2022-01-01',days_of_year=365):
        return self.JiaWeiPlot.Month_equity_plot(Name=self.Name, text_position=text_position,days_of_year=days_of_year)

    def draw_daily_distribution(self, bins=40):
        return self.JiaWeiPlot.Daily_Distribution_plot(Name=self.Name, bins=bins)

    def draw_hold_position(self):

        fig, ax = plt.subplots(figsize = (16,6))

        self.df_price.plot(label = 'Price', ax = ax, c = 'gray', grid=True, alpha=0.8)
        plt.scatter(self.df_price.iloc[self.buy].index, self.df_price.iloc[self.buy],c = 'orangered', label = 'Buy', marker='^', s=40)
        plt.scatter(self.df_price.iloc[self.sell].index, self.df_price.iloc[self.sell],c = 'orangered', label = 'Sell', marker='v', s=40)
        plt.scatter(self.df_price.iloc[self.sellshort].index, self.df_price.iloc[self.sellshort],c = 'limegreen', label = 'Sellshort', marker='v', s=40)
        plt.scatter(self.df_price.iloc[self.buytocover].index, self.df_price.iloc[self.buytocover],c = 'limegreen', label = 'Buytocover', marker='^', s=40)

        plt.legend()
        plt.ylabel('USD')
        plt.xlabel('Time')
        plt.title('Price Movement',fontsize  = 16)
        plt.show();

    def show_performance(self, days_of_year=365):

        performance_index_dict = calc_performance_index_func(self.percent_return_series, days_of_year)

        tradeTimes = len(self.tradePeriod)
        max_tradePeriod = max(self.tradePeriod)
        min_tradePeriod = min(self.tradePeriod)
        mean_tradePeriod = np.round(np.mean(self.tradePeriod),2)

        if len(self.profit_fee_list_realized) != 0:
            winRate = len([i for i in self.profit_fee_list_realized if i > 0]) / len(self.profit_fee_list_realized)
            winRate = np.round(winRate*100,2)
        else:
            winRate = np.nan
        if abs(sum([i for i in self.profit_fee_list_realized if i < 0])) != 0:
            profitFactor = sum([i for i in self.profit_fee_list_realized if i > 0]) / abs(sum([i for i in self.profit_fee_list_realized if i < 0]))
            profitFactor = np.round(profitFactor,2)
        else:
            profitFactor = np.nan
        if abs(np.mean([i for i in self.profit_fee_list_realized if i < 0])) != 0:
            winLossRatio = np.mean([i for i in self.profit_fee_list_realized if i > 0]) / abs(np.mean([i for i in self.profit_fee_list_realized if i < 0]))
            winLossRatio = np.round(winLossRatio,2)
        else:
            winLossRatio = np.nan

        print(f'Cumulative Return: {np.round(performance_index_dict["Cumulative Return"],2)}%')
        print(f'Sharpe Ratio: {performance_index_dict["Sharpe Ratio"]}')
        print(f'Sortino Ratio: {performance_index_dict["Sortino Ratio"]}')
        print(f'Calmar Ratio: {performance_index_dict["Calmar Ratio"]}')
        print(f'Return / MDD: {performance_index_dict["Return_MDD"]}')
        print(f'MDD: {performance_index_dict["MDD"]}%')
        print(f'tradeTimes: {tradeTimes}')
        print(f'maxTradePeriod: {max_tradePeriod}')
        print(f'minTradePeriod: {min_tradePeriod}')
        print(f'meanTradePeriod: {mean_tradePeriod}')
        print(f'winRate: {winRate}%')
        print(f'profitFactor: {profitFactor}')
        print(f'winLossRatio: {winLossRatio}')

        return


