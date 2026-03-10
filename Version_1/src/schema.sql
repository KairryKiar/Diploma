
CREATE TABLE IF NOT EXISTS activities_catalog (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bitrix_code TEXT UNIQUE, 
    display_name TEXT,       
    category TEXT            
);


CREATE TABLE IF NOT EXISTS activity_params (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    activity_id INTEGER,
    param_key TEXT,          
    is_required BOOLEAN DEFAULT 0,
    FOREIGN KEY (activity_id) REFERENCES activities_catalog(id),
    UNIQUE(activity_id, param_key)
);


CREATE TABLE IF NOT EXISTS training_dataset (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_prompt TEXT,        
    completion_json TEXT,    
    source_file TEXT         
);


CREATE TABLE IF NOT EXISTS syntax_dictionary (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    human_concept  TEXT,    
    bitrix_syntax  TEXT,    
    description    TEXT     
);