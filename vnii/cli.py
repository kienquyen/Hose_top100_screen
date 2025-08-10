_A=None
import sys,logging
from.core import VnstockInitializer
from.constants import AUKY
log=logging.getLogger(__name__)
def lc_init(repo_owner='vnstock-hq',repo_name=_A,debug=False):
	F='free user';E='status';D='vnstock';A=repo_name
	if not log.handlers:G=logging.StreamHandler(sys.stdout);J=logging.Formatter('%(message)s');G.setFormatter(J);log.addHandler(G)
	if debug:log.setLevel(logging.DEBUG);log.debug('vnii: Chế độ debug được kích hoạt.')
	else:log.setLevel(logging.INFO)
	B=VnstockInitializer(AUKY,repo_owner=repo_owner,repo_name=A);H=B._check_and_refresh_token()
	if not H:
		if A is _A or A==D:log.debug('[COMMUNITY] Không tìm thấy file xác thực, bạn đang dùng phiên bản cộng đồng.');return{E:F}
		else:raise SystemExit('Lỗi bản quyền: Không thể lấy được access token từ file xác thực.\nVui lòng chạy lại trình cài đặt (setup wizard).')
	try:I=B.licensing_id(H)
	except SystemExit as C:
		if A is _A or A==D:log.debug(f"[COMMUNITY] Không xác thực được license: {C}");return{E:F}
		else:raise
	except Exception as C:
		if A is _A or A==D:log.debug(f"[COMMUNITY] Lỗi không xác định khi kiểm tra license: {C}");return{E:F}
		else:raise
	B.log_analytics_data(I);return I