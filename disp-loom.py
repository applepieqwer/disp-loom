#!/usr/bin/python
# -*- coding: UTF-8 -*-
import wx  
import wx.grid 

from skylark import Database, Model, Field, PrimaryKey, ForeignKey, fn, distinct

class loom_table(wx.grid.Grid):
	def __init__(self,parent,num_cols,num_rows):
		self.__data = [([None] * num_cols) for i in range(num_rows)]
		self.__row_label=range(num_rows)
		self.__col_label=range(num_cols)
		wx.grid.Grid.__init__(self,parent)
		self.CreateGrid(num_rows , num_cols)
		
	def set_col_label(self,cols):
		self.__col_label = list(cols)
		
	def set_row_label(self,rows):
		self.__row_label = list(rows)

	def get(self,col,row):
		return self.__data[row][col]
		
	def set(self,col,row,val):
		self.__data[row][col]=val

class GridFrame(wx.Frame): 
	def __init__(self, parent): 
		wx.Frame.__init__(self, parent, -1, "A Grid")
		panel = wx.Panel(self)
		mygrid = loom_table(panel, 12 , 8)
		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(mygrid, 1, wx.EXPAND)
		panel.SetSizer(sizer)
        
if __name__ == '__main__': 
	app = wx.App()
	frame = GridFrame(None)
	frame.Show(True)
	app.MainLoop()
