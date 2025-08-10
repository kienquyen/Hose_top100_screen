import os,json,time,requests,logging
from cryptography.fernet import Fernet
import base64
log=logging.getLogger(__name__)
GITHUB_TOKEN_URL='https://github.com/login/oauth/access_token'
TOKEN_EXPIRATION_BUFFER_SECONDS=604800
ENC_CLIENT_ID=b'gAAAAABobLxWSwFFS9Z4PayIKqnFi5vkILr4zXGTnREzsfZ__gHF8GhgUC4hThQeUjnB4hYN6oUkozLtTvVUOi49Eq7cqdzL160-aELa0eiMtNhMhb38NCw='
ENC_CLIENT_SECRET=b'gAAAAABobLxWt6uthQRal3qHGpKtZMNe3FFo8EjPfOKNMGoa8zi9TStC6URjC8IvIDPYQMOqhFukQCuqYmyZpAIbAw9Gc311m9SFFjX6v5frPpfR28hFjT4ZJq6i_Zf_fuiISQ25ytDG'
class TokenManager:
	def __init__(A,project_dir,target,RH,LH):B=project_dir;A.project_dir=B;A.token_path=B/'access_token.json';A.target=target;A.RH=RH;A.LH=LH;C=(str(B).split(os.path.sep)[-1]+str(B).split(os.path.sep)[-1])[::-1].ljust(32)[:32].encode('utf-8');D=base64.urlsafe_b64encode(C);A.cph=Fernet(D)
	def _check_and_refresh_token(H,repo_name=None):
		h='refresh_token_expires_in';g='expires_in';f='Không rõ nguyên nhân.';e='error_description';d='error';c='application/json';b='Accept';a='grant_type';Z='client_secret';Y='client_id';X='refresh_token_expires_at';W='access_token_expires_at';P=repo_name;I='access_token';G='refresh_token';Q=H.project_dir/'token.json';R=H.token_path
		if Q.exists():
			try:
				with open(Q,'r')as D:
					E=json.load(D);B=E.get(I)
					if B and B.strip():log.debug('Sử dụng token từ file token.json (chế độ thủ công/VPS).');return B.strip()
			except(json.JSONDecodeError,ValueError)as C:log.warning(f"File token.json bị lỗi, sẽ bỏ qua và thử với access_token.json: {C}")
		if not R.exists():
			if P is None or P=='vnstock':return
			else:raise SystemExit('Vui lòng chạy lại trình cài đặt (setup wizard) để kích hoạt bản quyền.')
		try:
			with open(R,'r+')as D:
				E=json.load(D);B=E.get(I)
				if not B or B.startswith('ghp_'):return B
				J=E.get(G);S=E.get(W);T=E.get(X)
				if not J:return B
				if not S or not T:
					try:
						log.debug('Thiếu trường expires, thử tự động refresh token bằng refresh_token...');K=H.cph.decrypt(ENC_CLIENT_ID).decode();L=H.cph.decrypt(ENC_CLIENT_SECRET).decode();M={Y:K,Z:L,a:G,G:J};N={b:c};F=requests.post(GITHUB_TOKEN_URL,data=M,headers=N);log.debug(f"Phản hồi từ GitHub (no expires): {F.status_code}");F.raise_for_status();A=F.json()
						if d in A:O=A.get(e,f);raise SystemExit(f"Lỗi bản quyền: Không thể làm mới token.\nLý do từ GitHub: {O}\nCó thể bạn đã thu hồi quyền của ứng dụng. Vui lòng chạy lại trình cài đặt.")
						E.update({I:A.get(I,B),G:A.get(G,J)});D.seek(0);D.truncate();json.dump(E,D);log.debug('Đã làm mới access_token thành công (no expires).');return E[I]
					except Exception as C:log.debug(f"Không thể tự động refresh token (no expires): {C}");return B
				U=int(time.time())
				if U>=T:raise SystemExit('Lỗi bản quyền: Phiên xác thực của bạn đã hết hạn hoàn toàn.\nVui lòng chạy lại trình cài đặt (setup wizard) để xác thực lại.')
				if U<S-TOKEN_EXPIRATION_BUFFER_SECONDS:return B
				log.debug('Thông báo từ vnii: Token xác thực sắp hết hạn, đang tự động làm mới...')
				try:
					log.debug(f"Sử dụng refresh_token để lấy access_token mới.");K=H.cph.decrypt(ENC_CLIENT_ID).decode();L=H.cph.decrypt(ENC_CLIENT_SECRET).decode();M={Y:K,Z:L,a:G,G:J};N={b:c};log.debug(f"Gửi yêu cầu đến: {GITHUB_TOKEN_URL}");F=requests.post(GITHUB_TOKEN_URL,data=M,headers=N);log.debug(f"Phản hồi từ GitHub: {F.status_code}");F.raise_for_status();A=F.json()
					if d in A:O=A.get(e,f);raise SystemExit(f"Lỗi bản quyền: Không thể làm mới token.\nLý do từ GitHub: {O}\nCó thể bạn đã thu hồi quyền của ứng dụng. Vui lòng chạy lại trình cài đặt.")
					V=int(time.time())
					if g in A:A[W]=V+int(A[g])
					if h in A:A[X]=V+int(A[h])
					log.debug('Cập nhật file access_token.json với token mới.');D.seek(0);json.dump(A,D,indent=2);D.truncate();log.debug('Thông báo từ vnii: Token đã được làm mới thành công.');return A[I]
				except Exception as C:log.debug(f"Không thể tự động refresh token: {C}");return B
		except(json.JSONDecodeError,ValueError)as C:raise SystemExit(f"Lỗi bản quyền: File xác thực (access_token.json) bị lỗi hoặc không hợp lệ. {C}\nVui lòng chạy lại trình cài đặt.")
		except requests.exceptions.RequestException as C:i=C.response.text if C.response else'Không có phản hồi.';raise SystemExit(f"Lỗi bản quyền: Yêu cầu làm mới token thất bại.\nLỗi HTTP: {str(C)}\nPhản hồi từ GitHub: {i}\nVui lòng chạy lại trình cài đặt (setup wizard) để xác thực lại.")