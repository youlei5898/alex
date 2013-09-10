#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib
import urllib2

import alex.utils.cache as cache
import alex.utils.audio as audio

from alex.components.tts import TTSInterface
from alex.components.tts.exceptions import TTSException
from alex.components.tts.preprocessing import TTSPreprocessing

class VoiceRssTTS(TTSInterface):
    """Uses The VoiceRss TTS service to synthesize sentences in a
    specific language, e.g. en-us.

    The main function synthesize returns a string which contain a RIFF
    wave file audio of the synthesized text."""

    def __init__(self, cfg):
        """Intitialize: just remember the configuration."""
        self.cfg = cfg
        super(VoiceRssTTS, self).__init__(cfg)
        self.preprocessing = TTSPreprocessing(self.cfg, self.cfg['TTS']['VoiceRss']['preprocessing'])

    @cache.persistent_cache(True, 'VoiceRssTTS.get_tts_wav.')
    def get_tts_wav(self, language, text):
        """Access the VoiceRss TTS service and get synthesized audio
        for a text.
        Returns a string with a WAV stream."""
        baseurl = "http://api.voicerss.org"
        values = {'src': text.encode('utf8'),
                  'hl': language,
                  'key': self.cfg['TTS']['VoiceRss']['api_key']}
        data = urllib.urlencode(values)
        request = urllib2.Request(baseurl, data)
        request.add_header("User-Agent", "Mozilla/5.0 (X11; U; Linux i686) " +
                           "Gecko/20071127 Firefox/2.0.0.11")
        try:
            wavresponse = urllib2.urlopen(request)
            return audio.convert_wav(self.cfg, wavresponse.read())
        except Exception as e:
            raise TTSException("TTS error: " + unicode(e))

    def synthesize(self, text):
        """Synthesize the text and return it in a string
        with audio in default format and sample rate."""

        text = self.preprocessing.process(text)
        wav = self.get_tts_wav(self.cfg['TTS']['VoiceRss']['language'], text)
        wav = audio.change_tempo(self.cfg, self.cfg['TTS']['VoiceRss']['tempo'], wav)
        return wav
