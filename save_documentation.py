import os
import json

def save_documentation(docs_obj_dict):
    # Create a new dictionary to store the transformed values
    grouped_dict = {}
    
    # Iterate over the original dictionary
    for key, value in docs_obj_dict.items():
        # Get the source file from the object
        source_file = value.source_file

        # Get the payload from the object
        payload = value.payload
        pos = value.position_abs_to_rel()
        print(key, pos)
        payload["viz"] = pos
        
        # Add the key-value pair to the transformed dictionary
        if source_file not in grouped_dict:
            grouped_dict[source_file] = {}
        grouped_dict[source_file][key] = payload
    
    # Iterate over the grouped dictionary
    for source_file, transformed_dict in grouped_dict.items():
        # Create the directory if it doesn't exist
        directory = os.path.dirname(source_file)
        if not os.path.exists(directory):
            os.makedirs(directory)

        # Open the file in write mode
        with open(source_file, 'w') as file:
            # Write the transformed dictionary to the file as JSON
            json.dump(transformed_dict, file, indent=2)
