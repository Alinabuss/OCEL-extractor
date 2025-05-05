import pm4py

file_path = "final_event_log.json"

ocel = pm4py.read_ocel2_json(file_path)

ocpn = pm4py.discover_oc_petri_net(ocel)
pm4py.view_ocpn(ocpn, format='svg')
pm4py.save_vis_ocpn(ocpn, 'ocpn.png')
