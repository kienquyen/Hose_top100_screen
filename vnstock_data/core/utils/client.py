_A=None
import requests,json
from typing import Dict,Any,Optional,Union
from vnstock.core.utils.logger import get_logger
logger=get_logger(__name__)
def send_request(url:str,headers:Dict[str,str],method:str='GET',params:Optional[Dict]=_A,payload:Optional[Union[Dict,str]]=_A,show_log:bool=False,timeout:int=30)->Dict[str,Any]:
	I=timeout;H=show_log;G=method;F=headers;D=params;C=url;A=payload
	if H:
		logger.info(f"{G.upper()} request to {C}")
		if D:logger.info(f"Params: {D}")
		if A:logger.info(f"Payload: {A}")
	try:
		if G.upper()=='GET':B=requests.get(C,headers=F,params=D,timeout=I)
		else:
			if A is not _A:
				if isinstance(A,dict):E=json.dumps(A)
				elif isinstance(A,str):E=A
				else:raise ValueError('Payload must be either a dictionary or a raw string.')
			else:E=_A
			B=requests.post(C,headers=F,data=E,timeout=I)
		if B.status_code!=200:raise ConnectionError(f"Failed to fetch data: {B.status_code} - {B.reason}")
		J=B.json()
		if H:logger.info(f"Response data: {J}");logger.info(f"Response status: {B.status_code}")
		return J
	except requests.exceptions.RequestException as L:K=f"API request failed: {str(L)}";logger.error(K);raise ConnectionError(K)