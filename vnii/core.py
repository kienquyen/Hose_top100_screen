import os,pathlib,uuid,logging
from pathlib import Path
from vnstock import*
from.crypto import generate_key,create_fernet_cipher
from.analytics import Analytics
from.auth import TokenManager
from.licensing import LicenseManager
log=logging.getLogger(__name__)
from.colab_helper import get_vnstock_data_dir
from.constants import AUKY
class VnstockInitializer:
	def __init__(self,target,repo_owner,repo_name,analytics_class=Analytics,token_manager_class=TokenManager,license_manager_class=LicenseManager):self.project_dir=get_vnstock_data_dir();self.home_dir=self.project_dir.parent;self.id_dir=self.project_dir/'id';self.token_path=self.project_dir/'access_token.json';self.repo_owner=repo_owner;self.repo_name=repo_name;self.id=self.project_dir/'user.json';self.env_config=self.id_dir/'env.json';self.target=target;self.RH='asejruyy^&%$#W2vX>NfwrevDRESWR';self.LH='YMAnhuytr%$59u90y7j-mjhgvyFTfbiuUYH';self.analytics_class=analytics_class;self.token_manager_class=token_manager_class;self.license_manager_class=license_manager_class;self._init_managers()
	def _init_managers(self):key=generate_key(self.project_dir,self.id);self.cph=create_fernet_cipher(key);self.analytics=self.analytics_class(self.project_dir,self.id_dir,self.target,self.RH,self.LH);self.token_manager=self.token_manager_class(self.project_dir,self.target,self.RH,self.LH);self.license_manager=self.license_manager_class(self.project_dir,self.repo_owner,self.repo_name)
	def system_info(self):return self.analytics.system_info()
	def log_analytics_data(self,license_info):return self.analytics.log_analytics_data(license_info)
	def packages_installed(self):return self.analytics.packages_installed()
	def _check_and_refresh_token(self,repo_name=None):return self.token_manager._check_and_refresh_token(repo_name=repo_name if repo_name else self.repo_name)
	def licensing_id(self,access_token):return self.license_manager.licensing_id(access_token)