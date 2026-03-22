/**
 * recorder.js – Real-time audio recording with waveform visualisation.
 *
 * Usage:
 *   import { AudioRecorder } from './recorder.js';
 *   const recorder = new AudioRecorder({ onStop: (blob) => { ... } });
 *   await recorder.start();
 *   recorder.stop();
 */

export class AudioRecorder {
  /**
   * @param {Object} opts
   * @param {Function} [opts.onStop]          Called with (Blob, AudioBuffer|null) when recording stops.
   * @param {HTMLCanvasElement} [opts.canvas] Canvas element for the waveform visualiser.
   */
  constructor({ onStop = () => {}, canvas = null } = {}) {
    this._onStop       = onStop;
    this._canvas       = canvas;
    this._mediaStream  = null;
    this._mediaRecorder = null;
    this._chunks       = [];
    this._audioCtx     = null;
    this._analyser     = null;
    this._animFrameId  = null;
    this._blob         = null;
    this.isRecording   = false;
  }

  /** Start recording from the default microphone. */
  async start() {
    if (this.isRecording) return;

    this._chunks = [];
    this._blob   = null;

    this._mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });
    this._mediaRecorder = new MediaRecorder(this._mediaStream);

    this._mediaRecorder.ondataavailable = (e) => {
      if (e.data.size > 0) this._chunks.push(e.data);
    };

    this._mediaRecorder.onstop = () => {
      this._blob = new Blob(this._chunks, { type: 'audio/webm' });
      this._stopVisualiser();
      this._onStop(this._blob);
    };

    this._mediaRecorder.start(100); // collect data every 100 ms
    this.isRecording = true;

    if (this._canvas) this._startVisualiser();
  }

  /** Stop recording. */
  stop() {
    if (!this.isRecording) return;
    this.isRecording = false;
    this._mediaRecorder?.stop();
    this._mediaStream?.getTracks().forEach(t => t.stop());
  }

  /**
   * Return a playable <audio> element for the last recording.
   * The caller is responsible for revoking the object URL via
   * `URL.revokeObjectURL(audio.src)` when the element is no longer needed.
   * @returns {HTMLAudioElement|null}
   */
  createAudioElement() {
    if (!this._blob) return null;
    const url   = URL.createObjectURL(this._blob);
    const audio = new Audio(url);
    return audio;
  }

  /** Play back the last recording (URL is revoked automatically after playback). */
  play() {
    if (!this._blob) return;
    const url   = URL.createObjectURL(this._blob);
    const audio = new Audio(url);
    audio.addEventListener('ended', () => URL.revokeObjectURL(url));
    audio.play();
  }

  /* ── Private: waveform visualiser ─────────────────────────── */

  _startVisualiser() {
    this._audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    this._analyser = this._audioCtx.createAnalyser();
    this._analyser.fftSize = 256;

    const source = this._audioCtx.createMediaStreamSource(this._mediaStream);
    source.connect(this._analyser);

    this._drawWaveform();
  }

  _stopVisualiser() {
    if (this._animFrameId) {
      cancelAnimationFrame(this._animFrameId);
      this._animFrameId = null;
    }
    this._audioCtx?.close();
    this._audioCtx = null;

    // Clear canvas
    if (this._canvas) {
      const ctx = this._canvas.getContext('2d');
      ctx.clearRect(0, 0, this._canvas.width, this._canvas.height);
    }
  }

  _drawWaveform() {
    if (!this._canvas || !this._analyser) return;

    const canvas  = this._canvas;
    const ctx     = canvas.getContext('2d');
    const bufLen  = this._analyser.frequencyBinCount;
    const dataArr = new Uint8Array(bufLen);

    const draw = () => {
      this._animFrameId = requestAnimationFrame(draw);
      this._analyser.getByteTimeDomainData(dataArr);

      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.lineWidth   = 2;
      ctx.strokeStyle = '#3b82f6';
      ctx.beginPath();

      const sliceWidth = canvas.width / bufLen;
      let x = 0;

      for (let i = 0; i < bufLen; i++) {
        const v = dataArr[i] / 128.0;
        const y = (v * canvas.height) / 2;
        if (i === 0) ctx.moveTo(x, y);
        else         ctx.lineTo(x, y);
        x += sliceWidth;
      }

      ctx.lineTo(canvas.width, canvas.height / 2);
      ctx.stroke();
    };

    draw();
  }
}
