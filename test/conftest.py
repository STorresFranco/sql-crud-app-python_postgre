#%%
'''
In this file we have to configure the root directory so that our files can communicate
'''
import sys
import os

project_root=os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))

print(f"Project path {project_root}") #Just to be sure

sys.path.insert(0,project_root)
