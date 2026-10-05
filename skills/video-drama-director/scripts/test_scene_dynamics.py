"""Symbolic causal regressions, not evidence that a generated video looks correct."""
import copy
import unittest
from validate_scene_plan import validate_plan

def plan(kind,fields,events,end=None):
 return {'entities':{kind:{'kind':'tracked object'}},'initial_state':{kind:fields},'units':[{'id':'scene','cast':[],'start_state':{kind:copy.deepcopy(fields)},'events':events,'sounds':[],'end_state':{kind:copy.deepcopy(end if end is not None else fields)}}]}
def codes(p):return {x['code'] for x in validate_plan(p)['issues'] if x['severity']=='error'}

class SceneDynamicsTests(unittest.TestCase):
 def test_camera_wrong_direction_cannot_expose_as_group_photo(self):
  event={'id':'expose','cause':'mechanical delay expires','requires':{'camera':{'front_target':'companions'}},'effects':{'camera':{'exposures':1}}}
  p=plan('camera',{'front_target':'viewer','exposures':0},[event],{'front_target':'viewer','exposures':1})
  self.assertIn('event_precondition',codes(p))

 def test_turning_camera_then_exposing_has_valid_precondition(self):
  fields={'front_target':'viewer','exposures':0}
  events=[{'id':'aim','cause':'operator turns the camera toward companions','requires':{'camera':{'front_target':'viewer'}},'effects':{'camera':{'front_target':'companions'}}},
          {'id':'expose','cause':'mechanical delay expires','requires':{'camera':{'front_target':'companions'}},'effects':{'camera':{'exposures':1}}}]
  self.assertEqual(set(),codes(plan('camera',fields,events,{'front_target':'companions','exposures':1})))

 def test_stationary_crowd_cannot_supply_declared_moving_contact(self):
  e={'id':'contact','cause':'near pedestrian advances into shared space','requires':{'crowd':{'flow':'advancing'}},'effects':{'crowd':{'contact':'shoulder'}}}
  self.assertIn('event_precondition',codes(plan('crowd',{'flow':'stationary','contact':'none'},[e],{'flow':'stationary','contact':'shoulder'})))

 def test_advancing_crowd_supports_declared_contact(self):
  e={'id':'contact','cause':'near pedestrian advances into shared space','requires':{'crowd':{'flow':'advancing'}},'effects':{'crowd':{'contact':'shoulder'}}}
  self.assertEqual(set(),codes(plan('crowd',{'flow':'advancing','contact':'none'},[e],{'flow':'advancing','contact':'shoulder'})))

 def test_obvious_available_seat_conflicts_with_no_seat_premise(self):
  e={'id':'search','cause':'seek another usable place','requires':{'near_seat':{'available':False,'reachable':True}},'effects':{}}
  self.assertIn('event_precondition',codes(plan('near_seat',{'available':True,'reachable':True},[e])))

 def test_occupied_seat_supports_search_elsewhere(self):
  e={'id':'search','cause':'seek another usable place','requires':{'near_seat':{'available':False,'reachable':True}},'effects':{}}
  self.assertEqual(set(),codes(plan('near_seat',{'available':False,'reachable':True},[e])))

 def test_deliberately_quiet_reading_room_may_remain_still(self):
  self.assertEqual(set(),codes(plan('readers',{'activity':'reading quietly'},[])))

if __name__=='__main__':unittest.main()
