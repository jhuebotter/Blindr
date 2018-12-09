#!/usr/bin/python

import logging
from sys import stderr

def global_log(name, fname='global.log',active=True):
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


def init_html(html,file,n_groups):
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
            <p>Experimental groups to be created: ''' + str(n_groups) + '''</p>
    '''
    f.write(msg)
    f.close()


def table_to_html(html, table, title=None):
    f = open(html,'a')
    if title:
        msg = '''
            <h3>''' + title + '''</h3>
        '''
        f.write(msg)

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
    f = open(html,'a')
    text = text.replace(' ', '&ensp;')
    msg = '''
            <p>''' + text + '''</p>
    '''
    f.write(msg)
    f.close()


def plot_to_html(html, name, title='TITLE'):
    f = open(html,'a')
    name = name.split('\\')[-1]
    msg = '''
            <!-- *** Section 1 *** --->
            <h3>''' + title + '''</h3>
            <iframe width="100%%" height="400" frameborder="0" seamless="seamless" scrolling="no" \
    src="''' + name + '''"></iframe>
    '''
    f.write(msg)
    f.close()


def finish_html(html):
    f = open(html,'a')
    msg = '''       
    </body>
    </html>'''
    f.write(msg)
    f.close()