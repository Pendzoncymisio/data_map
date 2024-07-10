import json

from doc_obj import DocObj
from line import Line

def load_raw_documentation():
    with open("../documentation/documentation.json", 'r') as file:
        data = json.load(file)
    return data    

def load_documentation():
    print("Loading documentation...")
    raw_documentation_dict = load_raw_documentation()

    docs_obj_dict = {}
    group_dict = {}

    for document_id, document_value in raw_documentation_dict.items():
        doc_obj = DocObj(document_id, document_value, docs_obj_dict)

        # Handle parent groups
        group_id = document_value.get("group", "")
        if group_id:
            if group_id not in group_dict:
                group_dict[group_id] = []
            group_dict[group_id].append(doc_obj)

            
    # Fill children of groups
    for group_id, group_list in group_dict.items():
        for doc_obj in group_list:
            docs_obj_dict[group_id].add_child_document(doc_obj)

    #Second run, when we know that all objects are created
    for document_id, doc_obj in docs_obj_dict.items():
        # Specify group vs final type
        if doc_obj.children_docs:
            doc_obj.make_group()
            for child_doc_obj in doc_obj.children_docs:
                child_doc_obj.parent_doc = doc_obj
        else:
            doc_obj.make_final()

    # Tree traverse to calculate final position from relative position
    root_nodes = [doc_obj for doc_obj in docs_obj_dict.values() if not doc_obj.parent_doc]
    for root_node in root_nodes:
        root_node.propagate_postion_down()

    # Third pass after we know exact positions of all objects
    for document_id, doc_obj in docs_obj_dict.items():
        sources = [docs_obj_dict[source_id] for source_id in doc_obj.payload.get("sources", [])]
        for source in sources:
            line = Line(source, doc_obj)
            source.outbound_lines.append(line)
            doc_obj.inbound_lines.append(line)

        if doc_obj.group:
            doc_obj.propagate_postion_up()

    print("Documentation loaded!")

    return docs_obj_dict

if __name__ == "__main__":
    root_nodes = load_documentation()
    print(root_nodes)
