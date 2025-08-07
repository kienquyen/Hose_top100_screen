_K='symbol'
_J='Vui lòng nhập mã chứng khoán cần truy xuất khi khởi tạo Trading Class.'
_I='preparing'
_H='data_status'
_G='is_trading_hour'
_F='VCI.ext'
_E='records'
_D='POST'
_C=True
_B=False
_A=None
from typing import Dict,Optional,Union
from datetime import datetime
import pandas as pd
from vnai import agg_execution
from vnstock.explorer.vci.const import _TRADING_URL,_CHART_URL,_INTERVAL_MAP,_OHLC_MAP,_RESAMPLE_MAP,_OHLC_DTYPE,_INTRADAY_URL,_INTRADAY_MAP,_INTRADAY_DTYPE,_INDEX_MAPPING
from vnstock_data.explorer.vci.const import _PRICE_DEPTH_MAP
from vnstock.explorer.vci.models import TickerModel
from vnstock.core.utils.logger import get_logger
from vnstock.core.utils.market import trading_hours
from vnstock.core.utils.parser import get_asset_type
from vnstock.core.utils.user_agent import get_headers
from vnstock.core.utils.client import send_request
from vnstock_data.core.utils.transform import ohlc_to_df,intraday_to_df
logger=get_logger(__name__)
class Quote:
	def __init__(A,symbol,random_agent=_B,show_log=_C):
		B=show_log;A.symbol=symbol.upper();A.data_source='VCI';A._history=_A;A.asset_type=get_asset_type(A.symbol);A.base_url=_TRADING_URL;A.headers=get_headers(data_source=A.data_source,random_agent=random_agent);A.interval_map=_INTERVAL_MAP;A.show_log=B
		if not B:logger.setLevel('CRITICAL')
		if'INDEX'in A.symbol:A.symbol=A._index_validation()
	def _index_validation(A)->str:
		if A.symbol not in _INDEX_MAPPING.keys():raise ValueError(f"Không tìm thấy mã chứng khoán {A.symbol}. Các giá trị hợp lệ: {', '.join(_INDEX_MAPPING.keys())}")
		return _INDEX_MAPPING[A.symbol]
	def _input_validation(B,start:str,end:str,interval:str):
		A=TickerModel(symbol=B.symbol,start=start,end=end,interval=interval)
		if A.interval not in B.interval_map:raise ValueError(f"Giá trị interval không hợp lệ: {A.interval}. Vui lòng chọn: 1m, 5m, 15m, 30m, 1H, 1D, 1W, 1M")
		return A
	@agg_execution(_F)
	def history(self,start:str,end:Optional[str]=_A,interval:Optional[str]='1D',to_df:Optional[bool]=_C,show_log:Optional[bool]=_B,count_back:Optional[int]=_A,floating:Optional[int]=2)->Union[pd.DataFrame,str]:
		I='%Y-%m-%d';D=count_back;A=self;B=A._input_validation(start,end,interval);E=datetime.strptime(B.start,I)
		if end is not _A:
			F=datetime.strptime(B.end,I)+pd.Timedelta(days=1)
			if E>F:raise ValueError('Thời gian bắt đầu không thể lớn hơn thời gian kết thúc.')
			G=int(F.timestamp())
		else:G=int((datetime.now()+pd.Timedelta(days=1)).timestamp())
		J=int(E.timestamp());K=A.interval_map[B.interval];L=A.base_url+_CHART_URL;M={'timeFrame':K,'symbols':[A.symbol],'from':J,'to':G};H=send_request(url=L,headers=A.headers,method=_D,payload=M,show_log=show_log)
		if not H:raise ValueError('Không tìm thấy dữ liệu. Vui lòng kiểm tra lại mã chứng khoán hoặc thời gian truy xuất.')
		C=ohlc_to_df(data=H[0],column_map=_OHLC_MAP,dtype_map=_OHLC_DTYPE,asset_type=A.asset_type,symbol=A.symbol,source=A.data_source,interval=B.interval,floating=floating,resample_map=_RESAMPLE_MAP)
		if D is not _A:C=C.tail(D)
		if to_df:return C
		else:return C.to_json(orient=_E)
	@agg_execution(_F)
	def intraday(self,page_size:Optional[int]=100,last_time:Optional[str]=_A,to_df:Optional[bool]=_C,show_log:bool=_B)->Union[pd.DataFrame,str]:
		C=page_size;A=self;B=trading_hours(_A)
		if B[_G]is _B and B[_H]==_I:raise ValueError(f"{B['time']}: Dữ liệu khớp lệnh không thể truy cập trong thời gian chuẩn bị phiên mới. Vui lòng quay lại sau.")
		if A.symbol is _A:raise ValueError(_J)
		if C>30000:logger.warning('Bạn đang yêu cầu truy xuất quá nhiều dữ liệu, điều này có thể gây lỗi quá tải.')
		E=f"{A.base_url}{_INTRADAY_URL}/LEData/getAll";F={_K:A.symbol,'limit':C,'truncTime':last_time};G=send_request(url=E,headers=A.headers,method=_D,payload=F,show_log=show_log);D=intraday_to_df(data=G,column_map=_INTRADAY_MAP,dtype_map=_INTRADAY_DTYPE,symbol=A.symbol,asset_type=A.asset_type,source=A.data_source)
		if to_df:return D
		else:return D.to_json(orient=_E)
	@agg_execution(_F)
	def price_depth(self,to_df:Optional[bool]=_C,show_log:Optional[bool]=_B)->Union[pd.DataFrame,str]:
		B=self;C=trading_hours(_A)
		if C[_G]is _B and C[_H]==_I:raise ValueError(f"{C['time']}: Dữ liệu khớp lệnh không thể truy cập trong thời gian chuẩn bị phiên mới. Vui lòng quay lại sau.")
		if B.symbol is _A:raise ValueError(_J)
		D=f"{B.base_url}{_INTRADAY_URL}/AccumulatedPriceStepVol/getSymbolData";E={_K:B.symbol};F=send_request(url=D,headers=B.headers,method=_D,payload=E,show_log=show_log);A=pd.DataFrame(F);A=A[_PRICE_DEPTH_MAP.keys()];A.rename(columns=_PRICE_DEPTH_MAP,inplace=_C);A.source=B.data_source
		if to_df:return A
		else:return A.to_json(orient=_E)