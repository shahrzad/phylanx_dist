#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 25 12:03:39 2020

@author: shahrzad
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 21 12:43:56 2020

@author: shahrzad
"""

import csv
import glob
import numpy as np
import matplotlib.pyplot as plt

def read_files(dirs, mode='config'):
    data_files=[]
    for directory in dirs:
        [data_files.append(data_file) for data_file in glob.glob(directory+'/*.dat')]
        
    configs=[]
    results={}
    
    for filename in data_files:
        (node, run_type, batch, length, k_out, k_length, num_nodes) = filename.split('/')[-1].replace('.dat','').split('_')    
        num_nodes=int(num_nodes)
        f=open(filename, 'r')
        data=f.readlines()
        if len(data)>0:
            if run_type=='pytorch':
                d_time=[float(data[0].replace('\n',''))]
                d_size=data[1].split('[')[1].split('])\n')[0].replace(' ','')
            else:
                d_time=[float(d.split(': ')[1].split('\n')[0]) for d in data if ':' in d]        
                if run_type=='physl' and len(data)>num_nodes:
                    d_size=data[-1].split('(')[1].split(')\n')[0].replace(' ','')
                    (node, run_type, batch, length, k_length, k_out, num_nodes) = filename.split('/')[-1].replace('.dat','').split('_')                    
                elif run_type=='impl':
                    d_size=data[-1].split('[')[1].split(']\n')[0].replace(' ','')
                elif run_type=='cpp':
                    d_size=data[-1].split('(')[1].split(')\n')[0].replace(' ','')
                    (node, run_type, batch, length, k_length, k_out, num_nodes) = filename.split('/')[-1].replace('.dat','').split('_')                                
                else:
                    d_size=""
                           
#            if mode == 'run_type':
#                if node not in results.keys():
#                    results[node]={}
#                if num_nodes not in results[node].keys():
#                    results[node][num_nodes]={}
#                if run_type not in results[node][num_nodes].keys():
#                    results[node][num_nodes][run_type]={}
#                config=batch+'-'+length+'-'+k_out+'-'+k_length
#                if config not in results[node][num_nodes][run_type][config].keys():
#                    results[node][num_nodes][run_type][config]={'time':max(d_time), 'size':d_size}
#                    configs.append(config)
#            else:      
            if node not in results.keys():
                results[node]={}
            if num_nodes not in results[node].keys():
                results[node][num_nodes]={}
            config=batch+'-'+length+'-'+k_out+'-'+k_length
            if config not in results[node][num_nodes].keys():
                results[node][num_nodes][config]={}
                configs.append(config)
            if run_type not in results[node][num_nodes][config].keys():
                results[node][num_nodes][config][run_type]={'time':max(d_time), 'size':d_size}
    return results

#comparison of different runs pytorch and physl            
def plot_all(results, plot_dir='/home/shahrzad/repos/phylanx_dist/plots'):
    j=1
    for node in results.keys():     
        for no in results[node].keys():
            run_types=['instrumented','pytorch']
            all_results=[]
            plt.figure(j)
            plt.axes([0, 0, 2, 1])
            for config in results[node][no].keys():
                rs=[]
                for run_type in run_types:
                    if run_type in results[node][no][config].keys():
                        rs.append(results[node][no][config][run_type]['time'])
                    else:
                        rs.append(0)
                    all_results.append(rs)            
                    
            for run_type in run_types:     
                results_r=[all_results[i][run_types.index(run_type)] for i in range(len(all_results)) if all_results[i][run_types.index(run_type)]!=0]
                plt.scatter([i for i in range(len(results_r))], results_r,marker='.',label=run_type)
           
            plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
            plt.title("run on "+node+" on "+str(no)+" nodes")
            plt.savefig(plot_dir+'/all_configs/'+node+'_'+str(no)+'.png',bbox_inches='tight')
            plt.close()
            j=j+1


#comparison of different runs different nodes   
def plot_num_nodes(results, plot_dir='/home/shahrzad/repos/phylanx_dist/plots',mode='speedup'):
    j=1
    for node in results.keys():    
        run_types=['cpp','impl','pytorch']
        num_nodes=[k for k in results[node].keys()]
        num_nodes.sort()
        configs=[k for k in results[node][1].keys()]
        configs.sort()
        
        for config in configs:
            plt.figure(j)                 
            for run_type in run_types:    
                all_ks=[k for k in num_nodes if k in results[node].keys() and config in results[node][k] and run_type in results[node][k][config] and run_type in results[node][1][config]]
                if mode=='speedup':
                    plt.scatter(all_ks, [results[node][1][config][run_type]['time']/results[node][k][config][run_type]['time'] for k in all_ks], marker='.', label=run_type)
                    plt.ylabel('speed-up')
                else:
                    plt.scatter(all_ks, [results[node][k][config][run_type]['time'] for k in all_ks], marker='.', label=run_type)
                    plt.ylabel('time')

                          
            plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
            plt.title("run on "+node+" "+config)
            plt.xlabel('num_nodes')
            plt.savefig(plot_dir+'/based_on_num_nodes/'+mode+'/'+node+'_'+config+'.png',bbox_inches='tight')
            plt.close()
            j=j+1
                
        
#effect of batch size   
def plot_batch(results, plot_dir='/home/shahrzad/repos/phylanx_dist/plots'):
    j=1
    run_types=['cpp','impl','pytorch']

    for node in results.keys():    
        num_nodes=[k for k in results[node].keys()]
        num_nodes=[1]
        configs=[k for k in results[node][1].keys()]
        num_nodes.sort()
        configs.sort()
        
        not_batches=list(set(['-'.join([config.split('-')[i] for i in range(len(config.split('-'))) if i!=0]) for config in configs]))
        not_batches.sort()
        
        for nbatch in not_batches:        
            for no in num_nodes:
                p1_batches=[c for c in results[node][no].keys() if c.endswith('-'+nbatch)]
                if len(p1_batches)>0:
                    p1_batches=sorted(p1_batches, key=lambda x: int("".join([i for i in x if i.isdigit()])))
        
                    plt.figure(j)                 
                    for run_type in run_types: 
                        p1s=[p1 for p1 in p1_batches if run_type in results[node][no][p1].keys()]
                        if len(p1s)>0:
                            plt.scatter([p1.split('-')[0] for p1 in p1s],[results[node][no][p1][run_type]['time'] for p1 in p1s], marker='.', label=run_type)                                                  
                            plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
                    plt.title("run on "+node+" on "+str(no)+" nodes "+nbatch)
                    plt.xlabel('batch size')
                    plt.ylabel('time')
                    plt.savefig(plot_dir+'/based_on_batches/'+node+'_'+str(no)+'_'+nbatch+'.png',bbox_inches='tight')
                    plt.close()
                    j=j+1
                
            
#effect of batch length    
def plot_length(results, plot_dir='/home/shahrzad/repos/phylanx_dist/plots'):                    
    j=1
    for node in results.keys():    
        run_types=['instrumented','pytorch']
        num_nodes=[k for k in results[node].keys()]
        configs=[k for k in results[node][1].keys()]
        num_nodes.sort()
        configs.sort()
        
        not_batches=list(set(['-'.join([config.split('-')[i] for i in range(len(config.split('-'))) if i!=1]) for config in configs]))
        not_batches.sort()
    
        for nbatch in not_batches:        
            for no in num_nodes:
                p1_batches=[c for c in results[node][no].keys() if '-'.join([c.split('-')[i] for i in range(len(c.split('-'))) if i!=1])==nbatch]
                if len(p1_batches)>0:
                    p1_batches=sorted(p1_batches, key=lambda x: int("".join([i for i in x if i.isdigit()])))
                    
                    plt.figure(j)                 
                    for run_type in run_types:            
                        plt.scatter([p1.split('-')[1] for p1 in p1_batches if run_type in results[node][no][p1].keys()],[results[node][no][p1][run_type]['time'] for p1 in p1_batches if run_type in results[node][no][p1].keys()], marker='.', label=run_type)
                                                    
                    plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
                    plt.title("run on "+node+" on "+str(no)+" nodes "+nbatch)
                    plt.xlabel('length')
                    plt.ylabel('time')
                    plt.savefig(plot_dir+'/based_on_length/'+node+'_'+str(no)+'_'+nbatch+'.png',bbox_inches='tight')
                    plt.close()
                    j=j+1
                    
            
#effect of filter length   
def plot_f_length(results, plot_dir='/home/shahrzad/repos/phylanx_dist/plots'):
    j=1
    for node in results.keys():    
        run_types=['instrumented','pytorch']
        num_nodes=[k for k in results[node].keys()]
        configs=[k for k in results[node][1].keys()]
        num_nodes.sort()
        configs.sort()
        
        not_batches=list(set(['-'.join([config.split('-')[i] for i in range(len(config.split('-'))) if i!=2]) for config in configs]))
    
        for nbatch in not_batches:        
            for no in num_nodes:
                p1_batches=[c for c in results[node][no].keys() if '-'.join([c.split('-')[i] for i in range(len(c.split('-'))) if i!=2])==nbatch]
                if len(p1_batches)>0:
                    p1_batches=sorted(p1_batches, key=lambda x: int("".join([i for i in x if i.isdigit()])))
              
                    plt.figure(j)                 
                    for run_type in run_types:            
                        plt.scatter([p1.split('-')[2] for p1 in p1_batches if run_type in results[node][no][p1].keys()],[results[node][no][p1][run_type]['time'] for p1 in p1_batches if run_type in results[node][no][p1].keys()], marker='.', label=run_type)
                                                    
                    plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
                    plt.title("run on "+node+" on "+str(no)+" nodes "+nbatch)
                    plt.xlabel('filter_length')
                    plt.ylabel('time')
                    plt.close()
                    plt.savefig(plot_dir+'/based_on_filter_length/'+node+'_'+str(no)+'_'+nbatch+'.png',bbox_inches='tight')
        
                    j=j+1
                
            
#effect of batch filter_out   
def plot_f_out(results, plot_dir='/home/shahrzad/repos/phylanx_dist/plots'):
    j=1
    for node in results.keys():    
        run_types=['instrumented','pytorch']
        num_nodes=[k for k in results[node].keys()]
        configs=[k for k in results[node][1].keys()]
        num_nodes.sort()
        configs.sort()
        
        not_batches=list(set(['-'.join([config.split('-')[i] for i in range(len(config.split('-'))) if i!=3]) for config in configs]))
    
        for nbatch in not_batches:        
            for no in num_nodes:
                p1_batches=[c for c in results[node][no].keys() if '-'.join([c.split('-')[i] for i in range(len(c.split('-'))) if i!=3])==nbatch]
                if len(p1_batches)>0:
                    p1_batches=sorted(p1_batches, key=lambda x: int("".join([i for i in x if i.isdigit()])))
    
                    plt.figure(j)                 
                    for run_type in run_types:            
                        plt.scatter([p1.split('-')[3] for p1 in p1_batches if run_type in results[node][no][p1].keys()],[results[node][no][p1][run_type]['time'] for p1 in p1_batches if run_type in results[node][no][p1].keys()], marker='.', label=run_type)
                                                    
                    plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
                    plt.title("run on "+node+" on "+str(no)+" nodes "+nbatch)
                    plt.xlabel('out_channel')
                    plt.ylabel('time')
                    plt.savefig(plot_dir+'/based_on_out_channel/'+node+'_'+str(no)+'_'+nbatch+'.png',bbox_inches='tight')
                    plt.close()
                    j=j+1
                    
                    
def read_one_node(dirs):
    one_dir='/home/shahrzad/repos/phylanx_dist/data/results_one_node/'

    data_files=[]
    for directory in dirs:
        [data_files.append(data_file) for data_file in glob.glob(one_dir+directory+'/*.dat')]
        
    configs=[]
    results={}
    
    for filename in data_files:
        (node, run_type, batch, length, k_length, k_out, num_nodes, num_cores) = filename.split('/')[-1].replace('.dat','').split('_')    
        num_nodes=int(num_nodes)
        num_cores=int(num_cores)
        f=open(filename, 'r')
        data=f.readlines()
        if len(data)>0:
            if run_type=='pytorch':
                d_time=[float(data[0].replace('\n',''))]
                d_size=data[1].split('[')[1].split('])\n')[0].replace(' ','')
            else:
                d_time=[float(d.split(': ')[1].split('\n')[0]) for d in data if ':' in d]        
                if run_type=='physl' and len(data)>num_nodes:
                    d_size=data[-1].split('(')[1].split(')\n')[0].replace(' ','')
                    (node, run_type, batch, length, k_length, k_out, num_nodes) = filename.split('/')[-1].replace('.dat','').split('_')                    
                elif run_type=='impl':
                    d_size=data[-1].split('[')[1].split(']\n')[0].replace(' ','')
                elif run_type=='cpp':
                    d_size=data[-1].split('(')[1].split(')\n')[0].replace(' ','')
                    (node, run_type, batch, length, k_length, k_out, num_nodes) = filename.split('/')[-1].replace('.dat','').split('_')                                
                else:
                    d_size=""           
                            
            if node not in results.keys():
                results[node]={}
            if num_nodes not in results[node].keys():
                results[node][num_nodes]={}
            config=batch+'-'+length+'-'+k_length+'-'+k_out
            if config not in results[node][num_nodes].keys():
                results[node][num_nodes][config]={}
                configs.append(config)
            if run_type not in results[node][num_nodes][config].keys():
                results[node][num_nodes][config][run_type]={}
            if num_cores not in results[node][num_nodes][config][run_type].keys():
                results[node][num_nodes][config][run_type][num_cores]={'time':max(d_time), 'size':d_size}
    return results

def plot_one_node_speedup(results_one_node, plot_dir='/home/shahrzad/repos/phylanx_dist/plots',run_types=['cpp','impl','pytorch']):
    j=1
    for node in results_one_node.keys():    
        num_nodes=[k for k in results_one_node[node].keys()]
        num_nodes.sort()
        configs=[k for k in results_one_node[node][1].keys()]
        configs.sort()
        
        for config in configs:
            plt.figure(j)                 
            for run_type in [run_type for run_type in run_types if run_type in results_one_node[node][1][config].keys()]:                   
                num_cores=[k for k in results_one_node[node][1][config][run_type].keys() if config in results_one_node[node][1] and run_type in results_one_node[node][1][config]]
                num_cores.sort()
                plt.scatter(num_cores, [results_one_node[node][1][config][run_type][1]['time']/results_one_node[node][1][config][run_type][k]['time'] for k in num_cores], marker='.', label=run_type)
                          
            plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
            plt.title("run on "+node+" 1 node "+config)
            plt.xlabel('num_cores')
            plt.ylabel('speed-up')
            plt.savefig(plot_dir+'/one_node/'+node+'_'+config+'_speedup.png',bbox_inches='tight')
            plt.close()
            j=j+1

def plot_one_node_time(results_one_node, plot_dir='/home/shahrzad/repos/phylanx_dist/plots', run_types=['cpp','instrumented','impl','pytorch']):
    j=1
    for node in results_one_node.keys():            
        num_nodes=[k for k in results_one_node[node].keys()]
        num_nodes.sort()
        configs=[k for k in results_one_node[node][1].keys()]
        configs.sort()
        
        for config in configs:
            plt.figure(j)                 
            for run_type in [run_type for run_type in run_types if run_type in results_one_node[node][1][config].keys()]:                   
                num_cores=[k for k in results_one_node[node][1][config][run_type].keys() if config in results_one_node[node][1] and run_type in results_one_node[node][1][config]]
                num_cores.sort()
                plt.scatter(num_cores, [results_one_node[node][1][config][run_type][k]['time'] for k in num_cores], marker='.', label=run_type)
                          
            plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
            plt.title("run on "+node+" 1 node "+config)
            plt.xlabel('num_cores')
            plt.ylabel('time')
            plt.savefig(plot_dir+'/one_node/'+node+'_'+config+'_time.png',bbox_inches='tight')
            plt.close()
            j=j+1


def validate_output_size(results):
    for node in results.keys():
        for num_nodes in results[node].keys():
            for config in results[node][num_nodes].keys():                
                if 'impl' in results[node][num_nodes][config].keys() and 'pytorch' in results[node][num_nodes][config].keys():
                    size_impl=results[node][num_nodes][config]['impl']['size']
                    size_pytorch=results[node][num_nodes][config]['pytorch']['size']
                    if size_impl != size_pytorch:
                        print("error", config, node)
                        print("impl", size_impl)
                        print("pytorch", size_pytorch)
