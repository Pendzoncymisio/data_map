import json

def save_documentation(docs_obj_dict):
    # Create a new dictionary to store the transformed values
    transformed_dict = {}
    
    # Iterate over the original dictionary
    for key, value in docs_obj_dict.items():
        # Get the payload from the object
        payload = value.payload
        pos = value.get_rel_pos()
        print(key, pos)
        payload["viz"] = pos
        
        # Add the key-value pair to the transformed dictionary
        transformed_dict[key] = payload
    
    # Open the file in write mode
    with open('documentation.json', 'w') as file:
        # Write the transformed dictionary to the file as JSON
        json.dump(transformed_dict, file, indent=2)
