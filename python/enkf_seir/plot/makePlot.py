# -*- coding: utf-8 -*-
"""
Based on plot.py Created on Sat Apr 11 09:29:20 2020
by rafaeljmoraes

Updated by Geir Naevdal and Xiaodong Luo
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import argparse

available_variables = [
        'dead',
        'hosp',
        'case',
        'susc',
        'recov',
        'infec',
        'expos',
        ]

available_observations = [
        'Observed deaths',
        'Observed hospitalized',
        None,
        None,
        None,
        None,
        None,
        ]

variable2observation = dict(zip(available_variables, available_observations))

variable_colors = [
        (0, 0, 1), 
        (0, 1, 0),
        (1, 0, 0),
        (1, 1, 0),
        (0, 0, 0),
        (0, 1, 1),
        (1, 0, 1),
        ]

variable_colors = dict(zip(available_variables, variable_colors))

        
def lighter(color, percent):
    '''assumes color is rgb between (0, 0, 0) and (1, 1, 1)'''
    color = np.array(color)
    white = np.array([1, 1, 1])
    vector = white-color
    return color + vector * percent
    
#def load(file_name, header, skipfooter):
#    data = pd.read_csv(
#            filepath_or_buffer=file_name, 
#            delim_whitespace=True, 
#            header=header, 
#            skipfooter=skipfooter)
#    
#    return data
        
def load_ensemble_from_tecplot_file(file_name):
    #TODO: the header footer lines are hardcoded 
    header=53
    skipfooter=33
    df = pd.read_csv(
        filepath_or_buffer=file_name, 
        delim_whitespace=True, 
        header=header, 
        #skipfooter=skipfooter,
        nrows=366 )
    time = df.iloc[:, 0]
    mean = df.iloc[:, 1]
    std_dev = df.iloc[:, 2]
    ensemble = df.iloc[:, 3:df.columns.size-1]
    
    return time, mean, std_dev, ensemble

def load_observed_data_from_tecplot_file(file_name):
    #TODO: the header footer lines are hardcoded 
    header=3
    skipfooter=0
    df =  pd.read_csv(
        filepath_or_buffer=file_name, 
        delim_whitespace=True, 
        header=header, 
        skipfooter=skipfooter )
    time = df.iloc[:, 1]
    obs_data = df.iloc[:, 2]
    std_dev = df.iloc[:, 3]
    
    return time, obs_data, std_dev
    
def plot_ensemble(time, mean, std_dev, ensemble, color, fading):
    r, c = ensemble.shape
    ensemble_color = lighter(color, fading)
    plt.plot(time, ensemble, color=ensemble_color)
    plt.plot(time, mean, color=color)
    plt.plot(time, mean+std_dev, color=color, linestyle='dashed')
    plt.plot(time, mean-std_dev, color=color, linestyle='dashed')
        
def plot_observed_data(time, observed_data, std_dev, color):
    plt.errorbar(
            time, 
            observed_data, 
            yerr=std_dev, 
            marker='o', 
            markerfacecolor=color, 
            color=color)
    
def plot_variable(data_source, variable, obs_file_name, obs_name):
    post_file_name  = data_source + variable + '_1.dat'
    prior_file_name = data_source + variable + '_0.dat'
    
    color = variable_colors[variable]
    
    # plot prior data first becasue, since it is more spread than the posterior
    # it won't be cover it
    time, mean, std_dev, ensemble = load_ensemble_from_tecplot_file(prior_file_name)
    prior_fading = 0.9
    print("Ploting prior for: ", variable)
    plot_ensemble(time, mean, std_dev, ensemble, color, prior_fading)
    
    time, mean, std_dev, ensemble = load_ensemble_from_tecplot_file(post_file_name)
    prior_fading = 0.6
    print("Ploting posterior for: ", variable)
    plot_ensemble(time, mean, std_dev, ensemble, color, prior_fading)
    
    # note: not all variables have observed data
    if (obs_name is not None):
        print("Ploting observation for: ", variable)
        if variable == "hosp":
            obs_file_fullname = obs_file_name + "H.dat"
        elif variable == "dead":
            obs_file_fullname = obs_file_name + "D.dat"
        
        time, observed_data, std_dev = load_observed_data_from_tecplot_file(obs_file_fullname)
        print(time)
        print(observed_data)
        print(std_dev)
        plot_observed_data(time, observed_data, std_dev, color)
    
    patch = mpatches.Patch(color=color, label=variable)
    plt.legend(handles=[patch])

def parse_arguments():
    parser = argparse.ArgumentParser(description='EnKF_seir input arguments')
    
    parser.add_argument(
            "--data_dir", 
            default=None, 
            type=str, 
            help="The directory where the EnKF tecplot files can be found",
            required=True)
    
    parser.add_argument(
            "--figs_out_dir", 
            default=None, 
            type=str, 
            help="The directory where the figures will be output",
            required=True)
    
    parser.add_argument(
            "--format", 
            default='png', 
            type=str, 
            help="The format the figures will be saved",
            required=False)
    
    parser.add_argument(
            "--show", 
            default='false', 
            type=str, 
            help="Wheter the plots should be shown in interactive sessions",
            choices=['true', 'false'],
            required=False)
    
    parser.add_argument(
            "--dpi", 
            default=1200, 
            type=int, 
            help="The resolution the figures will be saved.",
            required=False)
    
    parser.add_argument(
            "--variables", 
            default=available_variables, 
            nargs='+',
            help="The variables to be plot",
            required=False,
            choices=available_variables)
    
    args = parser.parse_args()
        
    return args.data_dir, args.variables, args.figs_out_dir, args.format, args.dpi, args.show
    
def save_figures(figs_out_dir, figures, format, dpi, show):
    for var, fig in figures.items():
        fig.savefig(figs_out_dir + var + '.' + format, format=format, dpi=dpi)
        if show == 'true':
            plt.show()
        plt.close(fig)
        
def main():
   data_dir, requested_vars, figs_out_dir, format, dpi, show = parse_arguments()
   obs_file_name = data_dir + '/obs'
   figures = plot_variables(data_dir, requested_vars, obs_file_name)
   save_figures(figs_out_dir, figures, format, dpi, show)
   
def plot_variables(data_source, variables, obs_file_name):
    figures = {}
    for variable in variables:
        fig = plt.figure()
        plt.xlabel('Time (days)')
        plt.ylabel('Number of people (-)')
        obs_data_name = variable2observation[variable]
        print("Observed data: ", obs_data_name)
        plot_variable(data_source, variable, obs_file_name, obs_data_name)
        figures[variable] = fig
        
    return figures
        
if __name__ == '__main__':
    main()
