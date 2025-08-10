import abc,os,duckdb,pandas as pd
class Exporter(abc.ABC):
	@abc.abstractmethod
	def export(self,data,ticker:str,**A):0
	def preview(A,ticker:str,n:int=5,**B):0
class CSVExport(Exporter):
	def __init__(A,base_path:str):
		A.base_path=base_path
		if not os.path.exists(A.base_path):os.makedirs(A.base_path)
	def export(C,data,ticker:str,**D):
		B=False;A=os.path.join(C.base_path,f"{ticker}.csv")
		if os.path.exists(A):data.to_csv(A,mode='a',header=B,index=B)
		else:data.to_csv(A,index=B)
	def preview(B,ticker:str,n:int=5,**D):
		A=os.path.join(B.base_path,f"{ticker}.csv")
		if not os.path.exists(A):return
		C=pd.read_csv(A);return C.tail(n)
class DuckDBExport(Exporter):
	def __init__(A,db_path:str):A.db_path=db_path
	def export(D,data,ticker:str,**E):C='data';B=ticker;A=duckdb.connect(D.db_path);A.execute(f"CREATE TABLE IF NOT EXISTS {B} AS SELECT * FROM data LIMIT 0",{C:data});A.execute(f"INSERT INTO {B} SELECT * FROM data",{C:data});A.close()