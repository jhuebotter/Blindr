#!/usr/bin/python

# this script consits of helper functions to create logging and html output

import logging
from sys import stderr

def global_log(name, fname='global.log',active=True):

    # this function initializes the logger used by all blindr components and writes to the specified log output file

    logger = logging.getLogger(name);                                                                               
    logger.setLevel(logging.DEBUG)  
    if active == False:                                                                   
        logger.disabled = True
    else:
        fhan = logging.FileHandler(fname)                                                                               
        fhan.setLevel(logging.DEBUG)                                                                                    
        logger.addHandler(fhan)                                                                                         
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')                           
        fhan.setFormatter(formatter)
        sh = logging.StreamHandler(stderr)
        sh.setLevel(logging.DEBUG)
        sh.setFormatter(formatter)
        logger.addHandler(sh)
        
    return logger


def init_html(html,output_dir,file,n_groups):

    # this function initializes the html output file and writes the header

    f = open(html,'w')
    msg = '''
    <html>
        <head>
            <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.1/css/bootstrap.min.css">
            <style>
               body{ margin:0 100; background:whitesmoke; }
                table {
                  font-family: arial, sans-serif;
                  border-collapse: collapse;
                  width: 30%;
                }

                td, th {
                  border: 1px solid #dddddd;
                  text-align: center;
                  padding: 8px;
                }

                tr:nth-child(even) {
                  background-color: #dddddd;
                }
            </style>
        </head>
        <body>
            <h1>Blindr.py output</h1>
            <p>Input file: ''' + file + '''</p>
            <p>Output dicectory: ''' + output_dir + '''</p>
            <p>Experimental groups to be created: ''' + str(n_groups) + '''</p>
    '''
    #            <p>Output dicectory:  <a href="file://''' + output_dir + '''">''' + output_dir + '''</a> </p>

    f.write(msg)
    f.close()


def table_to_html(html, table, title=None):

    # this function is used to add tables to the html output file

    f = open(html,'a')
    if title:
        msg = '''
            <h3>''' + title + '''</h3>
        '''
        f.write(msg)
    
    # format example of the passed table:

    '''
        <table border="1" class="dataframe">
          <thead>
            <tr style="text-align: right;">
              <th></th>
              <th>foo1</th>
              <th>foo2</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <th>0</th>
              <td>-0.223430</td>
              <td>-0.904465</td>
            </tr>
            <tr>
              <th>1</th>
              <td>0.317316</td>
              <td>1.321537</td>
            </tr>
          </tbody>
        </table>
    '''
    f.write(table)
    f.write('<br><br>')
    f.close()


def write_to_html(html, text):

    # this function is used to write text to the html output file

    f = open(html,'a')
    text = text.replace(' ', '&ensp;')
    msg = '''
            <p>''' + text + '''</p>
    '''
    f.write(msg)
    f.close()


def topic_to_html(html, text):

    # this function is used to write headings to the html output file

    f = open(html,'a')
    text = text.replace(' ', '&ensp;')
    msg = '''
            <h3>''' + text + '''</h3>
    '''
    f.write(msg)
    f.close()


def plot_to_html(html, path, name, title='TITLE'):

    # this function is used to insert plots into the html output file

    f = open(html,'a')
    msg = '''
            <!-- *** Section 1 *** --->
            <h3>''' + title + '''</h3>
            <iframe width="100%%" height="380" frameborder="0" seamless="seamless" scrolling="no" \
    src="''' + name + '''"></iframe>
            <p>Plot available under ''' + path+name + '''</p>
    '''
    f.write(msg)
    f.close()


def finish_html(html):

    # this function finalizes the html output file

    f = open(html,'a')
    msg = '''       
    </body>
    </html>'''
    f.write(msg)
    f.close()
