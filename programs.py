#! /usr/bin/env python3
# -*- coding: utf-8 -*-


import os.path
import json



class ProgramStore():
    def __init__(self, path):
        self.program_file = path
        self.programs = dict()

        # Create new program file if it doens't exist yet
        if not os.path.exists(self.program_file):
            with open(self.program_file, 'w') as fout:
                fout.write('[]\n')
        
        with open(self.program_file, 'r') as fin:
            json_data = json.load(fin)
            for p in json_data:
                name = p["name"]
                self.programs[name] = p["operations"]
    
    def write_file(self):
        data = []
        for name, ops in self.programs.items():
            obj = {"name": name, "operations": ops}
            data.append(obj)
        
        with open(self.program_file, 'w') as fout:
            json.dump(data, fout, indent=2)

    def get_names(self):
        return list(self.programs.keys())

    def add(self, name: str, operations: list):
        self.programs[name] = operations
        self.write_file()

    def get(self, name: str):
        return self.programs.get(name, [])

    def delete(self, name: str):
        if name in self.programs:
            del self.programs[name]