import os
# Import other scripts
import GUI
import Dataset
# Import libraries used
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import PySimpleGUI as sg
from pandas.api.types import is_numeric_dtype

def uploadData(data):
    '''
    Function that reads a csv file, creates a dataframe and Dataset instance and return both
    
    Arguments:
            data (str) - string of data location on local file system
            
    Returns:
            df_initial (pd.DataFrame) - original/unchanged dataframe
            
            df (Dataset.Dataset) - instance of Dataset class
    '''
    # Read CSV
    csv = pd.read_csv(data)
    # Save a copy of dataframe
    df_initial = pd.DataFrame(csv)
    # Create Dataset object
    df = Dataset.Dataset(pd.DataFrame(csv))
    
    return df_initial, df

def viewData(df):
    '''
    Function that creates a new window to display uploaded data
    
    Arguments:
            df (Dataset.Dataset) - instance of Dataset that is used to display data
            
    Returns:
            None
    '''
    column_names = []
    answer = sg.popup_yes_no('Does the dataset have column names?')
    data = df.data.values.tolist()

    if answer == 'Yes': # Display data
    
        column_names = list(df.data.columns)
        data = df.data.iloc[1:].values.tolist()
    
    if answer == 'No': # Create generic column names
        column_names = ['columns' + str(i) for i in range(len(data[0]))]
    
    # Layout of gui window
    layout = [
        [sg.Table(values = data, headings = column_names, display_row_numbers = True,
              auto_size_columns = True, justification = 'right', num_rows = min(40, len(data)),
              vertical_scroll_only = False)]
    ]
    
    window = sg.Window('Data', layout, grab_anywhere = False, resizable = True)
    event, values = window.read()
    window.close()
    
def dataframe_type(dataframe):
    '''
    Function that determines whether data is all numeric or mixed
    
    Arguments:
            dataframe (Dataset.Dataset) - instance of Dataset that is used to get values
            
    Returns:
            bool - True for numeric data, False for mixed data
    '''
    column_types = list(dataframe.data.apply(lambda col: pd.to_numeric(col, errors = 'coerce').notnull().all()))
    if False in column_types:
        return False
    else :
        return True
    
def enable_buttons(event, isNumerical = False, uploaded = False):
    '''
    Function that enables buttons based on event
    
    Arguments:
            event (str) - name of the event in event loop
            
            isNumerical (bool) - boolean that indicates whether data is numerical
            
            uploaded (bool) - boolean that indicates whether data is uploaded
            
    Returns:
            None
    '''
    # Check which dim. red. frame to enable for parameter input
    if event == 'Apply':
        buttons = ['-SAVEDATA-', '-SAVEGRAPH-']
        for button in buttons:
            gui.window[button].update(disabled=False)  
        
    if event == 'Upload':
        if isNumerical:
            buttons = ['-NUMOFVARPCA-', '-APPLY-', '-VIEWDATA-']
            for button in buttons:
                gui.window[button].update(disabled=False)
             
            buttons = ['-NUMOFVARFA-']
            for button in buttons:
                gui.window[button].update(disabled=True)
                
        else:
            buttons = ['-NUMOFVARFA-', '-APPLY-', '-VIEWDATA-']
            for button in buttons:
                gui.window[button].update(disabled=False)
             
            buttons = ['-NUMOFVARPCA-']
            for button in buttons:
                gui.window[button].update(disabled=True)
            
def disable_buttons(event):
    '''
    Function that disables buttons based on event
    
    Arguments:
            event (str) - name of the event in event loop
            
    Returns:
            None
    '''
    if event == 'Apply':
       buttons = ['-APPLY-', '-NUMOFVARPCA-', '-NUMOFVARFA-']
       for button in buttons:
           gui.window[button].update(disabled=True) 
           
    if event == 'Upload':
       buttons = ['-SAVEGRAPH-', '-SAVEDATA-']
       for button in buttons:
           gui.window[button].update(disabled=True)  
                    
def draw_figure(canvas, figure):
    '''
    Function that binds canvas and graph and draws it
    
    Arguments:
            canvas (PySimpleGui.Canvas) - canvas for drawing graph
            
            figure (matplotlib.Figure) - graph that is drawn on canvas
    Returns:
            figure_canvas_agg - binded object of graph and canvas
    '''
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg

def delete_figure_agg(figure_agg):
    '''
    Function that deletes graph from canvas
    
    Arguments:
            figure_agg - binded graph and canvas
            
    Returns:
            None
    '''
    figure_agg.get_tk_widget().forget()

def select_sort(columns):
    '''
    Function that returns the value selected in list box (graph_setings)
    
    Arguments:
            columns (list) - list of original data column names
            
    Returns:
            value (str) - name of selected column
    '''
    col_names = columns
    value = sg.popup(sg.Listbox(values = (col_names[0], col_names[1]), select_mode = 'single'))
    
    return value
    
    
def main():
    # Make variables global and initialize them
    global gui
    global factor_variance
    global df_initial
    global ax
    global figure_agg
    global isNumerical
    
    gui = GUI.Gui()
    folder = ''
    name = ''
    factor_variance = None
    df_initial = None
    df = None
    ax = None
    figure_agg = None
    
    # Dataset type flag
    isNumerical = False
    
    while True: # Event Loop
        event, values = gui.window.read()
        
         # Exit GUI
        if event == "-EXIT-" or event == sg.WIN_CLOSED:
            gui.window.close()
            break
        
        # Import dataset
        if event == '-UPLOADDATA-':
            try:
                # Upload data and initialize Dataset object
                df_initial, df = uploadData(values['-UPLOADDATA-'])
                # Display name of uplaoded file
                gui.window['-FILEUPLOADTEXT-'].update(str(os.path.basename(values['-UPLOADDATA-'])) + ' uploaded')
                # Determine if dataset is numerical
                isNumerical = dataframe_type(df)
                # Enable/disable buttons
                enable_buttons('Upload', isNumerical, True)
                disable_buttons('Upload')
                # If graph is displayed, delete it
                if figure_agg is not None:
                    delete_figure_agg(figure_agg)
    
                gui.window['-LISTBOX-'].update(values = [])
                gui.window['-VARTEXT-'].update('')
            except:
                sg.popup_error('An Exception Occured. Could NOT upload dataset\n')
                gui.window.close()
                
        # Display data on GUI
        if event == '-VIEWDATA-':
            viewData(df)
            
        if event == '-APPLY-':
            try:
                # Disable/enable buttons
                disable_buttons('Apply')
                enable_buttons('Apply')
                
                # Perform PCA and visualize graph is 2 components
                if isNumerical: #check if numerical
                    variance = df.reduce_PCA(int(values['-NUMOFVARPCA-']))
                    # Display total explained variance
                    gui.window['-VARTEXT-'].update('Explained Variance: {}%'.format(str(variance)))
                    
                    if int(values['-NUMOFVARPCA-']) == 2: # Check if 2 components
                        columns = df_initial.columns
                        gui.window['-LISTBOX-'].update(values = columns, disabled = False)
                        # Create and draw raw graph
                        ax = df.graph()
                        figure_agg = draw_figure(gui.window['-CANVAS-'].TKCanvas, ax)
                    else:
                        # Display no graph text
                        gui.window['-NOGRAPHTEXT-'].update('No Graph Available (more than 2 dimensions selected)')
                        gui.window['-SAVEGRAPH-'].update(disabled = True)
                        
                # Perform FAMD    
                else:
                    factor_variance, variance = df.reduce_FA(int(values['-NUMOFVARFA-']))
                    gui.window['-VARTEXT-'].update('Explained Variance: {}%'.format(str(variance)))
                    
                    if int(values['-NUMOFVARFA-']) == 2: # Check if 2 components
                        columns = df_initial.columns
                        gui.window['-LISTBOX-'].update(values = columns, disabled = False)
                        # Create and draw graph
                        ax = df.graph(variance = factor_variance)
                        figure_agg = draw_figure(gui.window['-CANVAS-'].TKCanvas, ax)
                    else:
                        gui.window['-NOGRAPHTEXT-'].update('No Graph Available (more than 2 dimensions selected)')
                        gui.window['-SAVEGRAPH-'].update(disabled = True)
            except:
                    sg.popup_error('An Exception Occured. Could NOT reduce dimensions\n')
                    gui.window.close()  
        
        # Sort graph by color    
        if event == '-LISTBOX-':
            # Delete current graph
            delete_figure_agg(figure_agg)
            
            # Color data by selected column and display it
            if is_numeric_dtype(df_initial[values['-LISTBOX-'][0]]):
                ax = df.graph(color_by = df_initial[values['-LISTBOX-'][0]], variance = factor_variance)
                figure_agg = draw_figure(gui.window['-CANVAS-'].TKCanvas, ax)
            else:
                sg.popup('Could not color data by; {}'.format(values['-LISTBOX-'][0]))
                
        if event == '-SAVEDATA-':
            # Allow user to choose directory
            folder = sg.popup_get_folder(message='Choose a folder:',
                                                  title='Directory Browser')
            if folder != None and folder != '':
                # Allow user to enter the name of dataset
                name = sg.popup_get_text('Enter name of file (Example: NewData)')
                
                if name != None and name !='':
                    if os.path.isdir(folder):
                        df.save_data(folder, name)
                        #Check if saved successfully
                        if os.path.isfile(folder + '/' + name + '.csv'):
                            sg.popup('File ' + name + '.csv saved successfully')
                        else:
                            sg.popup('File ' + name + '.csv could not be saved')
                    else:
                        sg.popup('Directory ' + folder + ' does not exist')
                    
            folder = ''
            name = '' 
                
        if event == '-SAVEGRAPH-':
            # Allow user to choose directory
            folder = sg.popup_get_folder(message='Choose a folder:',
                                                  title='Directory Browser')
            if folder != None and folder != '':
                # Allow user to enter the name of dataset
                name = sg.popup_get_text('Enter name of graph (Example: Figure)')
            
                if name != None and name !='':
                    if os.path.isdir(folder):
                        #Check if saved successfully
                        ax.savefig(folder + '/' + name + '.png')
                        if os.path.isfile(folder + '/' + name + '.png'):
                            sg.popup('Graph ' + name + '.png saved successfully')
                        else:
                            sg.popup('Graph ' + name + '.png could not be saved')
                    else:
                        sg.popup('Directory ' + folder + ' does not exist')
                    
            folder = ''
            name = ''
        
main()
