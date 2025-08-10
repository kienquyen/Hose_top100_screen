import time,os
from pathlib import Path
from datetime import datetime
import pandas as pd
from vnstock import Vnstock
from vnstock_data.explorer.vci import Quote
from vnstock_pipeline.template.vnstock import VNFetcher,VNValidator,VNTransformer
from vnstock_pipeline.utils.deduplication import drop_duplicates
from vnstock_pipeline.utils.market_hours import trading_hours
class IntradayFetcher(VNFetcher):
	def _vn_call(E,ticker:str,**A)->pd.DataFrame:B=A.get('page_size',50000);C=Quote(symbol=ticker);D=C.intraday(page_size=B);return D
class IntradayValidator(VNValidator):required_columns=['time','price','volume','match_type','id']
class IntradayTransformer(VNTransformer):
	def transform(B,data:pd.DataFrame)->pd.DataFrame:A=super().transform(data);A=drop_duplicates(A,subset=['time','id']);return A
def run_intraday_task(tickers:list,interval:int=60,mode:str='live'):
	I='./data/intraday';C=tickers;from vnstock_pipeline.core.scheduler import Scheduler as D;from vnstock_pipeline.core.exporter import CSVExport as E;F=IntradayFetcher();G=IntradayValidator();H=IntradayTransformer()
	if mode.lower()=='eod':print('Chế độ EOD: Lấy dữ liệu intraday tĩnh một lần.');A=E(base_path=I);B=D(F,G,H,A);B.run(C);print('EOD download hoàn thành.')
	else:
		print('Chế độ live: Cập nhật dữ liệu intraday liên tục trong phiên giao dịch.');A=E(base_path=I);B=D(F,G,H,A)
		while True:
			try:
				J=trading_hours(market='HOSE',enable_log=True,language='en')
				if not J['is_trading_hour']:print('Ngoài giờ giao dịch. Dừng vòng lặp.');break
				B.run(C)
			except Exception as K:print(f"Error updating intraday data: {K}")
			time.sleep(interval)
if __name__=='__main__':sample_tickers=['ACB','VCB','HPG'];run_intraday_task(sample_tickers,interval=60,mode='live')