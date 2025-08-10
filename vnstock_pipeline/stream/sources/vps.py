_q='foreign_net_volume'
_p='foreign_sell_volume'
_o='foreign_buy_volume'
_n='volume_4'
_m='open_price'
_l='totalVol'
_k='changePc'
_j='lastVol'
_i='session_id'
_h='ceiling_actual'
_g='average_price'
_f='low_flag'
_e='change_flag'
_d='low_price'
_c='high_price'
_b='change_percent'
_a='unchanged'
_Z='declines'
_Y='advances'
_X='market_code'
_W='event_type'
_V='timeServer'
_U='time_server'
_T='color'
_S='openPrice'
_R='lastPrice'
_Q='total_volume'
_P='last_volume'
_O='last_price'
_N='volume'
_M='lot'
_L='stock_id'
_K='value'
_J='change'
_I='fSVol'
_H='fBVol'
_G='symbol'
_F='sym'
_E='time'
_D='id'
_C='side'
_B='data'
_A=None
import json,time,logging,traceback,asyncio
from typing import Dict,Any,List,Optional,Set
from vnstock_pipeline.stream.client import BaseWebSocketClient
from vnstock_pipeline.stream.parsers import FinancialDataParser
from vnstock_pipeline.stream.utils.session_manager import SessionManager
class VPSDataParser(FinancialDataParser):
	def parse_data(C,raw_data:Dict[str,Any])->Dict[str,Any]:
		E=raw_data;A=super().parse_data(E);D=E.get(_W,'');B=E.get(_B,{})
		if D=='index':C._parse_index_data(B.get(_B,{}),A)
		elif D=='stock':C._parse_stock_data(B.get(_B,{}),A)
		elif D=='stockps':C._parse_stockps_data(B,A)
		elif D=='soddlot':C._parse_soddlot_data(B.get(_B,{}),A)
		elif D=='board':C._parse_board_data(B.get(_B,{}),A)
		elif D=='boardps':C._parse_boardps_data(B,A)
		elif D=='aggregatemarket':C._parse_aggregate_market_data(B,A)
		elif D=='aggregateps':C._parse_aggregate_ps_data(B,A)
		elif D=='spt':C._parse_spt_data(B,A)
		elif D=='psfsell':C._parse_psfsell_data(B,A)
		elif D=='regs':C._parse_regs_data(B,A)
		else:A.update({'raw_data':B})
		return A
	def _parse_index_data(F,index_data,result):
		G='status';E=result;D='oIndex';C='cIndex';A=index_data;E.update({'index_id':A.get(_D),_X:A.get('mc'),'current_index':A.get(C),'open_index':A.get(D),_J:_A if not A.get(C)or not A.get(D)else A.get(C)-A.get(D),'percent_change':F.calculate_percent_change(A.get(C),A.get(D)),_N:A.get('vol'),_K:A.get(_K),'market_time':A.get(_E),G:A.get(G),'acc_vol':A.get('accVol')})
		if'ot'in A:
			try:
				B=A['ot'].split('|')
				if len(B)>=6:E.update({'abs_change':float(B[0])if B[0]else _A,'percent_change_text':B[1]if B[1]else _A,'value_ot':float(B[2])if B[2]else _A,_Y:int(B[3])if B[3]else _A,_Z:int(B[4])if B[4]else _A,_a:int(B[5])if B[5]else _A})
			except Exception as H:F.logger.warning(f"Failed to parse ot field: {H}")
		return E
	def _parse_stock_data(C,stock_data,result):
		B=result;A=stock_data;B.update({_G:A.get(_F),_L:A.get(_D),_O:A.get(_R),_P:A.get(_j),_J:A.get(_J),_b:A.get(_k),_Q:A.get(_l),_c:A.get('hp'),_d:A.get('lp'),_e:A.get('ch'),_f:A.get('lc'),_g:A.get('ap'),_h:A.get('ca'),_E:A.get(_E),_i:A.get('sID'),_C:A.get(_C)})
		if _S in A:B[_m]=A.get(_S)
		return B
	def _parse_stockps_data(B,data,result):C=result;A=data.get(_B,{});C.update({_G:A.get(_F),_L:A.get(_D),_O:A.get(_R),_P:A.get(_j),_T:A.get('cl'),_J:B._safe_convert(A.get(_J),float),_b:B._safe_convert(A.get(_k),float),_Q:A.get(_l),_E:A.get(_E),_c:A.get('hp'),_e:A.get('ch'),_d:A.get('lp'),_f:A.get('lc'),_g:A.get('ap'),_h:A.get('ca'),_U:A.get(_V),_i:A.get('sID'),'level':A.get('lv'),_m:A.get(_S),_C:A.get(_C)});return C
	def _parse_soddlot_data(C,soddlot_data,result):B=result;A=soddlot_data;B.update({_G:A.get(_F),_L:A.get(_D),'ceiling_price':A.get('c'),'floor_price':A.get('f'),'reference_price':A.get('r'),_O:A.get(_R),_P:A.get('lastVolume'),_M:A.get(_M),_X:A.get('mc'),'bid_price_1':A.get('bp1'),'bid_volume_1':A.get('bv1'),'bid_price_2':A.get('bp2'),'bid_volume_2':A.get('bv2'),'bid_price_3':A.get('bp3'),'bid_volume_3':A.get('bv3'),'ask_price_1':A.get('sp1'),'ask_volume_1':A.get('sv1'),'ask_price_2':A.get('sp2'),'ask_volume_2':A.get('sv2'),'ask_price_3':A.get('sp3'),'ask_volume_3':A.get('sv3')});return B
	def _parse_board_data(H,board_data,result):
		D=result;B=board_data;D.update({_G:B.get(_F),_L:B.get(_D),_C:B.get(_C),_U:B.get(_V),_n:B.get('vol4')})
		for E in range(1,4):
			C=f"g{E}"
			if C in B:
				try:
					A=B[C].split('|')
					if len(A)>=3:
						try:F=float(A[0])if A[0]else _A
						except ValueError:F=A[0]
						try:G=int(A[1])if A[1]else _A
						except ValueError:G=A[1]
						D.update({f"price_{E}":F,f"volume_{E}":G,f"flag_{E}":A[2]if A[2]else _A})
				except Exception as I:H.logger.warning(f"Failed to parse {C} field: {I}");D.update({f"{C}_raw":B.get(C)})
		return D
	def _parse_boardps_data(H,data,result):
		D=result;B=data.get(_B,{});D.update({_G:B.get(_F),_L:B.get(_D),_C:B.get(_C),_U:B.get(_V),_n:B.get('vol4')})
		for E in range(1,4):
			C=f"g{E}"
			if C in B:
				try:
					A=B[C].split('|')
					if len(A)>=3:
						try:F=float(A[0])if A[0]else _A
						except ValueError:F=A[0]
						try:G=int(A[1])if A[1]else _A
						except ValueError:G=A[1]
						D.update({f"price_{E}":F,f"volume_{E}":G,f"flag_{E}":A[2]if A[2]else _A})
				except Exception as I:H.logger.warning(f"Failed to parse {C} field: {I}");D.update({f"{C}_raw":B.get(C)})
		return D
	def _parse_aggregate_market_data(E,data,result):D=result;C='fSVal';B='fBVal';A=data;D.update({_Q:A.get('vol'),'total_value':A.get(_K),'put_through_volume':A.get('ptVol'),'put_through_value':A.get('ptValue'),_o:A.get(_H),_p:A.get(_I),'foreign_buy_value':A.get(B),'foreign_sell_value':A.get(C),_Y:A.get('up'),_Z:A.get('down'),_a:A.get('ref'),_q:_A if not A.get(_H)or not A.get(_I)else A.get(_H)-A.get(_I),'foreign_net_value':_A if not A.get(B)or not A.get(C)else A.get(B)-A.get(C)});return D
	def _parse_aggregate_ps_data(C,data,result):B=result;A=data;B.update({_M:A.get(_M),_o:A.get(_H),_p:A.get(_I),_q:_A if not A.get(_H)or not A.get(_I)else A.get(_H)-A.get(_I),'bid_volume':A.get('bid'),'ask_volume':A.get('ask'),'open_interest':A.get('oi')});return B
	def _parse_spt_data(B,data,result):D='price';C=result;A=data.get(_B,{});C.update({'transaction_id':A.get(_D),'transaction_type':A.get('type'),_G:A.get(_F),_T:A.get(_T),D:B._safe_convert(A.get(D),float),_N:B._safe_convert(A.get(_N),int),_K:B._safe_convert(A.get(_K),float),_E:A.get(_E),'market_id':A.get('marketID'),'firm_no':A.get('firmNo')});return C
	def _parse_psfsell_data(B,data,result):A=result;C=data.get(_B);A.update({'psf_sell_value':B._safe_convert(C,float)});return A
	def _parse_regs_data(E,data,result):D='list';C='action';B=result;A=data;B.update({C:A.get(C),'symbols':A.get(D,'').split(',')if isinstance(A.get(D),str)else[]});return B
	def _safe_convert(B,value,convert_func):
		A=value
		if A is _A:return
		try:return convert_func(A)
		except(ValueError,TypeError):return A
class VPSWebSocketClient(BaseWebSocketClient):
	def __init__(A,uri:str='wss://bgdatafeed.vps.com.vn/socket.io/?EIO=3&transport=websocket',ping_interval:int=25,market:str='HOSE',enable_session_manager:bool=True,session_check_interval:int=60):super().__init__(uri,ping_interval);A.raw_messages=[];A.data_parser=VPSDataParser();A.last_data_timestamp=_A;A.message_count=0;(A.received_symbols):Set[str]=set();A.market=market;A.enable_session_manager=enable_session_manager;A.session_manager=_A;A.session_check_interval=session_check_interval;A.data_freeze_check_task=_A;A.data_freeze_threshold=120
	def add_raw_message(A,raw_message:str)->_A:A.raw_messages.append(raw_message)
	def clear_raw_messages(A)->_A:A.raw_messages=[]
	def subscribe_symbols(A,symbols:List[str])->_A:B=','.join(symbols);C=f'42["regs","{{\\"action\\":\\"join\\",\\"list\\":\\"{B}\\"}}"]';A.add_raw_message(C);A.logger.info(f"Added subscription for symbols: {B}")
	async def connect(A)->_A:
		if A.enable_session_manager and not A.session_manager:A.session_manager=SessionManager(market=A.market,check_interval=A.session_check_interval);A.session_manager.register_connect_handler(A._session_connect);A.session_manager.register_disconnect_handler(A._session_disconnect);asyncio.create_task(A.session_manager.start_monitoring());return
		await A._session_connect()
	async def disconnect(A)->_A:
		if A.session_manager:await A.session_manager.stop_monitoring();A.session_manager=_A
		if A.data_freeze_check_task and not A.data_freeze_check_task.done():
			A.data_freeze_check_task.cancel()
			try:await A.data_freeze_check_task
			except asyncio.CancelledError:pass
			A.data_freeze_check_task=_A
		await A._session_disconnect()
	async def _session_connect(A)->_A:A.logger.info('Session manager initiating connection');A.message_count=0;A.last_data_timestamp=_A;A.received_symbols.clear();await super().connect();A.data_freeze_check_task=asyncio.create_task(A._monitor_data_freeze())
	async def _session_disconnect(A)->_A:
		A.logger.info('Session manager initiating disconnection')
		if A.data_freeze_check_task and not A.data_freeze_check_task.done():
			A.data_freeze_check_task.cancel()
			try:await A.data_freeze_check_task
			except asyncio.CancelledError:pass
			A.data_freeze_check_task=_A
		await super().disconnect()
	async def _send_initial_messages(A)->_A:
		if not A.raw_messages:A.logger.warning('No raw messages configured. You may not receive any data.');return
		for B in A.raw_messages:
			if A.websocket:
				try:await A.websocket.send(B);A.logger.info(f"Sent raw message: {B[:50]}...")
				except Exception as C:A.logger.error(f"Error sending raw message: {C}");A.logger.error(traceback.format_exc())
	def _parse_message(A,message:str)->Optional[Dict[str,Any]]:
		B=message
		try:
			A.logger.debug(f"Raw message received: {B[:100]}...");A.last_data_timestamp=time.time();A.message_count+=1
			if B.startswith('42'):
				F=B[2:];D=json.loads(F)
				if isinstance(D,list)and len(D)>=2:
					G=D[0];C=D[1]
					if isinstance(C,str):
						try:C=json.loads(C)
						except json.JSONDecodeError:A.logger.warning(f"Failed to parse payload as JSON: {C[:100]}...")
					H={_W:G,_B:C,'timestamp':time.time()}
					if isinstance(C,dict)and _B in C and isinstance(C[_B],dict):
						E=C[_B].get(_F)
						if E:A.received_symbols.add(E)
					return A.data_parser.parse_data(H)
			elif B=='2':A.logger.debug('Received ping response')
			elif B=='3':A.logger.debug('Received pong message')
			elif B.startswith('0'):A.logger.info(f"Connection established: {B}")
			elif B.startswith('40'):A.logger.info(f"Socket.IO connection established: {B}")
			elif B.startswith('41'):A.logger.warning(f"Socket.IO disconnected: {B}")
			else:A.logger.debug(f"Received unknown message type: {B[:50]}...")
			return
		except Exception as I:A.logger.error(f"Error parsing message: {I}");A.logger.error(traceback.format_exc());A.logger.debug(f"Problematic message: {B[:200]}...");return
	async def _monitor_data_freeze(A):
		try:
			B=0;D=min(30,A.data_freeze_threshold//4)
			while A.running:
				await asyncio.sleep(D)
				if A.last_data_timestamp is _A:continue
				E=time.time();C=E-A.last_data_timestamp
				if C>A.data_freeze_threshold:
					B+=1;A.logger.warning(f"Potential data freeze detected! No data for {C:.1f}s (Detection #{B})")
					if B>=2:
						A.logger.warning('Multiple data freezes detected, triggering reconnection')
						if A.session_manager:await A.session_manager.trigger_reconnect()
						else:await A._handle_data_freeze()
						B=0
				else:B=0
		except asyncio.CancelledError:A.logger.info('Data freeze monitoring cancelled');raise
		except Exception as F:A.logger.error(f"Error in data freeze monitoring: {F}");A.logger.error(traceback.format_exc())
	async def _handle_data_freeze(A):
		A.logger.info('Handling data freeze - reconnecting')
		try:
			A.running=False
			if A.websocket:await A.websocket.close();A.websocket=_A
		except Exception as B:A.logger.error(f"Error disconnecting during freeze handling: {B}")
		await asyncio.sleep(2)
		try:A.websocket=await websockets.connect(A.uri);A.running=True;A.logger.info('Reconnected after data freeze');await A._send_initial_messages();C=asyncio.create_task(A._send_ping());A.last_data_timestamp=time.time();await A._handle_messages();C.cancel()
		except Exception as B:A.logger.error(f"Error reconnecting after data freeze: {B}");A.logger.error(traceback.format_exc())
	def get_connection_stats(A)->Dict[str,Any]:
		B={'connected':A.websocket is not _A and A.running,'message_count':A.message_count,'received_symbols_count':len(A.received_symbols),'received_symbols':list(A.received_symbols)}
		if A.last_data_timestamp:B['last_data_time']=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(A.last_data_timestamp));B['seconds_since_last_data']=time.time()-A.last_data_timestamp
		return B