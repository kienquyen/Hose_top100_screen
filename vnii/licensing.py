_A=None
import requests,logging,sys,json
from pathlib import Path
log=logging.getLogger(__name__)
class LicenseManager:
	def __init__(A,project_dir,repo_owner,repo_name=_A):B=project_dir;A.project_dir=B;A.repo_owner=repo_owner;A.repo_name=repo_name;A.id=B/'user.json'
	def licensing_id(A,access_token):
		M='user';L='N/A';K='Unknown';N={'Authorization':f"token {access_token}",'Accept':'application/vnd.github.v3+json'}
		try:
			F=K;G='License check failed.';H=False;C=L;B=_A
			if A.repo_name:E=[A.repo_name]
			else:E=['diamond_sponsorship','golden_sponsorship','silver_sponsorship','bronze_sponsorship']
			log.debug(f"Bắt đầu kiểm tra quyền truy cập cho các repo: {E}")
			for D in E:
				I=f"https://api.github.com/repos/{A.repo_owner}/{D}";log.debug(f"Đang kiểm tra repo: {D} tại URL: {I}");B=requests.get(I,headers=N);log.debug(f"Phản hồi cho repo '{D}': {B.status_code}")
				if B.status_code==200:H=True;C=D;log.debug(f"Đã cấp quyền truy cập cho repo: {C}");break
			if H:
				G=f"License recognized and verified for: {C}. "
				if A.id.exists():
					with open(A.id,'r')as O:F=json.load(O).get(M,K)
			else:
				P=B.status_code if B is not _A else L;Q=f" (khi kiểm tra repo '{A.repo_name}')"if A.repo_name else'';R=A.project_dir/'token.json'
				if R.exists():J='Vui lòng cập nhật file token.json của bạn với một Personal Access Token (PAT) mới.'
				else:J='Vui lòng chạy lại trình cài đặt (setup wizard) để gia hạn quyền truy cập.'
				if A.repo_name is _A or A.repo_name=='vnstock':return
				else:raise SystemExit(f"Lỗi bản quyền (HTTP {P}):\nToken của bạn không hợp lệ, đã hết hạn, hoặc bạn không có quyền truy cập vào repository mục tiêu{Q}.\n{J}")
		except requests.exceptions.RequestException as S:raise SystemExit(f"Lỗi kết nối mạng khi kiểm tra bản quyền: {S}\nVui lòng kiểm tra kết nối và thử lại.")
		T={'status':G,M:F,'verified_repo':C};return T