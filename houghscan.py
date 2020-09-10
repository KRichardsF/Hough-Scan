import gi
from operation import tiles, hough_process
from plot_view import  DrawGraph, DrawHistogram
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk
import cv2
from matplotlib import pyplot as plt
import matplotlib.image as mpimg
import numpy as np
import threading
import json
from collections import namedtuple
#module inside matplotlib that allows us to use in gtk
from matplotlib.backends.backend_gtk3 import NavigationToolbar2GTK3 as NavigationToolbar

#setup variables for Hough analysis
class hough_params:
    def __init__(self, blur=5, min_dist=80, canny_detection=80, hough_threshold=50, min_radius=0, max_radius=0, tile_size=800, overlap=50, doubles_removal_distance=100):
        self.blur = blur
        self.min_dist = min_dist
        self.canny_detection = canny_detection
        self.hough_threshold = hough_threshold
        self.min_radius = min_radius
        self.max_radius = max_radius
        self.tile_size = tile_size
        self.overlap = overlap
        self.doubles_removal_distance = doubles_removal_distance

#Setup lists and tiling parameters
class universal_params:
        data = np.empty((0,3), int)
        liststore = Gtk.ListStore(int, int, int)
        tile_size = 800
        no_tiles_x = 12
        no_tiles_y = 10
        doubles_removal_distance = 100
        startup = True



class Handler:
    #
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
        #run function in plot_view to redraw the preview with new location using main setup paramters
        main_setup.image_plot.zoom(main_setup.preview_position[0],
                                        main_setup.preview_position[1],
                                        params=main_setup.current_params)
        print(main_setup.current_params)

    def updatezoomonclick(event):
        #reject anytoning other than left click from mous
         if event.button!=1: return
         if (event.xdata is None): return
         #set main_setups x and y positions
         main_setup.preview_position[0],main_setup.preview_position[1] = event.xdata, event.ydata
         #update preview using new x and y locations
         t1 = threading.Thread(target=Handler.updatezoom)
         t1.start()

    #general process when spinbutton updated (takes the value on spinbutton and name of paramter to change)
    def update_spinbuttons(button_value, parameter):
            print('button pressed')
            #checks current parameter value
            before = getattr(main_setup.current_params, parameter)
            #sets parameter as on spinbutton
            setattr(main_setup.current_params, parameter, button_value)
            #only if the paramter has changed update the preview
            if getattr(main_setup.current_params, parameter) != before:
                print('scan updated!')
                t1 = threading.Thread(target=Handler.updatezoom)
                t1.start()

    def add_button_pressed(self, *args):
        Handler.add_run(main_setup.run_list)
        Handler.update_scanlist(main_setup.scan_listbox, main_setup.run_list)

    #blur spinbox activate/button released signal
    def update_blur(self, entry, *args):
        #takes spinbox's entry object
        button_value = int(entry.get_text())
        #passes parameter name 'blur' to update_spinbuttons with value on spinbox
        Handler.update_spinbuttons(button_value, 'blur')

    #same process as above
    def update_min_dist(self, entry, *args):
        button_value = int(entry.get_text())
        Handler.update_spinbuttons(button_value, 'min_dist')

    #same process as above
    def update_canny_detection(self, entry, *args):
        button_value = int(entry.get_text())
        Handler.update_spinbuttons(button_value, 'canny_detection')

    #same process as above
    def update_hough_threshold(self, entry, *args):
        button_value = int(entry.get_text())
        Handler.update_spinbuttons(button_value, 'hough_threshold')

    #same process as above
    def update_min_radius(self, entry, *args):
        button_value = int(entry.get_text())
        Handler.update_spinbuttons(button_value, 'min_radius')

    #same process as above
    def update_max_radius(self, entry, *args):
        button_value = int(entry.get_text())
        Handler.update_spinbuttons(button_value, 'max_radius')

    def update_tile_size (self, entry, *args):
        button_value = int(entry.get_text())
        print('tile_size', button_value)
        setattr(main_setup.image_plot, 'tile_size', button_value)
        #Handler.update_spinbuttons(button_value, 'tile_size')
        setattr(main_setup.current_params, 'tile_size', button_value)

    def update_overlap (self, entry, *args):
        button_value = int(entry.get_text())
        print('overlap', button_value)
        #Handler.update_spinbuttons(button_value, 'no_tiles_x')
        setattr(main_setup.current_params, 'overlap', button_value)

    def update_doubles_removal (self, entry, *args):
        button_value = int(entry.get_text())
        print('doubles removal distance', button_value)
        #Handler.update_spinbuttons(button_value, 'doubles_removal_distance')
        setattr(main_setup.current_params, 'doubles_removal_distance', button_value)

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

    def run_button_pressed(self, *args):
        print('run button pressed')
        Handler.processing_display(True)
        t1 = threading.Thread(target= Handler.run_analysis)
        t1.start()


    def processing_display(active):
        processing_spinner = main_setup.builder.get_object("processing_spinner")
        run_button = main_setup.builder.get_object("run_button")
        #context = run_button.get_style_context()
        if active == True:
            #context.remove_class("suggested-action")
            run_button.set_label("Processing, Please Wait...")
            processing_spinner.start()

        else:
            #context.add_class("suggested-action")
            run_button.set_label("Run")
            processing_spinner.stop()

    def run_analysis():
        input_img = cv2.imread(main_setup.image_plot.image, 1)
        eb_img = cv2.cvtColor(input_img, cv2.COLOR_BGR2GRAY)

        data = np.empty((0,3), int)
        for i in main_setup.run_list:
            tile_array = tiles(eb_img, tile_size=i.tile_size,
                                        overlap=i.overlap)
            circles = tile_array.tile(hough_process.hough, blur= i.blur,
                                                            dp= 1,
                                                            min_dist= i.min_dist,
                                                            canny_upper= i.canny_detection,
                                                            hough_threshold= i.hough_threshold,
                                                            min_radius= i.min_radius,
                                                            max_radius= i.max_radius)

            data = np.append(data, circles, axis=0)
            data = tile_array.remove_doubles(data, separation= i.doubles_removal_distance)

            #np.append(data1, circles, axis=0)
        for i in data:
                cv2.circle(input_img,(i[0],i[1]),i[2],(0,255,0),2)
                cv2.circle(input_img,(i[0],i[1]),2,(0,0,255),3)

        input_img = cv2.cvtColor(input_img, cv2.COLOR_BGR2RGB)
        setattr(main_setup.image_plot, 'img', input_img)
        universal_params.data = data
        #setattr(main_setup.current_params, 'data', data)
        main_setup.image_plot.draw()
        Handler.processing_display(False)


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
                print(main_setup.run_list)


    def on_clear_listbox(*args):
        main_setup.listbox_contents = []
        main_setup.run_list = []
        active_row_objects = main_setup.scan_listbox.get_children()
        for i in active_row_objects:
            main_setup.scan_listbox.remove(i)

    def on_remove(self, *args):
        index = main_setup.selected_row
        print(index)
        del main_setup.listbox_contents[index-1]
        del main_setup.run_list[index-1]
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
            tile_size_entry = main_setup.builder.get_object('tile_size_entry')
            tile_size_entry.set_text(str(main_setup.run_list[index].tile_size))
            tile_overlap_entry = main_setup.builder.get_object('tile_overlap_entry')
            tile_overlap_entry.set_text(str(main_setup.run_list[index].overlap))
            doubles_removal_entry = main_setup.builder.get_object('doubles_removal_entry')
            doubles_removal_entry.set_text(str(main_setup.run_list[index].doubles_removal_distance))
            Handler.updatezoom()

        except:
            main_setup.current_params = main_setup.run_list[0]

    def on_exportjson_pressed(self, *args):
        filename = 'untitledjson'
        data = {}
        for i, j in enumerate(main_setup.run_list):
            print(i,j)
            data[f'run_{str(i)}'] = (j.__dict__)
        data['output_data'] = universal_params.data.tolist()
        print(data)
        
        dialog = main_setup.builder.get_object('save_chooser')

        response = dialog.run()
        if response == Gtk.ResponseType.NONE:
            name_entered = main_setup.builder.get_object('filename_entry')
            filename = name_entered.get_text()

            with open(f'{filename}.json','w') as outfile:
                json.dump(data, outfile)

        elif response == Gtk.ResponseType.CANCEL:
            print("Cancel clicked")
        dialog.hide()

    def jsondecoder(jsondict):
        return namedtuple('X', jsondict.keys())(*jsondict.values())

    def on_importjson_pressed(self, *args):
        print('button working')
        dialog = main_setup.builder.get_object('load_chooser')
        response = dialog.run()

        if response == Gtk.ResponseType.OK:

            print("File selected: " + dialog.get_filename())
            file_selected = dialog.get_filename()
            print(file_selected)
            with open(file_selected, mode='r', encoding='utf-8') as json_data:
                data = json.load(json_data)
                print (type(data))
                print(data.values())
                new_array = []
                for i in data:
                    j = (json.loads(data[i]))
                    obj = hough_params(blur=j['blur'],
                                        min_dist=j['min_dist'],
                                        canny_detection=j['canny_detection'],
                                        hough_threshold=j['hough_threshold'],
                                        min_radius=j['min_radius'],
                                        max_radius=j['max_radius'],
                                        tile_size=j['tile_size'],
                                        overlap=j['overlap'],
                                        doubles_removal_distance=j['doubles_removal_distance'])
                    new_array.append(obj)
            Handler.on_clear_listbox()
            main_setup.run_list = new_array
            Handler.update_listbox()

        elif response == Gtk.ResponseType.APPLY:
            print("Cancel clicked")
        dialog.hide()


class main_setup:
    #initial run variables
    run0 = hough_params()
    #generates list to add multiple runs
    run_list = [run0]
    #sets initial run to edit
    current_params = run_list[0]
    #sets initial preview location(before clicking)
    preview_position = [500,500]

    #builds interface from glade xml file
    builder = Gtk.Builder()
    builder.add_from_file("tool_layout.glade")
    #passes XML's signals to various handlers as described in XML
    builder.connect_signals(Handler())

    #gets the main window as object
    window = builder.get_object("main_window")
    #gets box which the matplotlib viewer will be placed in as object
    viewpane = builder.get_object("viewpane")
    #gets the listbox of different 'runs' as an object
    scan_listbox = builder.get_object('scan_listbox')
    #setup listbox inital contents
    selected_row = None
    listbox_contents = []

    context = window.get_style_context()
    color1 = context.get_background_color(Gtk.StateFlags.NORMAL)
    color1 = (color1.red,color1.blue,color1.green)
    print(type(color1))
    #DrawGraph function from plot_view.py creates an object with setup for main and preview matplotlib diagrams
    image_plot = DrawGraph(background_color=(color1))
    #adds the main diagram (canvas generated by the function above) to the box labelled vewpane
    viewpane.pack_start(image_plot.canvas, True, True, 0)
    #uses matplotlib event handling function to update preview when main diagram is clicked
    image_plot.canvas.mpl_connect('button_press_event', Handler.updatezoomonclick)
    #gets the preview box as object
    zoom_preview = builder.get_object("zoom_preview")
    #adds the preview diagram to the box
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
