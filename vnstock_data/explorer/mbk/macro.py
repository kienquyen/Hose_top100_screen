_M='exchange_rate'
_L='last_updated'
_K='quarter'
_J='day'
_I=True
_H='2025-04'
_G='2015-01'
_F='report_time'
_E='MBK'
_D='year'
_C=False
_B='month'
_A='group_name'
import pandas as pd
from datetime import datetime,date
from vnai import agg_execution
from vnstock.core.utils.parser import camel_to_snake
from vnstock.core.utils.transform import reorder_cols
from vnstock_data.core.utils.client import send_request
from vnstock_data.core.utils.user_agent import get_headers
from vnstock_data.explorer.mbk.const import _BASE_URL,MACRO_DATA,REPORT_PERIOD,TYPE_ID
def process_report_dates(df,last_updated_col,keep_label=_I):
	M='9 tháng';L='6 tháng';K='%Y-%m-%d';A=df;H=[];I=[]
	for(N,E)in zip(A.index,A[last_updated_col]):
		if isinstance(E,date):J=E
		else:J=datetime.strptime(E,K).date()
		C,B=N.split('/');B=int(B)
		if'Quý'in C:
			F=int(C.split(' ')[1]);O=F*3;D=date(B,O,1)
			if F==4 and J.year>B:D=date(B,12,31)
			G=f"Quý {F}"
		elif L in C:D=date(B,6,30);G=L
		elif M in C:D=date(B,9,30);G=M
		else:raise ValueError(f"Unrecognized report type: {C}")
		H.append(D.strftime(K));I.append(G)
	A=A.copy()
	if keep_label:A['label']=A.index
	A.index=H;A['report_type']=I;return A
class Macro:
	def __init__(A,random_agent:bool=_C,show_log:bool=_C):A.data_source=_E;A.headers=get_headers(data_source=A.data_source,random_agent=random_agent);A.headers['content-type']='application/x-www-form-urlencoded; charset=UTF-8';A.show_log=show_log
	def _fetch_macro_data(L,indicator:str,start:str,end:str,period:str=_K)->pd.DataFrame:
		Q='Tháng ';I=period;H=end;G=start;F=indicator;E='-';B='';R=f"{_BASE_URL}{MACRO_DATA}";M=REPORT_PERIOD.get(I)
		if M is None:raise ValueError(f"Unsupported report period type: {I}")
		if F==_M:
			C=G.split(E);D=H.split(E)
			if len(C)!=3 or len(D)!=3:raise ValueError("For exchange_rate, the date format must be 'YYYY-mm-dd'")
			N=C[0];O=D[0];J=G;K=H
		else:
			C=G.split(E)
			if len(C)!=2:raise ValueError("Start date format must be 'YYYY-mm'")
			N,J=C;D=H.split(E)
			if len(D)!=2:raise ValueError("End date format must be 'YYYY-mm'")
			O,K=D
			if I!=_K:J='0';K='0'
		P=TYPE_ID.get(F)
		if P is None:raise ValueError(f"{F} report type code is not defined in TYPE_ID mapping")
		S=f"type={M}&fromYear={N}&toYear={O}&from={J}&to={K}&normTypeID={P}";T=send_request(url=R,headers=L.headers,method='POST',payload=S,show_log=L.show_log);A=pd.DataFrame(T);A.columns=[camel_to_snake(A)for A in A.columns];A.columns=A.columns.str.replace('tern_',B,regex=_C).str.replace('norm_',B,regex=_C).str.replace('term_',B,regex=_C).str.replace('from_',B,regex=_C).str.replace('_code',B,regex=_C);U=pd.to_numeric(A[_J].str.replace('/Date(',B,regex=_C).str.replace(')/',B,regex=_C));A[_J]=pd.to_datetime(U,unit='ms').dt.date;V=['report_data_id','id',_D,'group_id','css_style','type_id'];A=A.drop(columns=V,errors='ignore');A=reorder_cols(A,cols=['unit','source'],position='last');A=reorder_cols(A,cols=[_F],position='first')
		if A[_F].str.contains(Q).any():A[_F]=A[_F].str.replace(Q,B,regex=_C);A[_F]=A[_F].apply(lambda x:pd.Period(x,freq='M').end_time.date()if isinstance(x,str)else x)
		A.set_index(_F,inplace=_I);A=A.sort_index(ascending=_I);A.rename(columns={_J:_L},inplace=_I);return A
	@agg_execution(_E)
	def gdp(self,start:str=_G,end:str=_H,period:str=_K,keep_label:bool=_C)->pd.DataFrame:
		B=period
		if B not in[_K,_D]:raise ValueError(f"Unsupported report period type: {B}")
		A=self._fetch_macro_data('gdp',start,end,B);A=process_report_dates(A,last_updated_col=_L,keep_label=keep_label);A.index.name=_F;A=A.sort_values([_L,_A,'name']);return A
	@agg_execution(_E)
	def cpi(self,start:str=_G,end:str=_H,period:str=_B)->pd.DataFrame:
		B=period
		if B not in[_B,_D]:raise ValueError(f"Unsupported report period type: {B}")
		A=self._fetch_macro_data('cpi',start,end,B)
		if _A in A.columns:A=A.drop(columns=[_A])
		return A
	@agg_execution(_E)
	def industry_prod(self,start:str=_G,end:str=_H,period:str=_B)->pd.DataFrame:
		A=period
		if A not in[_B,_D]:raise ValueError(f"Unsupported report period type: {A}")
		return self._fetch_macro_data('industrial_production',start,end,A)
	@agg_execution(_E)
	def import_export(self,start:str=_G,end:str=_H,period:str=_B)->pd.DataFrame:
		B=period
		if B not in[_B,_D]:raise ValueError(f"Unsupported report period type: {B}")
		A=self._fetch_macro_data('export_import',start,end,B)
		if _A in A.columns:A=A.drop(columns=[_A])
		return A
	@agg_execution(_E)
	def retail(self,start:str=_G,end:str=_H,period:str=_B)->pd.DataFrame:
		B=period
		if B not in[_B,_D]:raise ValueError(f"Unsupported report period type: {B}")
		A=self._fetch_macro_data('retail',start,end,B)
		if _A in A.columns:A=A.drop(columns=[_A])
		return A
	@agg_execution(_E)
	def fdi(self,start:str=_G,end:str=_H,period:str=_B)->pd.DataFrame:
		A=period
		if A not in[_B,_D]:raise ValueError(f"Unsupported report period type: {A}")
		return self._fetch_macro_data('fdi',start,end,A)
	@agg_execution(_E)
	def money_supply(self,start:str=_G,end:str=_H,period:str=_B)->pd.DataFrame:
		B=period
		if B not in[_B,_D]:raise ValueError(f"Unsupported report period type: {B}")
		A=self._fetch_macro_data('money_supply',start,end,B)
		if _A in A.columns:A=A.drop(columns=[_A])
		return A
	@agg_execution(_E)
	def exchange_rate(self,start:str='2025-01-02',end:str='2025-04-10',period:str=_J)->pd.DataFrame:
		B=period
		if B not in[_J,_D]:raise ValueError(f"Unsupported report period type: {B}")
		A=self._fetch_macro_data(_M,start,end,B)
		if _A in A.columns:A=A.drop(columns=[_A])
		A.index=pd.to_datetime(A.index,dayfirst=_I);return A
	@agg_execution(_E)
	def population_labor(self,start:str=_G,end:str=_H,period:str=_D)->pd.DataFrame:
		B=period
		if B not in[_B,_D]:raise ValueError(f"Unsupported report period type: {B}")
		A=self._fetch_macro_data('population_labor',start,end,B)
		if _A in A.columns:A=A.drop(columns=[_A])
		return A