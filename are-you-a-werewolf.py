import logging
import urllib
from waveapi import document
from waveapi import events
from waveapi import model
from waveapi import robot
from waveapi.robot_abstract import NewWave
from models import Game
from models import Participant

CONSOLE_GADGET_URL = 'http://are-you-a-werewolf.appspot.com/gadgets/console.xml'

def AddConsoleGadget(properties, context):
  blip = context.GetBlipById(context.GetRootWavelet().GetRootBlipId())
  if blip:
    blip.GetDocument().AppendElement(document.Gadget(CONSOLE_GADGET_URL))
  

def OnBlipSubmitted(properties, context):
  #NewWave(context, ['andyjpn@googlewave.com'])
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
        participant_ids = []
        for attr in dir(gadget):
          if attr.startswith('participant.'):
            participant_id = attr.split('.', 1)[-1]
            participant_ids.append(participant_id)
        game = Game(wave_id=wave_id)
        game.put()
        for participant_id in participant_ids:
          participant = Participant(parent=game, participant_id=participant_id)
          participant.put()

if __name__ == '__main__':
  bot = robot.Robot('are-you-a-werewolf', 
    version='0', 
    image_url='http://are-you-a-werewolf.appspot.com/images/profile.png', 
    profile_url='http://are-you-a-werewolf.appspot.com')
  bot.RegisterHandler(events.WAVELET_SELF_ADDED, AddConsoleGadget)
  bot.RegisterHandler(events.BLIP_SUBMITTED, OnBlipSubmitted)
  bot.Run()
