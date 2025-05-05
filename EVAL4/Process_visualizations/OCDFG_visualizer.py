import pm4py

file_path = "final_event_log.json"

ocel = pm4py.read_ocel2_json(file_path)

ocdfg = pm4py.discover_ocdfg(ocel)
pm4py.view_ocdfg(ocdfg, format='svg')
pm4py.save_vis_ocdfg(ocdfg, 'ocdfg.png', annotation='frequency')


