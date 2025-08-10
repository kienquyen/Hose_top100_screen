_D='market_data'
_C='unknown'
_B='data_type'
_A=None
import csv,json,logging,os,time,traceback,datetime
from abc import ABC,abstractmethod
from typing import Dict,Any,List,Tuple,Set,Optional
class DataProcessor(ABC):
	def __init__(A):A.logger=logging.getLogger(A.__class__.__name__)
	@abstractmethod
	async def process(self,data:Dict[str,Any])->_A:0
class ConsoleProcessor(DataProcessor):
	def __init__(A,pretty_print:bool=True):super().__init__();A.pretty_print=pretty_print
	async def process(A,data:Dict[str,Any])->_A:
		try:
			if A.pretty_print:print(f"Received: {json.dumps(data,indent=2)}")
			else:print(f"Received: {data}")
		except Exception as B:A.logger.error(f"Error in ConsoleProcessor: {B}");A.logger.error(traceback.format_exc())
class CSVProcessor(DataProcessor):
	def __init__(A,filename_template:str='market_data_{data_type}_%Y-%m-%d.csv'):super().__init__();A.filename_template=filename_template;A.files={};A.fields={}
	def _get_filename(B,data:Dict[str,Any])->str:C=data.get(_B,_C);A=B.filename_template.replace('{data_type}',C);A=datetime.datetime.now().strftime(A);return A
	def _create_new_file(B,filename:str,fields:List[str]):
		E=fields;A=filename
		try:import csv;os.makedirs(os.path.dirname(A)or'.',exist_ok=True);C=open(A,'w',newline='');D=csv.DictWriter(C,fieldnames=E);D.writeheader();B.files[A]=C,D;B.fields[A]=set(E);B.logger.info(f"Created new CSV file: {A}");return C,D
		except Exception as F:B.logger.error(f"Error creating CSV file {A}: {F}");B.logger.error(traceback.format_exc());raise
	async def process(A,data:Dict[str,Any])->_A:
		D=data;import csv
		try:
			B=A._get_filename(D);F=set(D.keys())
			if B in A.files:
				C,E=A.files[B];G=A.fields[B];H=F-G
				if H:A.logger.info(f"Found {len(H)} new fields in data. Creating new CSV file.");C.close();J=int(time.time());K=f"{os.path.splitext(B)[0]}_{J}.csv";I=list(G.union(F));C,E=A._create_new_file(K,I);A.files[B]=C,E;A.fields[B]=set(I)
			else:C,E=A._create_new_file(B,list(D.keys()))
			L={A:D.get(A,_A)for A in A.fields[B]};E.writerow(L);C.flush()
		except Exception as M:A.logger.error(f"Error writing to CSV: {M}");A.logger.error(traceback.format_exc())
	def close(A):
		for(B,(C,E))in A.files.items():
			try:C.close();A.logger.debug(f"Closed file: {B}")
			except Exception as D:A.logger.error(f"Error closing file {B}: {D}")
class DuckDBProcessor(DataProcessor):
	def __init__(A,db_path:str,table_prefix:str=_D):
		B=db_path;super().__init__()
		try:import duckdb as C;os.makedirs(os.path.dirname(B)or'.',exist_ok=True);A.con=C.connect(B);A.table_prefix=table_prefix;A.tables={};A.logger.info(f"DuckDB initialized: {B}")
		except ImportError:A.logger.error("DuckDB module not installed. Install with 'pip install duckdb'");raise
		except Exception as D:A.logger.error(f"DuckDB initialization error: {D}");A.logger.error(traceback.format_exc());raise
	def _get_table_name(A,data:Dict[str,Any])->str:B=data.get(_B,_C);return f"{A.table_prefix}_{B}"
	def _ensure_table_exists(A,table_name:str,data:Dict[str,Any])->_A:
		I=data;B=table_name
		try:
			if B in A.tables:
				K=A.tables[B]
				for(C,D)in I.items():
					if C not in K:
						E=A._infer_type(D);F=f'ALTER TABLE "{B}" ADD COLUMN "{C}" {E}'
						try:A.con.execute(F);A.tables[B].add(C);A.logger.info(f"Added column {C} to {B}")
						except Exception as G:A.logger.error(f"Failed to add column {C}: {G}");A.logger.error(traceback.format_exc())
			else:
				try:
					A.con.execute(f'SELECT * FROM "{B}" LIMIT 0');L=A.con.execute(f'PRAGMA table_info("{B}")');H={A[1]for A in L.fetchall()};A.tables[B]=H
					for(C,D)in I.items():
						if C not in H:
							E=A._infer_type(D);F=f'ALTER TABLE "{B}" ADD COLUMN "{C}" {E}'
							try:A.con.execute(F);A.tables[B].add(C);A.logger.info(f"Added column {C} to {B}")
							except Exception as G:A.logger.error(f"Failed to add column {C}: {G}");A.logger.error(traceback.format_exc())
				except Exception:
					H=[];J=set()
					for(C,D)in I.items():E=A._infer_type(D);H.append(f'"{C}" {E}');J.add(C)
					F=f'CREATE TABLE "{B}" ({", ".join(H)})';A.con.execute(F);A.tables[B]=J;A.logger.info(f"Created table {B}")
		except Exception as G:A.logger.error(f"Error ensuring table exists: {G}");A.logger.error(traceback.format_exc());raise
	def _infer_type(C,value:Any)->str:
		B='VARCHAR';A=value
		if A is _A:return B
		elif isinstance(A,bool):return'BOOLEAN'
		elif isinstance(A,int):return'BIGINT'
		elif isinstance(A,float):return'DOUBLE'
		elif isinstance(A,str):return B
		elif isinstance(A,(list,dict)):return'JSON'
		elif isinstance(A,datetime.datetime):return'TIMESTAMP'
		elif isinstance(A,datetime.date):return'DATE'
		else:return B
	def _sanitize_value(B,value:Any)->Any:
		A=value
		if isinstance(A,int)and(A>2147483647 or A<-2147483648):return str(A)
		return A
	async def process(A,data:Dict[str,Any])->_A:
		C=data
		try:
			B=A._get_table_name(C);A._ensure_table_exists(B,C)
			if B in A.tables:D={C:D for(C,D)in C.items()if C in A.tables[B]}
			else:D=C
			if not D:A.logger.warning(f"No valid columns to insert into {B}");return
			E={B:A._sanitize_value(C)for(B,C)in D.items()};F=', '.join([f'"{A}"'for A in E.keys()]);G=', '.join(['?'for A in E.keys()]);H=list(E.values());I=f'INSERT INTO "{B}" ({F}) VALUES ({G})';A.con.execute(I,H);A.logger.debug(f"Inserted data into {B}")
		except Exception as J:A.logger.error(f"Error inserting data into DuckDB: {J}");A.logger.error(traceback.format_exc())
	def close(A):
		try:A.con.close();A.logger.info('DuckDB connection closed')
		except Exception as B:A.logger.error(f"Error closing DuckDB connection: {B}")
class FirebaseProcessor(DataProcessor):
	def __init__(A,collection_prefix:str=_D,service_account_path:str=_A):
		C=service_account_path;B=collection_prefix;super().__init__()
		try:
			import firebase_admin as D;from firebase_admin import credentials as E,firestore as G
			if not D._apps:
				if C:F=E.Certificate(C)
				else:F=E.ApplicationDefault()
				D.initialize_app(F)
			A.db=G.client();A.collection_prefix=B;A.logger.info(f"Firebase Firestore initialized with prefix: {B}")
		except ImportError:A.logger.error("Firebase modules not installed. Install with 'pip install firebase-admin'");raise
		except Exception as H:A.logger.error(f"Firebase initialization error: {H}");A.logger.error(traceback.format_exc());raise
	def _get_collection_name(A,data:Dict[str,Any])->str:B=data.get(_B,_C);return f"{A.collection_prefix}_{B}"
	def _get_document_id(E,data:Dict[str,Any])->str:
		D='index_id';C='ticker';A=data;B=A.get('timestamp',time.time())
		if A.get(_B)=='price'and C in A:return f"{A[C]}_{B}"
		elif A.get(_B)=='index'and D in A:return f"{A[D]}_{B}"
		else:return f"{B}"
	async def process(A,data:Dict[str,Any])->_A:
		B=data
		try:C=A._get_collection_name(B);D=A._get_document_id(B);A.db.collection(C).document(D).set(B);A.logger.debug(f"Data saved to Firestore: {C}/{D}")
		except Exception as E:A.logger.error(f"Error saving to Firestore: {E}");A.logger.error(traceback.format_exc())