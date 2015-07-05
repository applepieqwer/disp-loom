#!/usr/bin/python
# -*- coding: UTF-8 -*-
import wx  
import wx.grid 
import datetime
import calendar
from skylark import Database, Model, Field, PrimaryKey, ForeignKey, fn, distinct

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

class loom_table(wx.grid.PyGridTableBase):
	def __init__(self,year,month):
		wx.grid.PyGridTableBase.__init__(self)
		self.year = year
		self.month = month
		self.date_now = datetime.date(year,month,1)
		self.date_from = self.date_now - datetime.timedelta(days=7)
		self.date_to = self.date_now + datetime.timedelta(days = calendar.monthrange(year, month)[1]-1)
		self.date_days = (self.date_to-self.date_from).days + 1
		self.date_list = [self.date_from + datetime.timedelta(days=w) for w in range(self.date_days)]
		
		
	def __init_database(self):
		Database.config(host='applepie-atom',db='loom', user='root', passwd='v79762', charset='utf8')
		
	def Rebuild_data(self):
		self.__init_database()
		r = Workers.getall()
		self.workers = [{'idworkers':w.idworkers,'w_name':w.w_name,'w_color':w.w_color} for w in r]
		r = Tables.getall()
		self.tables = [{'idtables':w.idtables,'t_name':w.t_name,'t_open':w.t_open,'t_close':w.t_close,'t_can_empty':w.t_can_empty,'t_disp_rule':w.t_disp_rule,'t_order':w.t_order} for w in r]
		self.__num_cols = len(self.tables)
		self.__num_rows = self.date_days
		self.__col_label=[w['t_name'] for w in self.tables]
		self.__row_label=[str(w) for w in self.date_list]
		self.__data = [([None] * self.__num_cols) for i in range(self.__num_rows)]

	def GetNumberRows(self):
		return self.__num_rows
		
	def GetNumberCols(self):
		return self.__num_cols
		
	def IsEmptyCell(self, row, col):
		return (self.__data[row][col] == None)

	def GetValue(self,row,col):
		return self.__data[row][col]
		
	def SetValue(self,row,col,val):
		self.__data[row][col]=val
		
	def GetColLabelValue(self,col):
		return self.__col_label[col]
		
	def GetRowLabelValue(self,row):
		return self.__row_label[row]

class GridFrame(wx.Frame): 
	def __init__(self, parent): 
		wx.Frame.__init__(self, parent, -1, "A Grid")
		panel = wx.Panel(self)
		mygrid = wx.grid.Grid(panel)
		grid_data = loom_table(2012,2)
		grid_data.Rebuild_data()
		mygrid.SetTable(grid_data)
		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(mygrid, 1, wx.EXPAND)
		panel.SetSizer(sizer)
        
if __name__ == '__main__': 
	app = wx.App()
	frame = GridFrame(None)
	frame.Show(True)
	app.MainLoop()
