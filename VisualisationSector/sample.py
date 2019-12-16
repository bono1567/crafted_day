from bokeh.io import show
from bokeh.plotting import figure
from bokeh.models import CheckboxGroup, CustomJS
from bokeh.layouts import gridplot
import numpy as np

figlist = [figure(title='Figure '+str(i),plot_width=200,plot_height=200) for i in range(6)]

x=np.arange(10)

linelist=[]
for fig in figlist:
    line0 = fig.line(x,x,color='blue')
    line1 = fig.line(x,x[::-1],color='red')
    line2 = fig.line(x,x**2,color='green')

    linelist+=[[line0,line1,line2]]
print(np.shape(linelist))
checkbox = CheckboxGroup(labels=['line0', 'line1', 'line2'], active=[0,1,2])

iterable = [elem for part in [[('_'.join(['line',str(figid),str(lineid)]),line) for lineid,line in enumerate(elem)] for figid,elem in enumerate(linelist)] for elem in part]
checkbox_code = '\n'.join([elem[0]+'.visible=checkbox.active.includes('+elem[0].split('_')[-1]+');' for elem in iterable])
print(checkbox_code)
checkbox.callback = CustomJS(args={key:value for key,value in iterable+[('checkbox',checkbox)]}, code=checkbox_code)

grid = gridplot([figlist[:3]+[checkbox],figlist[3:]])

# show(grid)