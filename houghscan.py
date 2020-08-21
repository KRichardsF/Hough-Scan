import gi
from operation import tiles, hough_process
from plot_view import  DrawGraph, DrawHistogram
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk
import cv2
from matplotlib import pyplot as plt
import matplotlib.image as mpimg
import numpy as np
from matplotlib.backends.backend_gtk3 import NavigationToolbar2GTK3 as NavigationToolbar

class hough_params:
    def __init__(self, blur=5, min_dist=80, canny_detection=80, hough_threshold=50, min_radius=0, max_radius=0):
        self.blur = blur
        self.min_dist = min_dist
        self.canny_detection = canny_detection
        self.hough_threshold = hough_threshold
        self.listbox_row = Gtk.ListBoxRow()
        self.min_radius = min_radius
        self.max_radius = max_radius
        #self.data = None
        #self.tile_size = 800
        #self.no_tiles_x = 12
        #self.no_tiles_y = 10
        #self.doubles_removal_distance = 100

class universal_params:
        data = np.empty((0,3), int)
        liststore = Gtk.ListStore(int, int, int)
        tile_size = 800
        no_tiles_x = 12
        no_tiles_y = 10
        doubles_removal_distance = 100



class Handler:
    def add_run(run_list):
        run = hough_params()
        run_list.append(run)

    def onDestroy(self, *args):
        Gtk.main_quit()
        return True

    def closeWindow(self, widget, *args):
        widget.hide()
        return True

    def updatezoom():
        main_setup.image_plot.zoom(main_setup.preview_position[0],
                                        main_setup.preview_position[1],
                                        params=main_setup.current_params)
        print(main_setup.current_params)

    def updatezoomonclick(event):
         if event.button!=1: return
         if (event.xdata is None): return
         main_setup.preview_position[0],main_setup.preview_position[1] = event.xdata, event.ydata
         Handler.updatezoom()

    def update_spinbuttons(button_value, parameter):

            print('button pressed')
            before = getattr(main_setup.current_params, parameter)
            setattr(main_setup.current_params, parameter, button_value)
            if getattr(main_setup.current_params, parameter) != before:
                print('scan updated!')
                Handler.updatezoom()

    def add_button_pressed(self, *args):
        Handler.add_run(main_setup.run_list)
        Handler.update_scanlist(main_setup.scan_listbox, main_setup.run_list)
        Handler.last_updated_scanlist_size += 1

    def update_blur(self, entry, *args):
        button_value = int(entry.get_text())
        Handler.update_spinbuttons(button_value, 'blur')

    def update_min_dist(self, entry, *args):
        button_value = int(entry.get_text())
        Handler.update_spinbuttons(button_value, 'min_dist')

    def update_canny_detection(self, entry, *args):
        button_value = int(entry.get_text())
        Handler.update_spinbuttons(button_value, 'canny_detection')

    def update_hough_threshold(self, entry, *args):
        button_value = int(entry.get_text())
        Handler.update_spinbuttons(button_value, 'hough_threshold')

    def update_min_radius(self, entry, *args):
        button_value = int(entry.get_text())
        Handler.update_spinbuttons(button_value, 'min_radius')

    def update_max_radius(self, entry, *args):
        button_value = int(entry.get_text())
        Handler.update_spinbuttons(button_value, 'max_radius')

    def update_tile_size (self, entry, *args):
        button_value = int(entry.get_text())
        print('tile_size', button_value)
        setattr(main_setup.image_plot, 'tile_size', button_value)
        #Handler.update_spinbuttons(button_value, 'tile_size')
        universal_params.tile_size = button_value

    def update_no_tiles_x (self, entry, *args):
        button_value = int(entry.get_text())
        #Handler.update_spinbuttons(button_value, 'no_tiles_x')
        universal_params.no_tiles_x = button_value

    def update_no_tiles_y (self, entry, *args):
        button_value = int(entry.get_text())
        #Handler.update_spinbuttons(button_value, 'no_tiles_y')
        universal_params.no_tiles_y = button_value

    def update_doubles_removal (self, entry, *args):
        button_value = int(entry.get_text())
        #Handler.update_spinbuttons(button_value, 'doubles_removal_distance')
        universal_params.doubles_removal_distance = button_value

    def display_histogram (self, *args):
        histogram_window.hist_plot.draw(universal_params.data)
        histogram_window.histogram.show_all()

    def change_bins(self, entry, *args):
        button_value = int(entry.get_text())
        histogram_window.hist_plot.draw(universal_params.data, bin_no = button_value)

    def build_treeview_model():
        universal_params.liststore.clear()
        data_list = universal_params.data.tolist()
        for i in data_list:
            universal_params.liststore.append(i)

    def display_info (self, *args):
        Handler.build_treeview_model()
        data_window.treeview.set_model(universal_params.liststore)
        data_window.data_table.show()


    def copy_data(self, *args):
        data_list = universal_params.data.tolist()
        csv_string = []
        for i in data_list:
            csv_string.append((str(i))[1:-1])
        csv_string = '\n'.join((csv_string))
        print(csv_string)
        data_window.clipboard.set_text(csv_string, -1)


    def run_analysis(self, *args):
        input_img = cv2.imread(main_setup.image_plot.image, 1)
        eb_img = cv2.cvtColor(input_img, cv2.COLOR_BGR2GRAY)
        tile_array1 = tiles(eb_img, tile_size=universal_params.tile_size,
                                    no_tiles_x=universal_params.no_tiles_x,
                                    no_tiles_y=universal_params.no_tiles_y)


        data = np.empty((0,3), int)
        for i in main_setup.run_list:
            circles = tile_array1.tile(hough_process.hough, blur= i.blur,
                                                            dp= 1,
                                                            min_dist= i.min_dist,
                                                            canny_upper= i.canny_detection,
                                                            hough_threshold= i.hough_threshold,
                                                            min_radius= i.min_radius,
                                                            max_radius= i.max_radius)

            data = np.append(data, circles, axis=0)
            data = tile_array1.remove_doubles(data, separation= universal_params.doubles_removal_distance)

            #np.append(data1, circles, axis=0)
        for i in data:
                cv2.circle(input_img,(i[0],i[1]),i[2],(0,255,0),2)
                cv2.circle(input_img,(i[0],i[1]),2,(0,0,255),3)

        input_img = cv2.cvtColor(input_img, cv2.COLOR_BGR2RGB)
        setattr(main_setup.image_plot, 'img', input_img)
        universal_params.data = data
        #setattr(main_setup.current_params, 'data', data)
        main_setup.image_plot.draw()


    def on_file_clicked(self, widget, *args):
        print('button working')
        dialog = main_setup.builder.get_object('file_chooser')
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            print("Open clicked")
            print("File selected: " + dialog.get_filename())
            file_selected = dialog.get_filename()
            file_img = mpimg.imread(file_selected)
            setattr(main_setup.image_plot, 'image', file_selected)
            setattr(main_setup.image_plot, 'img', file_img)
            main_setup.image_plot.draw()
        elif response == Gtk.ResponseType.CANCEL:
            print("Cancel clicked")
        dialog.hide()

    def update_listbox():
        for i in main_setup.run_list:
            if i not in main_setup.listbox_contents:
                label = Gtk.Label()
                label.set_text(f'run {main_setup.run_list.index(i)}')
                main_setup.scan_listbox.add(label)
                main_setup.listbox_contents.append(i)
                main_setup.scan_listbox.show_all()


    def on_remove(self, *args):
        index = main_setup.selected_row
        print(index)
        del main_setup.listbox_contents[index]
        del main_setup.run_list[index]
        active_row_object = main_setup.scan_listbox.get_selected_row()
        main_setup.scan_listbox.remove(active_row_object)


    def on_add(*args):
        number = len(main_setup.run_list)+1
        main_setup.run_list.append(hough_params())
        Handler.update_listbox()

    def on_row_selected(self, listbox_widget, row, *args):
        try:
            index = row.get_index()
            main_setup.current_params = main_setup.run_list[index]
            main_setup.selected_row = index

            adjustment1 = main_setup.builder.get_object('adjustment1')
            adjustment1.set_value(main_setup.run_list[index].blur)
            adjustment2 = main_setup.builder.get_object('adjustment2')
            adjustment2.set_value(main_setup.run_list[index].min_dist)
            adjustment3 = main_setup.builder.get_object('adjustment3')
            adjustment3.set_value(main_setup.run_list[index].canny_detection)
            adjustment4 = main_setup.builder.get_object('adjustment4')
            adjustment4.set_value(main_setup.run_list[index].hough_threshold)
            adjustment5 = main_setup.builder.get_object('adjustment5')
            adjustment5.set_value(main_setup.run_list[index].min_radius)
            adjustment6 = main_setup.builder.get_object('adjustment6')
            adjustment6.set_value(main_setup.run_list[index].max_radius)
            Handler.updatezoom()

        except:
            main_setup.current_params = main_setup.run_list[0]





class main_setup:


    run1 = hough_params()
    run_list = [run1]
    current_params = run_list[0]
    builder = Gtk.Builder()
    preview_position = [500,500]
    builder.add_from_file("tool_layout.glade")
    builder.connect_signals(Handler())
    window = builder.get_object("main_window")
    viewpane = builder.get_object("viewpane")

    scan_listbox = builder.get_object('scan_listbox')
    selected_row = None
    listbox_contents = []

    image_plot = DrawGraph()
    viewpane.pack_start(image_plot.canvas, True, True, 0)
    image_plot.canvas.mpl_connect('button_press_event', Handler.updatezoomonclick)
    zoom_preview = builder.get_object("zoom_preview")
    zoom_preview.add(image_plot.zoomcanvas)

    toolbar = NavigationToolbar(image_plot.canvas, window)
    plotbuttons = builder.get_object('plotbuttons')
    plotbuttons.add(toolbar)

    window.show_all()


class data_window:


        treeview = main_setup.builder.get_object('treeview')
        data_table = main_setup.builder.get_object('data_table')
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)




        for i, column_title in enumerate (['x', 'y', 'radius']):
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(column_title, renderer, text= i)
            treeview.append_column(column)
            treeview.columns_autosize()

class histogram_window:

            histogram = main_setup.builder.get_object('histogram')
            box = main_setup.builder.get_object('histogram_container')
            hist_plot = DrawHistogram()
            box.pack_start(hist_plot.canvas, True, True, 0)











main_setup()
Handler.update_listbox()
Gtk.main()
