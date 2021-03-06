#!/usr/bin/python
# -*- coding: UTF-8 -*-
import wx  
import wx.grid 
import datetime
import calendar
import sqlite3
from skylark import Database, Model, Field, PrimaryKey, ForeignKey, fn, distinct
#from MySQLdb import IntegrityError
from sqlite3 import IntegrityError

Database.set_dbapi(sqlite3)

class Workers(Model):
	table_name = 'workers'
	idworkers = PrimaryKey()
	w_name = Field()
	w_color = Field()
	
class Tables(Model):
	table_name = 'tables'
	idtables = PrimaryKey()
	t_name = Field()
	t_open = Field()
	t_close = Field()
	t_can_empty = Field()
	t_disp_rule = Field()
	t_order = Field()

class Datelines(Model):
	table_name = 'datelines'
	iddatelines = PrimaryKey()
	d_is_hoilday = Field()

class Workers_limit_tables(Model):
	table_name = 'workers_limit_tables'
	workers_idworkers = ForeignKey(Workers.idworkers)
	tables_idtables = ForeignKey(Tables.idtables)
	
class Workers_tempo_limit(Model):
	table_name = 'workers_tempo_limit'
	workers_idworkers = ForeignKey(Workers.idworkers)
	wtl_from = Field()
	wtl_to = Field()
	wtl_reason = Field()
	
class Loomitem(Model):
	table_name = 'loomitem'
	datelines_iddatelines = ForeignKey(Datelines.iddatelines)
	tables_idtables = ForeignKey(Tables.idtables)
	workers_idworkers = ForeignKey(Workers.idworkers)
	l_color = Field()

#database above

class WorkersGridData(wx.grid.PyGridTableBase):
	def __init__(self):
		wx.grid.PyGridTableBase.__init__(self)
	def Rebuild_data(self):
		r = Workers.getall()
		self.workers = [{'idworkers':w.idworkers,'w_name':w.w_name,'w_color':w.w_color} for w in r]
		r = Tables.getall()
		self.tables = [{'idtables':w.idtables,'t_name':w.t_name,'t_open':w.t_open,'t_close':w.t_close,'t_can_empty':w.t_can_empty,'t_disp_rule':w.t_disp_rule,'t_order':w.t_order} for w in r]
		self.__num_rows = len(self.workers)
		self.__num_cols = 2 + len(self.tables)
		for i in range(self.__num_rows):
			self.workers[i]['idtables'] = self.GetWorkerLimit(self.workers[i]['idworkers'])
		
	def GetAttr(self, row, col, someExtraParameter ):
		attr = wx.grid.GridCellAttr()
		attr.SetReadOnly(True)
		if col == 1:
			attr.SetBackgroundColour(self.workers[row]['w_color'])
		return attr
		
	def GetNumberRows(self):
		return self.__num_rows
		
	def GetNumberCols(self):
		return self.__num_cols
		
	def IsEmptyCell(self, row, col):
		return False

	def CheckWorkerLimit(self,idworkers,idtables):
		q = Workers_limit_tables.where(workers_idworkers=idworkers,tables_idtables=idtables).select(Workers_limit_tables.workers_idworkers,Workers_limit_tables.tables_idtables)
		r = q.execute()
		if r.count > 0:
			return "OK"
		else:
			return ""
			
	def GetWorkerLimit(self,idworkers):
		q = Workers_limit_tables.where(workers_idworkers=idworkers).select(Workers_limit_tables.tables_idtables)
		r = q.execute()
		return [w.tables_idtables for w in r.all()]
		
	def SetWorkerLimit(self,idworkers,idtables):
		for i in self.workers:
			if i['idworkers'] == idworkers:		
				if idtables in i['idtables']:
					#del
					Workers_limit_tables.where(tables_idtables=idtables,workers_idworkers=idworkers).delete().execute()
					i['idtables'].remove(idtables)
					return False
				else:
					#new
					Workers_limit_tables.create(tables_idtables=idtables,workers_idworkers=idworkers)
					i['idtables'].append(idtables)
					return True
		
	def GetValue(self,row,col):
		if col == 0:
			return self.workers[row]['w_name']
		if col == 1:
			return self.workers[row]['w_color']
		if col >1:
			if self.tables[col-2]['idtables'] in self.workers[row]['idtables']:
				return 'OK'
			else:
				return ''
		
	def SetValue(self,row,col,val):
		pass
		
	def GetColLabelValue(self,col):
		if col == 0:
			return '姓名'
		if col == 1:
			return '颜色'
		if col >1:
			return self.tables[col-2]['t_name']
		
	def GetRowLabelValue(self,row):
		return self.workers[row]['idworkers']
		
		
class LoomGridItem():
	def __init__(self,iddatelines,idtables,text='',color='#FFFFFF',textcolor='#000000'):
		self.text = text
		self.color = color
		self.textcolor = textcolor
		self.readonly = True
		self.idtables = idtables
		self.t_name = ''
		self.iddatelines = iddatelines
		self.idworkers = None
		self.datetime_line = None
		self.datetime_from = None
		self.datetime_to = None
		self.need_rebuild = True
		self.legal = True
		self.illegal_reason = ['','','']#three rules,three reasons
		t = Tables.findone(idtables=self.idtables)
		self.t_can_empty = t.t_can_empty
		self.t_disp_rule = None
		self.t_name = t.t_name
		
	def Dump(self):
		return  'LoomGridItem.Dump:\n datetime = %s\n datetime_from = %s\n datetime_to = %s\n idtables = %s\n idworkers = %s\n text = %s\n color = %s\n need_rebuild = %s\n t_disp_rule = %s\n legal = %s\n illegal_reason[0] = %s\n illegal_reason[1] = %s\n illegal_reason[2] = %s'.decode('utf8')%(self.datetime_line,self.datetime_from,self.datetime_to,self.idtables,self.idworkers,self.text,self.color,self.need_rebuild,str(self.t_disp_rule),str(self.legal),self.illegal_reason[0],self.illegal_reason[1],self.illegal_reason[2])

	def Del(self):
		if self.IsEmpty():
			return
		else:
			q = Loomitem.where(datelines_iddatelines = self.iddatelines , tables_idtables = self.idtables).delete()
			q.execute()
			self.need_rebuild = True
			self.Rebuild_data()
			print self.Dump()

	def IsEmpty(self):
		return (self.idworkers == None)

	def SetWorker(self,idworkers):
		#print self.iddatelines, self.idtables,idworkers
		if self.IsEmpty():
			try:
				Loomitem.create(datelines_iddatelines = self.iddatelines, tables_idtables = self.idtables, workers_idworkers = idworkers)
			except IntegrityError:
				pass
		else:
			if idworkers == self.idworkers:
				return
			q = Loomitem.where(datelines_iddatelines = self.iddatelines , tables_idtables = self.idtables).update(workers_idworkers = idworkers).limit(1)
			q.execute()
		self.need_rebuild = True
		self.CheckOne()
		
	def Rebuild_data(self):
		#print 'LoomGridItem.Rebuild_data',self.idtables,self.iddatelines
		self.need_rebuild = False
		if self.idtables == None or self.iddatelines == None:
			self.idworkers = None
			self.text = ''
			self.t_name = ''
			self.need_rebuild = True
			return
		#------------------------------
		t = Tables.at(self.idtables).getone()
		self.datetime_line =  datetime.datetime.strptime(self.iddatelines,'%Y-%m-%d') 
		if type(t.t_open) == unicode:
			tempsplit = t.t_open.split(':')
			t.t_open = datetime.timedelta(hours=int(tempsplit[0]),minutes=int(tempsplit[1]),seconds=int(tempsplit[2]))
		if type(t.t_close) == unicode:
			tempsplit = t.t_close.split(':')
			t.t_close = datetime.timedelta(hours=int(tempsplit[0]),minutes=int(tempsplit[1]),seconds=int(tempsplit[2]))
		self.datetime_from = self.datetime_line + t.t_open
		self.datetime_to = self.datetime_line + t.t_close
		
		if type(t.t_disp_rule) == unicode:
			tempsplit = t.t_disp_rule.split(':')
			self.t_disp_rule = datetime.timedelta(hours=int(tempsplit[0]),minutes=int(tempsplit[1]),seconds=int(tempsplit[2]))
		else:
			self.t_disp_rule  = t.t_disp_rule

		q = Loomitem.where(datelines_iddatelines = self.iddatelines , tables_idtables = self.idtables).limit(1).select(Loomitem.workers_idworkers,Loomitem.l_color)
		r = q.execute()
		if r.count > 0:
			t = r.one()
			self.idworkers = t.workers_idworkers
			w = Workers.at(self.idworkers).getone()
			self.text = w.w_name
			self.color = w.w_color
			if t.l_color != None:
				self.color = t.l_color
			return
		else:
			self.idworkers = None
			self.text = ''
			self.color = '#FFFFFF'
			self.textcolor = '#000000'
			self.legal = True
			self.illegal_reason = ['','','']
			return
	
	def CheckOne(self):
#		检查席位的合法性
		if self.need_rebuild:
			self.Rebuild_data()
		if self.IsEmpty():
			if self.t_can_empty:
				self.legal = True
				self.illegal_reason[0] = ''
				return True
			else:
				self.legal = False
				self.illegal_reason[0] = '席位符合性检查（错误）：%s “%s”不能为空'.decode('utf8')%(str(self.datetime_from),self.t_name)
				return False
		q = Workers_limit_tables.where(tables_idtables=self.idtables,workers_idworkers=self.idworkers).limit(1).select(Workers_limit_tables.tables_idtables,Workers_limit_tables.workers_idworkers)
#		print q.sql
		r = q.execute()
		if r.count > 0:
			self.legal = True
			self.illegal_reason[0] = 'Pass'
			return True
		else:
			self.legal = False
			self.illegal_reason[0] = '席位符合性检查（错误）：%s “%s”无法工作在“%s”'.decode('utf8')%(str(self.datetime_from),self.text,self.t_name)
			print self.illegal_reason[0]
			return False
	
	def __str__(self):
		return self.text.encode('utf8')

		
class LoomGridData(wx.grid.PyGridTableBase):
	def __init__(self,year,month):
		wx.grid.PyGridTableBase.__init__(self)
		self.year = year
		self.month = month
		self.date_now = datetime.date(year,month,1)
		self.date_from = self.date_now - datetime.timedelta(days=7)
		self.date_to = self.date_now + datetime.timedelta(days = calendar.monthrange(year, month)[1]-1)
		self.date_days = (self.date_to-self.date_from).days + 1
		self.date_list = [self.date_from + datetime.timedelta(days=w) for w in range(self.date_days)]
		
	def Rebuild_data(self):
		r = Workers.getall()
		self.workers = [{'idworkers':w.idworkers,'w_name':w.w_name,'w_color':w.w_color} for w in r]
		r = Tables.getall()
		self.tables = [{'idtables':w.idtables,'t_name':w.t_name,'t_open':w.t_open,'t_close':w.t_close,'t_can_empty':w.t_can_empty,'t_disp_rule':w.t_disp_rule,'t_order':w.t_order} for w in r]
		self.__num_cols = len(self.tables)
		self.__num_rows = self.date_days
		self.__col_label=[w['t_name'] for w in self.tables]
		self.__row_label=[str(w) for w in self.date_list]
		self.__data = [([None] * self.__num_cols) for i in range(self.__num_rows)]
		for r in range(self.__num_rows):
			for c in range(self.__num_cols):
				self.__data[r][c] = LoomGridItem(str(self.date_list[r]),self.tables[c]['idtables'])
		for i in self.date_list:
			try:
				Datelines.create(iddatelines = i)
			except IntegrityError:
				continue

	def GetItem(self,row,col):
		return self.__data[row][col]
		
	def SearchIdworkers(self,row,col,idworkers):
		for i in range(row):
			if self.GetItem(i,col).idworkers == idworkers:
				#print 'found at',i,col
				return i
		return None
		
	def AutoRepeat(self,row,col):
		if self.IsEmptyCell(row,col):
			return None
		target_idworkers = self.GetItem(row,col).idworkers
		f = self.SearchIdworkers(row,col,target_idworkers)
		if f is None:
			return None
		else:
			d = row - f
			nextrow = row + d
			while nextrow < self.GetNumberRows():
				self.GetItem(nextrow,col).SetWorker(target_idworkers)
				nextrow = nextrow + d
			return nextrow - d

	def ClearIllegalReason(self):
#		清除所有错误信息
		for r in range(self.__num_rows):
			for c in range(self.__num_cols):
				i = self.__data[r][c]
				i.legal = True
				i.illegal_reason = ['','','']

	def CheckOne(self):
#		检查席位的合法性
		for r in range(self.__num_rows):
			for c in range(self.__num_cols):
				i = self.__data[r][c]
				if i.need_rebuild:
					i.Rebuild_data()
				i.CheckOne()
				
	def CheckTwo(self):
#		检查一般劳动时间限制
		workers_list = {}
		for r in range(self.__num_rows):
			for c in range(self.__num_cols):
				i = self.__data[r][c]
				if i.need_rebuild:
					i.Rebuild_data()
				if i.IsEmpty():
					continue
				if i.idworkers in workers_list.keys():
					workers_list[i.idworkers].append(list((r,c,i.datetime_from,i.datetime_to)))
				else:
					workers_list[i.idworkers] = [list((r,c,i.datetime_from,i.datetime_to))]
#		print workers_list
		for k in workers_list.keys():
			#for every worker
			for i in range(len(workers_list[k])):
				#for every item
				#get datetimefrom #1
				f = workers_list[k][i][2]
				for d in workers_list[k]:
					#for every item
					#compare datetimefrom  and datetimeto
					if f > d[2] and f<= d[3]:
						##find illegal
						##let's mark 2 items illegal:
						i1 = self.__data[workers_list[k][i][0]][workers_list[k][i][1]]
						i2 = self.__data[d[0]][d[1]]
						i1.legal = False
						i1.illegal_reason[1] = '常规时间检查（错误）：%s “%s”的“%s”与%s “%s”的“%s”冲突'.decode('utf8')%(str(i1.datetime_from),i1.text,i1.t_name,str(i2.datetime_from),i2.text,i2.t_name)
						i2.legal = False
						i2.illegal_reason[1] = '常规时间检查（错误）：%s “%s”的“%s”与%s “%s”的“%s”冲突'.decode('utf8')%(str(i2.datetime_from),i2.text,i2.t_name,str(i1.datetime_from),i1.text,i1.t_name)
						print i1.illegal_reason[1]
						print i2.illegal_reason[1]
					else:
						i1 = self.__data[workers_list[k][i][0]][workers_list[k][i][1]]
						if i1.legal:
							i1.illegal_reason[1]  = 'Pass'
					
	def CheckThree(self):
		#max = 10 hours and 24x7 hours
		max_10 = datetime.timedelta(hours = 10)
		max_24x7 = datetime.timedelta(days = 7)
		#8 hours and 24 hours
		td8 = datetime.timedelta(hours = 8)
		td24 = datetime.timedelta(hours = 24)
		
#		检查签派时间
		workers_list = {}
		for r in range(self.__num_rows):
			for c in range(self.__num_cols):
				i = self.__data[r][c]
				if i.need_rebuild:
					i.Rebuild_data()
				if i.IsEmpty():
					continue
				if i.idworkers in workers_list.keys():
					workers_list[i.idworkers].append(list((r,c,i.datetime_from,i.datetime_to,i.t_disp_rule)))
				else:
					workers_list[i.idworkers] = [list((r,c,i.datetime_from,i.datetime_to,i.t_disp_rule))]
		for i in workers_list.keys():
			workers_list[i].sort(key=lambda x:x[2])
			#print workers_list[i]
			c = len(workers_list[i])
			
			#检查连续24小时内工作满10小时前休息连续的8小时。
			prev_k = 0
			first_k = 0
			W = datetime.timedelta(0)
			R= datetime.timedelta(0)
			for k in range(c):
				first_k_workfrom, first_k_workto, first_k_disprule = workers_list[i][first_k][2:]
				prev_k_workfrom, prev_k_workto, prev_k_disprule = workers_list[i][prev_k][2:]
				k_workfrom, k_workto, k_disprule = workers_list[i][k][2:]
				if k_workto - first_k_workto > td24:
					W = W - first_k_disprule
					first_k = first_k + 1
				if prev_k != k:
					R = k_workfrom - prev_k_workto
				if R >= td8:
					W = datetime.timedelta(0)
					first_k = k
					prev_k = k
					continue
				W = W + k_disprule
				if W > max_10:
					##illegal
					i1 = self.__data[workers_list[i][k][0]][workers_list[i][k][1]]
					i1.legal = False
					i1.illegal_reason[2] = '执勤时间检查（错误）：%s “%s”的“%s”不满足24小时内工作10小时休息8小时要求'.decode('utf8')%(str(i1.datetime_from),i1.text,i1.t_name)
				else:
					prev_k = k
					
			#检查连续24*7小时内休息连续的24小时。
			first_k = 0
			prev_k = 0
			R= datetime.timedelta(0)
			for k in range(c):
				first_k_workfrom, first_k_workto, first_k_disprule = workers_list[i][first_k][2:]
				prev_k_workfrom, prev_k_workto, prev_k_disprule = workers_list[i][prev_k][2:]
				k_workfrom, k_workto, k_disprule = workers_list[i][k][2:]
				if prev_k != k:
					R = k_workfrom - prev_k_workto
				if R >= td24:
					print str(R)
					prev_k = k
					first_k = k
					continue
				print k_workto - first_k_workfrom
				if k_workto - first_k_workfrom > max_24x7:
					##illegal
					i1 = self.__data[workers_list[i][k][0]][workers_list[i][k][1]]
					i1.legal = False
					i1.illegal_reason[2] = '执勤时间检查（错误）：%s “%s”的“%s”不满足7个工作日内休息24小时要求'.decode('utf8')%(str(i1.datetime_from),i1.text,i1.t_name)
				else:
					prev_k = k
					i1 = self.__data[workers_list[i][k][0]][workers_list[i][k][1]]
					i1.illegal_reason[2] = 'Pass'

	def GetNumberRows(self):
		return self.__num_rows
		
	def GetNumberCols(self):
		return self.__num_cols
		
	def IsEmptyCell(self, row, col):
		return self.__data[row][col].IsEmpty()

	def GetValue(self,row,col):
		i = self.__data[row][col]
		if i.need_rebuild:
			i.Rebuild_data()
		return str(self.__data[row][col])

	def SetValue(self,row,col,val):
		pass
		
	def GetColLabelValue(self,col):
		return self.__col_label[col]
		
	def GetRowLabelValue(self,row):
		return self.__row_label[row]
		
	def GetAttr(self, row, col, someExtraParameter ):
		i = self.__data[row][col]
#		i.idtables = self.tables[col]['idtables']
		if i.need_rebuild:
			i.Rebuild_data()
		attr = wx.grid.GridCellAttr()
		attr.SetReadOnly(self.__data[row][col].readonly)
		if not self.__data[row][col].legal:
			attr.SetBackgroundColour('#FF0000')
		else:
			attr.SetBackgroundColour(self.__data[row][col].color)
		attr.SetTextColour(self.__data[row][col].textcolor)
		return attr

class BaseGrid(wx.grid.Grid):
	idworkers = None
	idtables = None
	iddatelines = None
	def __init__(self,parent):
		wx.grid.Grid.__init__(self,parent)
	def ShowIds(self):
		print 'iddatelines = %s, idtables = %s, idworkers=%s'%(BaseGrid.iddatelines,BaseGrid.idtables,BaseGrid.idworkers)

class WorkersGrid(BaseGrid):
	def __init__(self,parent):
		BaseGrid.__init__(self,parent)
		self.grid_data = WorkersGridData()
		self.grid_data.Rebuild_data()
		self.SetTable(self.grid_data)
		self.Bind(wx.grid.EVT_GRID_CELL_LEFT_DCLICK, self.OnCellLeftDClick)
		
	def Rebuild_data(self):
		self.grid_data.Rebuild_data()
		
	def NewDisp(self,name,color='#FFFFFF'):
		Workers.create(w_name=name.strip(),w_color=color.strip())
		self.grid_data.Rebuild_data()
		self.SetTable(self.grid_data)
		self.ForceRefresh()
		
	def OnCellLeftDClick(self, evt):
		col = evt.GetCol()
		if col == 0:
			BaseGrid.idworkers = self.grid_data.workers[evt.GetRow()]['idworkers']
			#print 'WorkersGrid Click: %s'%self.grid_data.workers[evt.GetRow()]['w_name']
			self.ShowIds()
		elif col == 1:
			#color
			BaseGrid.idworkers = self.grid_data.workers[evt.GetRow()]['idworkers']
			dlg = wx.ColourDialog(self)
			dlg.GetColourData().SetChooseFull(True)
			if dlg.ShowModal() == wx.ID_OK:
				color = dlg.GetColourData().GetColour().GetAsString(flags=wx.C2S_HTML_SYNTAX)
				Workers.where(idworkers=BaseGrid.idworkers).update(w_color=color).execute()
				self.grid_data.Rebuild_data()
				self.ForceRefresh()
		elif col > 1:
			self.grid_data.SetWorkerLimit(self.grid_data.workers[evt.GetRow()]['idworkers'],self.grid_data.tables[col-2]['idtables'])
			self.ForceRefresh()
		evt.Skip()

class LoomGrid(BaseGrid):
	def __init__(self,parent):
		BaseGrid.__init__(self,parent)
		self.grid_data = LoomGridData(2012,2)
		self.grid_data.Rebuild_data()
		self.SetTable(self.grid_data)
		self.currentSelection = {'toprow':None,'bottonrow':None,'leftcol':None,'rightcol':None}
		self.Bind(wx.grid.EVT_GRID_CELL_LEFT_DCLICK, self.OnCellLeftDClick)
		self.Bind(wx.grid.EVT_GRID_SELECT_CELL,self._OnSelectedCell)
		self.Bind(wx.grid.EVT_GRID_RANGE_SELECT,self._OnSelectedRange)
		
	def Info(self):
		if self.currentSelection['toprow'] is None or self.currentSelection['leftcol'] is None:
			print 'No selection,Plz select a item.'
			return
		print self.grid_data.GetItem(self.currentSelection['toprow'],self.currentSelection['leftcol']).Dump()
		
	def Del(self):
		if self.currentSelection['toprow'] is None or self.currentSelection['leftcol'] is None:
			return
		self.grid_data.GetItem(self.currentSelection['toprow'],self.currentSelection['leftcol']).Del()
		self.ForceRefresh()
	
	def _OnSelectedRange(self,evt):
		if evt.Selecting():
			self.currentSelection = {'toprow':evt.GetTopRow(),'bottonrow':evt.GetBottomRow(),'leftcol':evt.GetLeftCol(),'rightcol':evt.GetRightCol()}
			print self.currentSelection
		evt.Skip()
		
	def _OnSelectedCell(self,evt):
		self.currentSelection = {'toprow':evt.GetRow(),'bottonrow':evt.GetRow(),'leftcol':evt.GetCol(),'rightcol':evt.GetCol()}
		print self.currentSelection
		evt.Skip()
		
	def GetLoomItem(self,evt):
		return self.grid_data.GetItem(evt.GetRow(),evt.GetCol())

	def AutoRepeat(self):
		if self.currentSelection['leftcol'] is None:
			return
		for c in range(self.currentSelection['leftcol'],self.currentSelection['rightcol']+1):
			for r in range(self.currentSelection['toprow'],self.currentSelection['bottonrow']+1):
				BaseGrid.iddatelines = self.grid_data.date_list[r]
				BaseGrid.idtables = self.grid_data.tables[c]['idtables']
				self.grid_data.AutoRepeat(r,c)
		self.ForceRefresh()

	def Rebuild_data(self):
		self.grid_data.Rebuild_data()
		
	def Check(self):
		self.grid_data.CheckOne()
		self.grid_data.CheckTwo()
		self.grid_data.CheckThree()
		self.ForceRefresh()
	
	def OnCellLeftDClick(self, evt):
		BaseGrid.iddatelines = self.grid_data.date_list[evt.GetRow()]
		BaseGrid.idtables = self.grid_data.tables[evt.GetCol()]['idtables']
		print "LoomGrid Click: %s,%s" % (BaseGrid.iddatelines,self.grid_data.tables[evt.GetCol()]['t_name'])
		if BaseGrid.idworkers != None:
			self.GetLoomItem(evt).SetWorker(BaseGrid.idworkers)
			self.ForceRefresh()
		else:
			print 'Select a Worker!!!'
		print self.GetLoomItem(evt).Dump()
		evt.Skip()

class WorkersFrame(wx.Frame):
	def __init__(self, parent): 
		wx.Frame.__init__(self, parent, title="签派员列表",size=(500,500))
		panel = wx.Panel(self)
		self.mygrid = WorkersGrid(panel)
		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(self.mygrid , 1, wx.EXPAND)
		panel.SetSizer(sizer)
		self.Bind(wx.EVT_CLOSE,self.OnClose)
		menuFile = wx.Menu()
		menuItem0 = menuFile.Append(wx.ID_ANY,'新建签派员','New Dispatchers')
		self.Bind(wx.EVT_MENU, self.OnNewDisp, menuItem0)
		menuItem1 = menuFile.Append(wx.ID_EXIT,'退出')
		self.Bind(wx.EVT_MENU, self.OnClose, menuItem1)
		menuBar = wx.MenuBar()
		menuBar.Append(menuFile,'文件')
		self.SetMenuBar(menuBar)
		
	def OnNewDisp(self,evt):
		new_disp = wx.GetTextFromUser('输入新签派员姓名', caption='输入新签派员姓名',default_value='', parent=self).strip()
		if len(new_disp)>0:
			self.mygrid.NewDisp(new_disp)
		
	def OnClose(self,evt):
		self.Hide()
	
	def Rebuild_data(self):
		self.mygrid.Rebuild_data()
		
	def ForceRefresh(self):
		self.mygrid.ForceRefresh()

class GridFrame(wx.Frame): 
	def __init__(self, parent): 
		wx.Frame.__init__(self, parent, title="This is a Loom",size=(800,800))
		self.CreateStatusBar()
		self.mygrid = LoomGrid(self)
		#menu
		menuFile = wx.Menu()
		menuItem1 = menuFile.Append(wx.ID_EXIT,'退出')
		self.Bind(wx.EVT_MENU, self.OnExit, menuItem1)
		
		menuFrame = wx.Menu()
		menuItem2 = menuFrame.Append(wx.ID_ANY,'签派员列表','List Of Dispatchers')
		self.Bind(wx.EVT_MENU, self.OnWorkers, menuItem2)
		
		menuTool = wx.Menu()
		menuItem6 = menuTool.Append(wx.ID_ANY,'删除','Del!')
		self.Bind(wx.EVT_MENU, self.OnDel, menuItem6)
		menuItem3 = menuTool.Append(wx.ID_ANY,'自动重复','Auto The Loom')
		self.Bind(wx.EVT_MENU, self.OnAutoRepeat, menuItem3)
		menuItem4 = menuTool.Append(wx.ID_ANY,'检查合法性','Check!')
		self.Bind(wx.EVT_MENU, self.OnCheck, menuItem4)
		menuItem5 = menuTool.Append(wx.ID_ANY,'刷新','Refresh!')
		self.Bind(wx.EVT_MENU, self.OnRefresh, menuItem5)
		menuItem6 = menuTool.Append(wx.ID_ANY,'显示单元格信息','Info!')
		self.Bind(wx.EVT_MENU, self.OnInfo, menuItem6)
		
		menuBar = wx.MenuBar()
		menuBar.Append(menuFile,'文件')
		menuBar.Append(menuTool,'工具')
		menuBar.Append(menuFrame,'窗口')
		self.SetMenuBar(menuBar)
		#sub frames
		self.workers_frame = WorkersFrame(self)
		#show frames
		self.Show(True)
		self.workers_frame.Show(True)
		
	def OnInfo(self,evt):
		self.mygrid.Info()
		
	def OnDel(self,evt):
		self.mygrid.Del()
		
	def OnCheck(self,evt):
		self.mygrid.Check()
		
	def OnAutoRepeat(self,evt):
		self.mygrid.AutoRepeat()
		
	def OnWorkers(self,evt):
		self.workers_frame.Show(True)

	def OnRefresh(self,evt):
		self.mygrid.Rebuild_data()
		self.mygrid.ForceRefresh()
		self.workers_frame.Rebuild_data()
		self.workers_frame.ForceRefresh()

	def OnExit(self,evt):
		self.workers_frame.Close()
		self.Close()

if __name__ == '__main__': 
#	Database.config(host='applepie-atom',db='loom', user='root', passwd='v79762', charset='utf8')
	Database.config(db='loom.db')
	app = wx.App()
	mainFrame = GridFrame(None)
	app.MainLoop()
