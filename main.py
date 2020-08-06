#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Author: Tom Rae
Authorised use only
"""

import json
import argparse
from pathlib import Path
import subprocess



class Constants:
    
    """Global constants for output or functioning"""
    
    def __init__(self):
        self.CONFIG_FILE_PATTERN = "*.json"
        self.ARGS_DESCRIPTION = 'Deploy a preconfigured server via a {} config file'.format(self.CONFIG_FILE_PATTERN)
        self.CONFIG_SELECTION_PROMPT = 'Select one of the listed config files'
        self.CONFIG_NO_FILES = 'No config files found. Exiting application'
        self.CONFIG_REQUIRED_KEYS = ['description', 'path', 'commands']
        self.LOG_ERROR = 'An error with a command occured. Exiting application'
        self.LOG_MISSING_KEY = '{key} not found in task #{index} in {group}'
        self.LOG_MISSING_GROUP = '{key} not found in config file'
        self.LOG_INDENT = ' | '
        self.LOG_RETURN_STATE = '[{state}]'
        self.LOG_DESCRIPTION = '"{description}"'
        self.LOG_COMMAND_PREFIX = ' | '
        self.LOG_DEBUG_PREFIX = ' |  | '
        self.VERBOSE_COMMAND = 1
        self.VERBOSE_DEBUG = 2
        self.MOD_VERBOSE = 'verbose'
        self.MOD_IGNOREERROR = 'ignoreerror'
        self.MOD_SKIP = 'skip'
        self.TASK_SUCCESS = 0
        self.TASK_ERROR = 1
        self.TASK_ERROR_IGNORED = 2
        self.TASK_SKIPPED = 3
        self.TASK_RETURNCODES = {
            self.TASK_SUCCESS: 'ok',
            self.TASK_ERROR: 'FAIL',
            self.TASK_ERROR_IGNORED: 'fail silent',
            self.TASK_SKIPPED: 'skip'
        }
        self.RETURNCODE_SUMMARY = '''Of {total} tasks run:
{0} succeeded,
{3} skipped,
{2} failed silently,
{1} failed'''



class Functions:
    
    """A series of common functions"""
    
    def get_input(self, prompt, requirement):
        while True:
            user_input = input(prompt)
            if requirement(user_input): break
        return user_input
        
        
    def exit_if_false(self, value, text=''):
        if not value:
            if text: print(text)
            exit()
            
            
    def is_digit(self, value):
        try:
            int(value)
            return True
        except (ValueError, TypeError):
            return False
            
            
    def between_function(self, low, high):
        return lambda x: func.is_digit(x) and low <= int(x) <= high
        
        
    def get_list_index_string(self, item_string, item_list):
        return '\n'.join([
            item_string.format(index=index, item=item)
            for index, item in enumerate(item_list) ])
            
            
    def check_missing_keys(self, item, keys, error_text):
        for key in keys:
            if key not in item:
                raise KeyError(error_text.format(key=key))
                
                
    def prefix_text(self, text, prefix):
        return prefix + text[:-1].replace('\n', '\n'+prefix) + text[-1] if text else text
        
        
    def ascii_only(self, text):
        return ''.join(c for c in text if ord(c)<128)
        
    
    def search_for_files(self, file_match, recursive_directories=[], directories=[], files=[]):
        return sorted(list({
            file.absolute().resolve().as_posix()
            for file in
                [
                    file
                    for dir in recursive_directories
                    for file in Path(dir).rglob(file_match) 
                ] + [
                    file
                    for dir in directories
                    for file in Path(dir).glob(file_match) 
                ] + [
                    files
                    for file in files
                    if file.is_file()
                ]
            }))
        
            
                
class ServerDeployer:
    
    """This class has responsilitiy for deploying a preconfigured server"""
    
    def __init__(self):
        self.file_directory = Path(__file__).parent.absolute().resolve()
        
        self.args = None
        self.verbose = None
        self.override_verbose = None
        
        self.config_files = None
        self.config_file = None
        self.config_data = None
        
        self.running = True
        self.returncode_summary = ReturncodeSummary(list(const.TASK_RETURNCODES))


    def run(self):
        self.read_in_args()
        self.find_config_files()
        self.select_config_file()
        self.read_in_config()
        # self.execute_group('bashscripts')
        self.execute_group('clonegithubrepos')
        # self.execute_group('installgithubrepos')
        self.execute_group('dockerfiles')
        self.create_task_summary()
        
    
    def skippable(func):
        def decorator(*args, **kwargs):
            self = args[0]
            if self.running:
                func(*args, **kwargs)
        return decorator
        
    
    @skippable
    def read_in_args(self):
        """Read in command line arguments amd prompt user to select config file"""
        
        parser = argparse.ArgumentParser(description=const.ARGS_DESCRIPTION)
        parser.add_argument('-v', '--verbose', action='count', default=0, help='give more debug output. can be used up to 2 times')
        parser.add_argument('-f', '--file', nargs='*', default=[], help='include listed config files')
        parser.add_argument('-r', '--recursive-directory', nargs='*', default=[], help='recursively search listed directories')
        parser.add_argument('-d', '--directory', nargs='*', default=[], help='search listed directories')
        parser.add_argument('-m', '--disable-mods', action='store_true', default=[], help='disable config modficiation attributes')
        args = parser.parse_args()
        
        self.args = args
        self.verbose = args.verbose
        self.enable_mods = not args.disable_mods
        
    
    @skippable    
    def find_config_files(self):
        """Search the given directories for config files"""
        
        config_files = func.search_for_files(
            const.CONFIG_FILE_PATTERN,
            recursive_directories=self.args.recursive_directory,
            directories=self.args.directory + [self.file_directory], # include cwd
            files=self.args.file )
        self.config_files = config_files
        
    
    @skippable    
    def select_config_file(self):
        """Output config file choices and store input"""
        
        func.exit_if_false(self.config_files, text=const.CONFIG_NO_FILES)
        
        print(const.CONFIG_SELECTION_PROMPT)
        print(func.get_list_index_string('[{index}] {item}', ['exit']+self.config_files))
        config_file_choice = int(func.get_input(
            '> ', func.between_function(0, len(self.config_files)) ))
            
        func.exit_if_false(config_file_choice)
        self.config_file = self.config_files[config_file_choice-1]

    
    @skippable
    def read_in_config(self):
        """Read and store chosen config file into memory"""
        
        with open(self.config_file, 'r') as file:
            self.config_data = json.load(file)
            
    
    @skippable        
    def execute_group(self, json_group): # make group into object?
        """Run a shell task group"""
        
        func.check_missing_keys(self.config_data, [json_group], const.LOG_MISSING_GROUP )
        list_of_tasks = self.config_data[json_group]
        
        for index, task_data in enumerate(list_of_tasks):
            task = Task(task_data, self.verbose, self.enable_mods, index, json_group)
            returncode = task.execute()
            
            self.returncode_summary.count(returncode)
            if returncode == const.TASK_ERROR:
                self.running = False
                break
                
            
    def create_task_summary(self):
        self.returncode_summary.summary(const.RETURNCODE_SUMMARY)
        
                    
    
                
class Task:
    """Execute and manage a task"""
    
    def __init__(self, data, verbose, enable_mods, index_in_group, group_name):
        self.verbose = verbose
        self.enable_mods = enable_mods
        self.index = index_in_group
        self.group = group_name
        self.check_missing_keys(data)
        self.description = data['description']
        self.path = Path(data['path']).absolute().resolve()
        self.commands = data['commands']
        self.mods = data.get('mods', [])
        
        self.should_output_command = self.check_verbose_output(const.VERBOSE_COMMAND)
        self.should_output_debug = self.check_verbose_output(const.VERBOSE_DEBUG)
        self.should_throw_error = self.check_error_output()
        self.should_execute = self.check_should_execute()
        
        self.returncode = self.get_inital_returncode()
        
    def check_missing_keys(self, data):
        func.check_missing_keys(
            data, 
            const.CONFIG_REQUIRED_KEYS,
            const.LOG_MISSING_KEY.format(
                key='{key}',
                index=self.index+1,
                group=self.group ))
                
    def check_verbose_output(self, verbose_level):
        verbose_override = self.enable_mods and const.MOD_VERBOSE in self.mods
        return verbose_override or self.verbose >= verbose_level
        
    
    def check_error_output(self):
        return not (self.enable_mods and const.MOD_IGNOREERROR in self.mods)
        
    
    def check_should_execute(self):
        return const.MOD_SKIP not in self.mods
        
        
    def get_inital_returncode(self):
        return const.TASK_SUCCESS if self.should_execute else const.TASK_SKIPPED
        
    
    def execute(self):
        if self.should_execute:
            
            self.output_description()
            
            process_handler = ProcessHandler(self.commands, self.path)
            for process in process_handler.run():
                self.try_output_command(process.command)
                
                for stdout_line in process.execute():                    
                    self.try_output_debug(stdout_line)
                    
                self.handle_process_error(process, process_handler)
        
        self.output_returncode_state()
        print()
        return self.returncode
        
        
    def output_description(self):
        print(const.LOG_DESCRIPTION.format(description=self.description))
        
        
    def try_output_command(self, command):
        if self.should_output_command:
            self.output_command(command)
        
        
    def output_command(self, command):
        print(func.prefix_text(command, const.LOG_COMMAND_PREFIX))
            
            
    def try_output_debug(self, debug):
        if self.should_output_debug:
            self.output_debug(debug)
            
            
    def output_debug(self, debug):
        print(self.format_debug(debug), end='')
        
        
    def output_returncode_state(self):
        print(const.LOG_RETURN_STATE.format(state=const.TASK_RETURNCODES[self.returncode]))
            
    def handle_process_error(self, process, process_handler):
        if process.returncode != 0:
            if not self.should_output_command:
                self.output_command(process.command)
            print(self.format_debug(process.stderr), end='')
            if self.should_throw_error:
                self.returncode = const.TASK_ERROR
                process_handler.kill()
            else:
                self.returncode = const.TASK_ERROR_IGNORED

                        
    def format_debug(self, text):
        return func.prefix_text(func.ascii_only(text), const.LOG_DEBUG_PREFIX)
                
                
    
class ProcessHandler:
    
    """Creates a process for each command"""
    
    def __init__(self, commands, cwd):
        self.commands = commands
        self.cwd = cwd
        self.running = True
        
        
    def run(self):
        for command in self.commands:
            process = ProcessExecutor(command, self.cwd)
            yield process
            
            if not self.running:
                break
            
            
    def kill(self):
        self.running = False
        
        
        
class ProcessExecutor:
    
    """Runs a specific command and yields output"""
    
    def __init__(self, command, cwd):
        self.command = command
        self.cwd = cwd
        self.returncode = None
        self.stdout = None
        self.stderr = None
        
    
    # def check_cwd(self):
    #     if not Path(self.cwd).is_dir():
    # 
    # 
    def execute(self):
        process = subprocess.Popen(
            self.command, 
            shell=True, 
            text=True, # returns stdout as string
            stderr=subprocess.PIPE, # enables output
            stdout=subprocess.PIPE, # enables output
            cwd=self.cwd )
            
        self.stdout = ''
        while process.poll() is None:
            line = process.stdout.readline()
            self.stdout += line
            if line: yield line
        process.wait()
        
        self.returncode = process.returncode
        self.stderr = process.stderr.read()



class ReturncodeSummary:
    def __init__(self, returncodes):
        self.counts = {str(item): 0 for item in returncodes+['total']}
        
    def count(self, returncode):
        self.counts[str(returncode)] += 1
        self.counts['total'] += 1
        
    def summary(self, string):
        result = string
        for key, item in self.counts.items():
            result = result.replace('{{{}}}'.format(key), str(item))
        print(result)
        
        
        
### GLOBAL VARIABLES

const = Constants()

func = Functions()
    
### END GLOBAL VARIABLES



def main():
    """Run the main method."""
    Deployer = ServerDeployer()
    Deployer.run()

if __name__ == "__main__":
    main()
