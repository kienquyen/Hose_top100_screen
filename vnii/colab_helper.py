_A='.vnstock'
import os,shutil
from pathlib import Path
def get_vnstock_data_dir():
	A=os.environ.get('VNSTOCK_DATA_DIR')
	if A:return Path(A).expanduser().resolve()
	return Path.home()/_A
def migrate_vnstock_data_colab(new_dir):
	A=new_dir;B=Path.home()/_A;A=Path(A).expanduser().resolve()
	if not B.exists():print(f"Không tìm thấy thư mục dữ liệu cũ: {B}");return
	os.makedirs(A,exist_ok=True)
	for C in B.iterdir():
		D=A/C.name
		if C.is_dir():shutil.copytree(C,D,dirs_exist_ok=True)
		else:shutil.copy2(C,D)
	print(f"Đã di chuyển dữ liệu từ {B} sang {A}.");print('Hãy set biến môi trường VNSTOCK_DATA_DIR trỏ đến thư mục mới để sử dụng ở các lần sau.');print(f"Ví dụ: os.environ['VNSTOCK_DATA_DIR'] = '{str(A)}'")