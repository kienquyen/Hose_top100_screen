_D='last_trigger'
_C=b'secret'
_B='ads'
_A=None
import re,sys
from pathlib import Path
from datetime import datetime,timedelta,timezone
from.crypto import CryptoManager
from.licensing import LicenseManager
class AdCategory:FREE=0;MANDATORY=1;ANNOUNCEMENT=2;REFERRAL=3;FEATURE=4;GUIDE=5;SURVEY=6;PROMOTION=7;SECURITY=8;MAINTENANCE=9;WARNING=10
class AdDefinition:
	def __init__(A,name:str,freq_seconds:float,category:int):A.name=name;A.freq=timedelta(seconds=freq_seconds);A.category=category
from.colab_helper import get_vnstock_data_dir
class AdHistoryStore(CryptoManager):
	def __init__(A,project_dir=_A,secret=_C):
		B=project_dir
		if B is _A:B=get_vnstock_data_dir()
		A.log_file=B/'ads_log.json';super().__init__(B,secret)
		if not A.log_file.exists():A.log_file.parent.mkdir(exist_ok=True);A.log_file.write_text(A.encrypt_json({_B:{}}))
	def _load(A):return A.decrypt_json(A.log_file.read_text())
	def _save(A,data):A.log_file.write_text(A.encrypt_json(data))
	def get_last(C,name:str)->datetime:
		D=C._load().get(_B,{});B=D.get(name,{}).get(_D)
		if B:
			A=datetime.fromisoformat(B)
			if A.tzinfo is _A:A=A.replace(tzinfo=timezone.utc)
			return A
	def log_show(A,name:str,timestamp:datetime):D='total_count';B=A._load();C=B.setdefault(_B,{}).setdefault(name,{D:0});C[D]+=1;C[_D]=timestamp.isoformat();A._save(B)
	def log_skip(A,name:str,reason:str):0
class AdScheduler:
	def __init__(B,project_dir=_A,secret:bytes=_C):
		A=project_dir;from.colab_helper import get_vnstock_data_dir as C
		if A is _A:A=C()
		B.history=AdHistoryStore(project_dir=A,secret=secret);B.license=LicenseManager(project_dir=A,repo_owner=_A)
	def should_show(A,ad:AdDefinition)->bool:
		B=False
		if ad.category==AdCategory.FREE and A.license.is_sponsor():A.history.log_skip(ad.name,'sponsor');return B
		C=A.history.get_last(ad.name)
		if C and datetime.now(timezone.utc)-C<ad.freq:return B
		if'google.colab'in sys.modules and not A.license.is_authenticated_google():return B
		return True
def parse_meta_frequency(html:str)->float:
	C=re.search('<meta[^>]*name=["\\\']ad-freq["\\\'][^>]*content=["\\\']([^"\\\']+)["\\\']',html)
	if not C:return .0
	D=C.group(1).strip().lower();A,B=re.match('(\\d+(?:\\.\\d+)?)/(\\w+)',D).groups();A=float(A)
	if B=='d':return A*86400
	if B=='wk':return A*604800
	if B=='m':return A*2592000
	return A