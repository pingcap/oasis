# -*- coding: utf-8 -*-

from __future__ import absolute_import

SCHEMA = '''
      CREATE TABLE IF NOT EXISTS model_template (
            id INTEGER PRIMARY KEY , 
            name TEXT UNIQUE, 
            config TEXT);
      CREATE INDEX IF NOT EXISTS idx_mt_name ON model_template(name); 
      
      CREATE TABLE IF NOT EXISTS model_instance (
            id INTEGER PRIMARY KEY , 
            model TEXT , 
            job_id INTEGER ,
            report TEXT,
            config TEXT ,  
            status TEXT); 
      CREATE INDEX IF NOT EXISTS idx_mi_model ON model_instance(model); 
      CREATE INDEX IF NOT EXISTS idx_mi_job ON model_instance(job_id); 
      
      CREATE TABLE IF NOT EXISTS job (
            id INTEGER PRIMARY KEY , 
            data_source TEXT ,  
            models TEXT , 
            timeout TEXT , 
            slack_channel TEXT , 
            model_instance_ids TEXT , 
            status TEXT , 
            api_models_config TEXT); 
'''


