_S='organ_code'
_R='%Y-%m-%d'
_Q='time_frame'
_P='coerce'
_O='content'
_N='foreign'
_M='toDate'
_L='fromDate'
_K='ONE_DAY'
_J='timeFrame'
_I='size'
_H='page'
_G='ticker'
_F=True
_E='VCI.ext'
_D='data'
_C='trading_date'
_B=False
_A=None
from typing import List,Optional,Union
import pandas as pd,requests,json
from vnstock.core.utils.logger import get_logger
from vnstock.core.utils.user_agent import get_headers
from vnstock.core.utils.parser import get_asset_type,camel_to_snake,flatten_data
from vnstock_data.core.utils.parser import filter_columns_by_language
from vnstock.explorer.vci.const import _TRADING_URL
from vnstock_data.explorer.vci.const import _VCIQ_URL,_REPORT_RESOLUTION
from vnstock_data.core.utils.validation import validate_date
from vnstock.core.utils.transform import flatten_hierarchical_index
from vnai import agg_execution
logger=get_logger(__name__)
class Trading:
	def __init__(A,symbol:Optional[str],random_agent=_B,show_log:Optional[bool]=_B):
		B=show_log;A.symbol=symbol.upper();A.asset_type=get_asset_type(A.symbol);A.base_url=_VCIQ_URL;A.headers=get_headers(data_source='VCI',random_agent=random_agent)
		if not B:logger.setLevel('CRITICAL')
		A.show_log=B
	def _process_dates(C,start:Optional[str],end:Optional[str])->tuple[Optional[str],Optional[str]]:
		B=end;A=start
		if A and B:
			if not validate_date(A)or not validate_date(B):logger.error('Invalid date format. Please use the format YYYY-mm-dd.');return _A,_A
			else:return A.replace('-',''),B.replace('-','')
		return _A,_A
	def _fetch_data(A,endpoint:str,params:dict)->dict:
		B=endpoint;E=f"{A.base_url}/v1/company/{A.symbol}/{B}"
		try:
			D=requests.get(E,headers=A.headers,params=params);D.raise_for_status();F=D.json()
			if A.show_log:logger.info(f"Successfully fetched data from {B} for {A.symbol}")
			return F
		except requests.exceptions.RequestException as C:logger.error(f"Failed to fetch data from {B} for {A.symbol}: {C}");raise
		except ValueError as C:logger.error(f"Failed to parse JSON response from {B}: {C}");raise
	def _to_dataframe(D,data:dict,data_path:Optional[list]=_A)->pd.DataFrame:
		B=data_path
		try:
			if B is _A:B=[_D]
			A=data
			for E in B:
				if isinstance(A,dict)and E in A:A=A[E]
				else:logger.warning(f"Data path {B} not found in response for {D.symbol}");return pd.DataFrame()
			if not A:logger.warning(f"No data found at path {B} for {D.symbol}");return pd.DataFrame()
			if isinstance(A,list):C=pd.DataFrame(A)
			elif isinstance(A,dict):C=pd.DataFrame([A])
			else:logger.error(f"Unexpected data type at path {B}: {type(A)}");return pd.DataFrame()
			if not C.empty:C.columns=[camel_to_snake(A)for A in C.columns]
			return C
		except(KeyError,TypeError,Exception)as F:logger.error(f"Unexpected error processing data for {D.symbol}: {F}");raise
	@agg_execution(_E)
	def price_board(self,symbols_list:List[str],to_df:Optional[bool]=_F,show_log:Optional[bool]=_B,flatten_columns:Optional[bool]=_B,separator:Optional[str]='_',drop_levels:Optional[Union[int,List[int]]]=_A):
		W='time';V='session';U='symbol';T='volume';S='price';L='message_type';K='received_time';J='code';I='bidAsk';D='match';C='bid_ask';A='listing';M=f"{_TRADING_URL}price/symbols/getList";N=json.dumps({'symbols':symbols_list})
		if show_log:logger.info(f"Requested URL: {M} with query payload: {N}")
		H=requests.post(M,headers=self.headers,data=N)
		if H.status_code!=200:raise ConnectionError(f"Tải dữ liệu không thành công: {H.status_code} - {H.reason}")
		O=H.json();P=[]
		for E in O:
			X={A:E['listingInfo'],I:E[I],D:E['matchPrice']};F=flatten_data(X)
			try:
				for(G,Q)in enumerate(E[I]['bidPrices'],start=1):F[f"bidAsk_bid_{G}_price"]=Q[S];F[f"bidAsk_bid_{G}_volume"]=Q[T]
				for(G,R)in enumerate(E[I]['askPrices'],start=1):F[f"bidAsk_ask_{G}_price"]=R[S];F[f"bidAsk_ask_{G}_volume"]=R[T]
			except:pass
			P.append(F)
		B=pd.DataFrame(P);B.columns=pd.MultiIndex.from_tuples([tuple(camel_to_snake(A)for A in A.split('_',1))for A in B.columns]);Y=[(C,J),(C,U),(C,V),(C,K),(C,L),(C,W),(C,'bid_prices'),(C,'ask_prices'),(A,J),(A,'exercise_price'),(A,'exercise_ratio'),(A,'maturity_date'),(A,'underlying_symbol'),(A,'issuer_name'),(A,K),(A,L),(A,'en_organ_name'),(A,'en_organ_short_name'),(A,'organ_short_name'),(A,_G),(D,J),(D,U),(D,K),(D,L),(D,W),(D,V)];B=B.drop(columns=[A for A in Y if A in B.columns]);B=B.rename(columns={'board':'exchange'},level=1)
		if flatten_columns:B=flatten_hierarchical_index(B,separator=separator,drop_levels=drop_levels,handle_duplicates=_F)
		B.attrs['source']='VCI'
		if to_df:return B
		else:return O
	@agg_execution(_E)
	def summary(self,resolution:str='1D',start:Optional[str]=_A,end:Optional[str]=_A,limit:Optional[int]=100):
		B=self;C,D=B._process_dates(start,end);E={_J:_REPORT_RESOLUTION.get(resolution,_K),_H:0,_I:limit}
		if C and D:E.update({_L:C,_M:D})
		F=B._fetch_data('price-history-summary',E);A=B._to_dataframe(F,[_D])
		if not A.empty and any(_N in A for A in A.columns):A.columns=A.columns.str.replace(_N,'fr',regex=_B)
		return A
	@agg_execution(_E)
	def price_history(self,resolution:str='1D',start:Optional[str]=_A,end:Optional[str]=_A,limit:Optional[int]=100):
		B=self;C,D=B._process_dates(start,end);E={_J:_REPORT_RESOLUTION.get(resolution,_K),_H:0,_I:limit}
		if C and D:E.update({_L:C,_M:D})
		F=B._fetch_data('price-history',E);A=B._to_dataframe(F,[_D,_O]);A.columns=A.columns.str.replace(_N,'fr',regex=_B);G=['id',_G,'stock_type',_Q];H={'open_price':'open','close_price':'close','highest_price':'high','lowest_price':'low','total_match_volume':'matched_volume','total_match_value':'matched_value','total_deal_volume':'deal_volume','total_deal_value':'deal_value'};A=A.drop(columns=[B for B in G if B in A.columns])
		if _C in A.columns:A[_C]=pd.to_datetime(A[_C],format=_R,errors=_P)
		A=A.rename(columns={B:C for(B,C)in H.items()if B in A.columns});return A
	@agg_execution(_E)
	def prop_trade(self,resolution:str='1D',start:Optional[str]=_A,end:Optional[str]=_A,limit:Optional[int]=100):
		B=self;C,D=B._process_dates(start,end);E={_J:_REPORT_RESOLUTION.get(resolution,_K),_H:0,_I:limit}
		if C and D:E.update({_L:C,_M:D})
		F=B._fetch_data('proprietary-history',E);A=B._to_dataframe(F,[_D,_O]);A.columns=A.columns.str.replace('proprietary','prop',regex=_B);G=['id',_G,_S,_Q];A=A.drop(columns=[B for B in G if B in A.columns])
		if _C in A.columns:
			try:A[_C]=pd.to_datetime(A[_C],format=_R,errors=_P)
			except Exception as H:logger.warning(f"Failed to convert trading_date to datetime: {H}")
		A=A.dropna(how='all');A=A.reset_index(drop=_F);return A
	@agg_execution(_E)
	def insider_deal(self,limit:Optional[int]=100,lang:str='vi'):
		C={_H:0,_I:limit};D=self._fetch_data('insider-transaction',C);A=self._to_dataframe(D,[_D,_O]);A=filter_columns_by_language(A,lang=lang);E=['id',_G,_S,'display_date1','display_date2','event_code','action_type_code','icb_code_lv1'];A=A.drop(columns=[B for B in E if B in A.columns]);F=['start_date','end_date','public_date']
		for B in F:
			if B in A.columns:
				try:A[B]=pd.to_datetime(A[B],errors=_P)
				except Exception as G:logger.warning(f"Failed to convert {B} to datetime: {G}")
		A=A.dropna(how='all');A=A.reset_index(drop=_F);return A