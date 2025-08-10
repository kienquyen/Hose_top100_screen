_A='utf-8'
import json
from vnstock import*
import requests,logging
from cryptography.fernet import Fernet
import base64,os,importlib.metadata
log=logging.getLogger(__name__)
GITHUB_TOKEN_URL='https://github.com/login/oauth/access_token'
TOKEN_EXPIRATION_BUFFER_SECONDS=604800
class Analytics:
	def __init__(self,project_dir,id_dir,target,RH,LH):from pathlib import Path;self.project_dir=Path(project_dir);self.id_dir=Path(id_dir);self.target=target;self.RH=RH;self.LH=LH;self.env_config=self.id_dir/'env.json';kb=(str(project_dir).split(os.path.sep)[-1]+str(id_dir).split(os.path.sep)[-1])[::-1].ljust(32)[:32].encode(_A);kb64=base64.urlsafe_b64encode(kb);self.cph=Fernet(kb64)
	def system_info(self):A='mock';return{'cpu':A,'ram':A}
	def log_analytics_data(self,license_info):
		HARDWARE=self.system_info();from.constants import AUKY;ECRU='gAAAAABocpJI0diAlnWkgTP_3e1kxw2MkKK8MUgocXbJ6duKhtFEGd98pwLe3_JMjamhS2yyc-5wZ2xcUz79DqxsPcu5B3Uh6h6WqNJ5I6RlxVMBCQwIh_qOwD832yXzN5Uw_JcAOLU_';url=self.cph.decrypt(ECRU.encode()).decode(_A);api_key=self.cph.decrypt(AUKY).decode(_A);payload=json.dumps({'segment':'paid','analytics_data':{'license_info':license_info},'metadata':{'system_info':HARDWARE,'packages_installed':self.packages_installed()}});headers={'x-api-key':api_key,'Content-Type':'application/json'}
		with open(self.env_config,'w',encoding=_A)as f:f.write(payload)
		try:response=requests.request('POST',url,headers=headers,data=payload)
		except Exception:raise SystemExit('Vui lòng kiểm tra kết nối mạng và thử lại sau hoặc liên hệ Vnstock để được hỗ trợ.')
	def packages_installed(self):
		B='financetoolkit';A='backtesting';package_mapping={'vnstock_family':['vnstock','vnstock_ta','vnstock_data','vnstock_news','vnstock_pipeline','vnstock_ezchart','vnai','vnii'],'analytics':['openbb','pandas_ta'],'static_charts':['matplotlib','seaborn','altair'],'dashboard':['streamlit','voila','panel','shiny','dash'],'interactive_charts':['mplfinance','plotly','plotline','bokeh','pyecharts','highcharts-core','highcharts-stock','mplchart'],'datafeed':['yfinance','alpha_vantage','pandas-datareader','investpy'],'official_api':['ssi-fc-data','ssi-fctrading','fiinquantx','xnoapi'],'risk_return':['pyfolio','empyrical','quantstats',B],'machine_learning':['scipy','sklearn','statsmodels','pytorch','tensorflow','keras','xgboost'],'indicators':['stochastic','talib','tqdm','finta',B,'tulipindicators'],A:['vectorbt',A,'bt','zipline','pyalgotrade','backtrader','pybacktest','fastquant','lean','ta','finmarketpy','qstrader'],'server':['fastapi','flask','uvicorn','gunicorn'],'framework':['lightgbm','catboost','django']};installed_packages={}
		for(category,packages)in package_mapping.items():
			installed_packages[category]=[]
			for pkg in packages:
				try:version=importlib.metadata.version(pkg);installed_packages[category].append((pkg,version))
				except importlib.metadata.PackageNotFoundError:pass
		return installed_packages