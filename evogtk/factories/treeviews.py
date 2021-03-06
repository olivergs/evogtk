# -*- coding: utf-8 -*-
###############################################################################
# Copyright (C) 2008 EVO Sistemas Libres <central@evosistemas.com>
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
###############################################################################
# treeviews
# Treeview factory class
###############################################################################

# Import GTK
import gtk

###############################################################################
# TreeView Factory class
###############################################################################
class TreeViewFactory(object):

    ###############################################################################
    # TreeView Factory methods
    ###############################################################################
    
    TREEVIEW_MODEL_TYPES={
        'list': gtk.ListStore,
        'tree': gtk.TreeStore,
    }
    
    TREEVIEW_COLUMN_TYPES={
        'str': str,
        'markup': str,
        'int': int,
        'float': float,
        'bool': bool,
        'pixbuf': gtk.gdk.Pixbuf,
        'progress': float,
    }
    
    def __init__(self,modeltype='list',struct=['str'],headers=[],datacols=[],showheaders=True,menu=None,showmenucheck=None,treeview=None):
        """
        Class constructor
            modeltype: Treeview model type. It can be 'list' or 'tree'
            struct: Struct of the model used for the treeview
            headers: List of names for the column headers (must be as long as struct) or empty list for no headers
            datacols: List of column indexes that will not be added as visible columns to tree view (columns must be in a group)
            showheaders: Specifies if TreeView Headers must be shown
            treeview: Specifies a treeview for using this model. If it's None, a new one is created
        """
        # Check selected model
        if self.TREEVIEW_MODEL_TYPES.has_key(modeltype):
            self.modeltype=self.TREEVIEW_MODEL_TYPES[modeltype]
        else:
            raise TypeError('EVOGTK - TreeViewFactory: Model type must be list or tree, not %s' % modeltype)
        # Generate model struct
        self.modelstruct=[]
        for coltype in struct:
            if isinstance(coltype,list):
                for elem in coltype:
                    self.check_column_type(elem)
                    self.modelstruct.append(self.TREEVIEW_COLUMN_TYPES[elem])
            else:
                self.check_column_type(coltype)
                self.modelstruct.append(self.TREEVIEW_COLUMN_TYPES[coltype])
        # Create storage model
        self.storagemodel=self.modeltype(*self.modelstruct)
        # Create treeview widget
        if not treeview:
            self.treeview=gtk.TreeView(self.storagemodel)
            # Show TreeView headers
            if headers:
                self.treeview.set_headers_visible(showheaders)
        else:
            self.treeview=treeview
            self.treeview.set_model(self.storagemodel)
        # Add the columns to TreeView widget
        index=0
        for coltypes in struct:
            header=''
            if headers:
                header=headers[index]
            index+=self.prepare_column(coltypes, header, index, datacols)
        
        self.popup_menu_widget=menu
        if menu:
            self.treeview.connect('button-press-event',self.popup_menu_callback)
        self.showmenucheck=showmenucheck

    def popup_menu_callback(self,widget,event):
        """
        Show associated menu callback
        """
        if event.button == 3:
            x = int(event.x)
            y = int(event.y)
            time = event.time
            pthinfo = widget.get_path_at_pos(x, y)
            if pthinfo != None:
                path, col, cellx, celly = pthinfo
                widget.grab_focus()
                widget.set_cursor(path,col,0)
                if not self.showmenucheck:
                    self.popup_menu_widget.popup(None,None,None,event.button,time)
                    return True
                else:
                    menu=self.showmenucheck(widget,event)
                    if menu:
                        menu.popup(None,None,None,event.button,time)
                        return True
                
    def check_column_type(self,coltype):
        """
        Check column types
        """
        if not self.TREEVIEW_COLUMN_TYPES.has_key(coltype):
            raise Exception('EVOGTK - TreeViewFactory: Column type must be str, int, pixbuf or progress, not %s' % coltype)

    def prepare_column(self,coltypes,header,baseindex,datacols):
        """
        Prepare a tree view column
        """
        column=gtk.TreeViewColumn(header)
        if not isinstance(coltypes,list):
            coltypes=[coltypes]
        index=0
        for coltype in coltypes:
            if not baseindex+index in datacols:
                if coltype=='str' or coltype=='int' or coltype=='float':
                    # Text or number column
                    cr=gtk.CellRendererText()
                    column.pack_start(cr)
                    column.set_attributes(cr, text=baseindex+index)
                if coltype=='markup':
                    # Pango markup text column
                    cr=gtk.CellRendererText()
                    column.pack_start(cr)
                    column.set_attributes(cr, markup=baseindex+index)
                elif coltype=='pixbuf':
                    # Pixbuf column
                    cr=gtk.CellRendererPixbuf()
                    column.pack_start(cr)
                    column.set_attributes(cr, pixbuf=baseindex+index)
                elif coltype=='bool':
                    # Toggle column
                    cr=gtk.CellRendererToggle()
                    column.pack_start(cr)
                    column.set_attributes(cr, active=baseindex+index)
                elif coltype=='progress':
                    # Progress column
                    cr=gtk.CellRendererProgress()
                    column.pack_start(cr)
                    column.set_attributes(cr, value=baseindex+index)
            index+=1
        self.treeview.append_column(column)
        return index

    def append(self,data,parent=None):
        """
        Appends data to treeview
        """
        if self.modeltype==gtk.TreeStore:
            return self.storagemodel.append(parent,data)
        else:
            return self.storagemodel.append(data)
        
    def search(self,value,col=0,count=False,startwith=False):
        """
        Search first occurence of a value in tree view and return iterator 
        """
        iter=self.storagemodel.get_iter_first()
        while iter:
            val=self.storagemodel.get_value(iter,col)
            if startwith:
                if val.lower().startswith(value.lower()):
                    return iter
            else:
                if val==value:
                    return iter
            iter=self.storagemodel.iter_next(iter)
        return None

    def starts_with(self,value,col=0,count=False):
        """
        Search first occurence of a value in tree view and return iterator 
        """
        iter=self.storagemodel.get_iter_first()
        while iter:
            val=self.storagemodel.get_value(iter,col)
            if val==value:
                return iter
            iter=self.storagemodel.iter_next(iter)
        return None

    def remove(self,value=None,col=0):
        """
        Removes currently selected data from treeview
        """
        if value:
            iter=self.search(value,col)
            if iter:
                self.storagemodel.remove(iter)
                return True
        else:
            model,iter=self.treeview.get_selection().get_selected()
            if iter:
                model.remove(iter)
                return True
        return False

    def update(self,value,data,col=0):
        """
        Updates a register
        """
        iter=self.search(value,col)
        if iter:
            for colindex in range(len(data)):
                self.storagemodel.set_value(iter,colindex,data[colindex])
            return True
        return False

    def count(self,value=None,col=0):
        """
        Returns total register count or ocurrences of a value
        """
        count=0
        iter=self.storagemodel.get_iter_first()
        while iter:
            if value:
                val=self.storagemodel.get_value(iter,col)
                if val==value:
                    count+=1
            else:
                count+=1
            iter=self.storagemodel.iter_next(iter)
        return count

    def getRow(self,value,col=0):
        """
        Returns data stored in a row as a list
        """
        row=[]
        iter=self.search(value,col)
        if iter:
            for col in range(len(self.modelstruct)):
                row.append(self.storagemodel.get_value(iter,col))
        return row        

    def getData(self):
        """
        Returns all rows data as a list of lists
        """
        data=[]
        iter=self.storagemodel.get_iter_first()
        while iter:
            row=[]
            for col in range(len(self.modelstruct)):
                row.append(self.storagemodel.get_value(iter,col))
            data.append(row)
            iter=self.storagemodel.iter_next(iter)
        return data

    def clear(self):
        """
        Clears all data
        """
        self.storagemodel.clear()

    def selected(self):
        """
        Returns currently selected row as a list or None if nothing selected
        """
        model,iter=self.treeview.get_selection().get_selected()
        if iter:
            data=[]
            for col in range(len(self.modelstruct)):
                data.append(model.get_value(iter,col))
            return data
        else:
            return None

    def select(self,value,col=0):
        """
        Selects first row with specified value
        """
        iter=self.search(value,col)
        if iter:
            self.treeview.set_cursor(self.storagemodel.get_path(iter))
            return True
        else:
            return False