/**
 * transcriber.js – Speech-to-Text via the Web Speech API (Chrome / Edge).
 *
 * Usage:
 *   import { SpeechTranscriber } from './transcriber.js';
 *   const t = new SpeechTranscriber({
 *     lang: 'th-TH',
 *     onResult: (text, isFinal, confidence) => { ... },
 *     onError:  (err)  => { ... },
 *     onEnd:    ()     => { ... },
 *   });
 *   t.start();
 *   t.stop();
 */

export class SpeechTranscriber {
  /**
   * @param {Object}   opts
   * @param {string}   [opts.lang='th-TH']    BCP-47 language tag.
   * @param {Function} [opts.onResult]         (text, isFinal, confidence) => void
   * @param {Function} [opts.onError]          (errorEvent) => void
   * @param {Function} [opts.onEnd]            () => void
   * @param {Function} [opts.onStatusChange]   (status: 'idle'|'listening'|'error') => void
   */
  constructor({
    lang = 'th-TH',
    onResult       = () => {},
    onError        = () => {},
    onEnd          = () => {},
    onStatusChange = () => {},
  } = {}) {
    this.lang           = lang;
    this._onResult      = onResult;
    this._onError       = onError;
    this._onEnd         = onEnd;
    this._onStatusChange = onStatusChange;
    this._recognition   = null;
    this.isListening    = false;
  }

  /** Whether the browser supports the Web Speech API. */
  static isSupported() {
    return 'SpeechRecognition' in window || 'webkitSpeechRecognition' in window;
  }

  /** Start listening. Throws if browser does not support STT. */
  start() {
    if (!SpeechTranscriber.isSupported()) {
      throw new Error(
        'Speech recognition is not supported in this browser. ' +
        'Please use Chrome or Edge.'
      );
    }

    if (this.isListening) return;

    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    this._recognition = new SR();

    // For Thai + EN combined, use Thai as primary language
    const primaryLang = this.lang === 'th-TH+en-US' ? 'th-TH' : this.lang;
    this._recognition.lang          = primaryLang;
    this._recognition.interimResults = true;
    this._recognition.continuous     = true;
    this._recognition.maxAlternatives = 1;

    this._recognition.onstart = () => {
      this.isListening = true;
      this._onStatusChange('listening');
    };

    this._recognition.onresult = (event) => {
      let interim = '';
      let finalText = '';

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const result = event.results[i];
        const transcript = result[0].transcript;
        const confidence = result[0].confidence;

        if (result.isFinal) {
          finalText += transcript;
          this._onResult(transcript, true, confidence);
        } else {
          interim += transcript;
          this._onResult(transcript, false, confidence);
        }
      }
    };

    this._recognition.onerror = (event) => {
      this.isListening = false;
      this._onStatusChange('error');
      this._onError(event);
    };

    this._recognition.onend = () => {
      this.isListening = false;
      this._onStatusChange('idle');
      this._onEnd();
    };

    this._recognition.start();
  }

  /** Stop listening. */
  stop() {
    if (!this.isListening) return;
    this._recognition?.stop();
    this.isListening = false;
  }
}
