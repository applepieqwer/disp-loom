#!/usr/bin/python
# -*- coding: UTF-8 -*-
import wx  
import wx.grid 

from skylark import Database, Model, Field, PrimaryKey, ForeignKey, fn, distinct

class loom_table(wx.grid.PyGridTableBase):
	def __init__(self,num_cols,num_rows):
		wx.grid.PyGridTableBase.__init__(self)
		self.__data = [([None] * num_cols) for i in range(num_rows)]
		self.__row_label=range(num_rows)
		self.__col_label=range(num_cols)
		self.__num_cols = num_cols
		self.__num_rows = num_rows
		
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
		grid_data = loom_table(12 , 8)
		mygrid.SetTable(grid_data)
		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(mygrid, 1, wx.EXPAND)
		panel.SetSizer(sizer)
        
if __name__ == '__main__': 
	app = wx.App()
	frame = GridFrame(None)
	frame.Show(True)
	app.MainLoop()
