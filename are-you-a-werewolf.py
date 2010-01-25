import logging
import urllib
import random
from waveapi import document
from waveapi import events
from waveapi import model
from waveapi import robot
from waveapi.robot_abstract import NewWave
from models import Game
from models import Participant

CONSOLE_GADGET_URL = 'http://are-you-a-werewolf.appspot.com/gadgets/console.xml'
PING_GADGET_URL = 'http://are-you-a-werewolf.appspot.com/gadgets/ping.xml'


def AddConsoleGadget(properties, context):
  wavelet = context.GetRootWavelet()
  wavelet.SetTitle('Are You a Werewolf?')
  blip = context.GetBlipById(wavelet.GetRootBlipId())
  if blip:
    blip.GetDocument().AppendElement(document.Gadget(CONSOLE_GADGET_URL))

def GetRoles(size):
  ret = None 
  if   size <= 3:  ret = ['wolf']
  elif size <= 6:  ret = ['fortuneteller', 'wolf', 'wolf']
  elif size <= 8:  ret = ['hunter', 'fortuneteller', 'wolf', 'wolf']
  elif size <= 16: ret = ['hunter', 'fortuneteller', 'wolf', 'wolf', 'wolf'] 
  while (len(ret) < size): ret.append('villager')
  return ret

def AddPingGadget(blip, document, wave_id, role):
  blip.GetDocument().AppendElement(document.Gadget(PING_GADGET_URL + '?' + urllib.urlencode({'wave_id': wave_id, 'role': role})))

# ugly function. must be refactored
def SendWave(participant_id, role, context, wave_id, hunter_wave, fortuneteller_wave, wolves_wave):
  blip = None
  if role == 'hunter':
    hunter_wave.AddParticipant(participant_id)
    blip = context.GetBlipById(hunter_wave.GetRootBlipId())
  elif role == 'fortuneteller':
    fortuneteller_wave.AddParticipant(participant_id)
    blip = context.GetBlipById(fortuneteller_wave.GetRootBlipId())
  elif role == 'wolf':
    wolves_wave.AddParticipant(participant_id)
    blip = context.GetBlipById(wolves_wave.GetRootBlipId())
  else:
    participant_wave = NewWave(context, [participant_id])
    participant_wave.SetTitle('You are a villager.')
    blip = context.GetBlipById(participant_wave.GetRootBlipId())
  AddPingGadget(blip, document, wave_id, role)

def AddRootText(context, text):
  # not implemented
  blip_id = wavelet.GetRootBlipId()
  #blip = context.GetBlipById(context.GetRootWavelet().GetRootBlipId())

def AddText(wavelet, text):
  wavelet.CreateBlip().GetDocument().SetText(text)

def CheckExecutionPolling(game, gadget, doc):
  points = {}
  for key, pollee in gadget.items():
    if key.startswith('execution.'):
      doc.GadgetSubmitDelta(gadget, {key:None})
      if points[pollee]:
        points[pollee] += 1
      else:
        points[pollee] = 0
  max = 0
  result = []
  for pollee, point in points:
    if max == point:
      result.push(pollee)
    elif max < point:
      max = point
      result = [pollee]
  return random.choice(result)

def HandleConsoleGadget(context, blip, doc, gadget):
  if not gadget.get('started'): 
    return

  wave_id = blip.GetWaveId()
  games = Game.gql("WHERE wave_id = :1 LIMIT 1", wave_id)
  if games.count() == 0:
    wolves_wave = NewWave(context)
    wolves_wave.SetTitle('You are wolves.')
    fortuneteller_wave = NewWave(context)
    fortuneteller_wave.SetTitle('You are a fortuneteller.')
    hunter_wave = NewWave(context)
    hunter_wave.SetTitle('You are a hunter.')
    game = Game(wave_id=wave_id) 
    game.put()

    participant_ids = []
    for attr in dir(gadget):
      if attr.startswith('participant.'):
        participant_id = attr.split('.', 1)[-1]
        participant_ids.append(participant_id)
    roles = GetRoles(len(participant_ids))
    random.shuffle(participant_ids)
    for participant_id in participant_ids:
      role = roles.pop(0)
      SendWave(participant_id, role, context, wave_id, hunter_wave, fortuneteller_wave, wolves_wave)
      participant = Participant(parent=game, game_wave_id=wave_id, participant_id=participant_id, role=role)
      participant.put()

  game = games[0]
  if gadget.get('stage_changed'):
    doc.GadgetSubmitDelta(gadget, {'stage_changed':None})
    stage = gadget.get('stage')
    if stage == 'day':
      # check and show night result
      pass
    elif stage == 'twilight':
      AddText(context.GetRootWavelet(), 'Start polling for execution')
    elif stage == 'night':
      target = CheckExecutionPolling(game, gadget, doc)
      doc.GadgetSubmitDelta(gadget, {'participant.' + target: 'dead'})
      # check and show twilight result
    game.stage = stage
    game.put()

def HandlePingGadget(context, blip, doc, gadget):
  parent_wave_id = gadget.get('parent_wave_id')
  games = Game.gql('WHERE wave_id = :1', parent_wave_id)
  if games.count() != 0:
    game = games[0]
    wave_id = blip.GetWaveId()
    role = gadget.get('role')
    if role == 'wolf':
      game.wolves_wave_id = wave_id
    elif role == 'fortuneteller':
      game.fortuneteller_wave_id = wave_id
    elif role == 'hunter':
      game.hunter_wave_id = wave_id
    game.put()

    """
    participant = Participant.gql(
      'WHERE game_wave_id = :1 AND participant_id = :2', 
      wave_id, participant_id
    )
    """

def GetGadgetByBaseUrl(blip, url):
  for el in blip.elements.values():
    if (el.type == document.ELEMENT_TYPE.GADGET
        and getattr(el, 'url', None).startswith(url)):
      return el
  return None

def OnBlipSubmitted(properties, context):
  blip_id = properties['blipId']
  blip = context.GetBlipById(blip_id)
  doc = blip.GetDocument()

  console_gadget = blip.GetGadgetByUrl(CONSOLE_GADGET_URL)
  if console_gadget:
    HandleConsoleGadget(context, blip, doc, console_gadget)

  ping_gadget = GetGadgetByBaseUrl(blip, PING_GADGET_URL)
  if ping_gadget:
    HandlePingGadget(context, blip, doc, ping_gadget)


if __name__ == '__main__':
  bot = robot.Robot('Are you a werewolf?', 
    version='1', 
    image_url='http://are-you-a-werewolf.appspot.com/images/profile_medium.png', 
    profile_url='http://are-you-a-werewolf.appspot.com')
  bot.RegisterHandler(events.WAVELET_SELF_ADDED, AddConsoleGadget)
  bot.RegisterHandler(events.BLIP_SUBMITTED, OnBlipSubmitted)
  bot.RegisterCronJob('/wave', 5 * 60) # do not work
  bot.Run()
