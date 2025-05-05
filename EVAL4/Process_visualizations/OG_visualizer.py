import pm4py

file_path = "final_event_log.json"

ocel = pm4py.read_ocel2_json(file_path)

obj_graph = pm4py.ocel.discover_objects_graph(ocel)
pm4py.view_object_graph(ocel, obj_graph, format='svg')
pm4py.save_vis_object_graph(ocel, obj_graph, 'obj_graph.png')