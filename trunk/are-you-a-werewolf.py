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

def AddConsoleGadget(properties, context):
  wavelet = context.GetRootWavelet()
  wavelet.SetTitle('Are You a Werewolf?')
  blip = context.GetBlipById(wavelet.GetRootBlipId())
  if blip:
    blip.GetDocument().AppendElement(document.Gadget(CONSOLE_GADGET_URL))

def GetRoles(size):
  if size <= 3:
    return ['wolf', 'villager', 'villager']
  elif size <= 6:
    return ['fortuneteller', 'wolf', 'wolf', 'villager', 
     'villager', 'villager']
  elif size <= 8:
    return ['hunter', 'fortuneteller', 'wolf', 'wolf', 'villager', 
     'villager', 'villager', 'villater']
  elif size <= 16:
    return ['hunter', 'fortuneteller', 'wolf', 'wolf', 'wolf', 
     'villager', 'villager', 'villager', 'villater', 'villager', 
     'villager', 'villager', 'villater', 'villater', 'villater']

def SendWave(participant_id, role, context, hunter_wave, fortuneteller_wave, wolves_wave):
  if role == 'hunter':
    hunter_wave.AddParticipant(participant_id)
    return hunter_wave.GetWaveId()
  elif role == 'fortuneteller':
    fortuneteller_wave.AddParticipant(participant_id)
    return fortuneteller_wave.GetWaveId()
  elif role == 'wolf':
    wolves_wave.AddParticipant(participant_id)
    return wolves_wave.GetWaveId()
  else:
    participant_wave = NewWave(context, [participant_id])
    participant_wave.SetTitle('You are a villager.')
    return participant_wave.GetWaveId()

def AddRootText(context, text):
  # not implemented
  blip_id = wavelet.GetRootBlipId()
  #blip = context.GetBlipById(context.GetRootWavelet().GetRootBlipId())

def AddText(wavelet, text):
  wavelet.CreateBlip().GetDocument().SetText(text)

def OnBlipSubmitted(properties, context):
  blip_id = properties['blipId']
  blip = context.GetBlipById(blip_id)
  doc = blip.GetDocument()
  gadget = blip.GetGadgetByUrl(CONSOLE_GADGET_URL)
  if gadget:
    started = gadget.get('started')
    if started:
      wave_id = blip.GetWaveId()
      games = Game.gql("WHERE wave_id = '" + wave_id + "' LIMIT 1")
      if games.count() == 0:
        wolves_wave = NewWave(context)
        wolves_wave.SetTitle('You are wolves.')
        fortuneteller_wave = NewWave(context)
        fortuneteller_wave.SetTitle('You are a fortuneteller.')
        hunter_wave = NewWave(context)
        hunter_wave.SetTitle('You are a hunter.')
        game = Game(wave_id=wave_id, 
          wolves_wave_id=wolves_wave.GetWaveId(),
          fortuneteller_wave_id=fortuneteller_wave.GetWaveId(),
          hunter_wave_id=hunter_wave.GetWaveId())
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
          participant_wave_id = SendWave(participant_id, role, 
            context, hunter_wave, fortuneteller_wave, wolves_wave)
          participant = Participant(parent=game, participant_id=participant_id, 
            role=role, participant_wave_id=participant_wave_id)
          participant.put()

if __name__ == '__main__':
  bot = robot.Robot('are-you-a-werewolf', 
    version='0', 
    image_url='http://are-you-a-werewolf.appspot.com/images/profile.png', 
    profile_url='http://are-you-a-werewolf.appspot.com')
  bot.RegisterHandler(events.WAVELET_SELF_ADDED, AddConsoleGadget)
  bot.RegisterHandler(events.BLIP_SUBMITTED, OnBlipSubmitted)
  bot.Run()
