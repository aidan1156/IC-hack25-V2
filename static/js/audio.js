 class AudioRecorder {
    constructor() {
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.recordingPromise = null;
        this.resolveRecording = null;
    }

    start() {
        return new Promise(async (resolve, reject) => {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                this.audioChunks = [];
                
                this.mediaRecorder = new MediaRecorder(stream, {
                    mimeType: 'audio/webm'
                });

                // Set up data handling
                this.mediaRecorder.ondataavailable = (event) => {
                    if (event.data.size > 0) {
                        this.audioChunks.push(event.data);
                    }
                };

                // Create a new promise that will resolve when stop() is called
                this.recordingPromise = new Promise(resolve => {
                    this.resolveRecording = resolve;
                });

                // Start recording
                this.mediaRecorder.start(1000);
                resolve();
            } catch (error) {
                reject(error);
            }
        });
    }

    stop() {
        return new Promise((resolve, reject) => {
            if (!this.mediaRecorder || this.mediaRecorder.state === 'inactive') {
                reject(new Error('No recording in progress'));
                return;
            }

            this.mediaRecorder.onstop = () => {
                const audioBlob = new Blob(this.audioChunks, { type: 'audio/webm' });
                this.resolveRecording(audioBlob);
                resolve(audioBlob);
            };

            this.mediaRecorder.stop();
            this.mediaRecorder.stream.getTracks().forEach(track => track.stop());
        });
    }
}

class AudioProcessor {
    static webmToWav(webmBlob) {
        return new Promise(async (resolve, reject) => {
            try {
                const audioContext = new (window.AudioContext || window.webkitAudioContext)();
                const arrayBuffer = await webmBlob.arrayBuffer();
                const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);
                const wavBlob = this.audioBufferToWav(audioBuffer);
                resolve(wavBlob);
            } catch (error) {
                reject(error);
            }
        });
    }

    static audioBufferToWav(audioBuffer) {
        return new Promise((resolve) => {
            const numOfChan = audioBuffer.numberOfChannels;
            const length = audioBuffer.length * numOfChan * 2;
            const buffer = new ArrayBuffer(44 + length);
            const view = new DataView(buffer);
            
            // Write WAV header
            this.writeString(view, 0, 'RIFF');
            view.setUint32(4, 36 + length, true);
            this.writeString(view, 8, 'WAVE');
            this.writeString(view, 12, 'fmt ');
            view.setUint32(16, 16, true);
            view.setUint16(20, 1, true);
            view.setUint16(22, numOfChan, true);
            view.setUint32(24, audioBuffer.sampleRate, true);
            view.setUint32(28, audioBuffer.sampleRate * numOfChan * 2, true);
            view.setUint16(32, numOfChan * 2, true);
            view.setUint16(34, 16, true);
            this.writeString(view, 36, 'data');
            view.setUint32(40, length, true);

            // Write audio data
            let offset = 44;
            for (let i = 0; i < audioBuffer.numberOfChannels; i++) {
                const channelData = audioBuffer.getChannelData(i);
                for (let j = 0; j < channelData.length; j++) {
                    const sample = Math.max(-1, Math.min(1, channelData[j]));
                    view.setInt16(offset, sample < 0 ? sample * 0x8000 : sample * 0x7FFF, true);
                    offset += 2;
                }
            }

            resolve(new Blob([buffer], { type: 'audio/wav' }));
        });
    }

    static writeString(view, offset, string) {
        for (let i = 0; i < string.length; i++) {
            view.setUint8(offset + i, string.charCodeAt(i));
        }
    }

    static uploadToServer(wavBlob, url, filename = 'recording.wav') {
        return new Promise(async (resolve, reject) => {
            const formData = new FormData();
            formData.append('audio', wavBlob, filename);

            try {
                const response = await fetch(url, {
                    method: 'POST',
                    body: formData
                });

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const result = await response.json();
                resolve(result);
            } catch (error) {
                reject(error);
            }
        });
    }
}


var isRecording = false;
var recorder = new AudioRecorder();
var audioBlob = null;
async function record() {
    try {
        
        if (!isRecording) {
            // Start recording
            await recorder.start();
            isRecording = true;
        } else {
            // Stop recording
            const webmBlob = await recorder.stop();
            isRecording = false;

            // Convert to WAV
            audioBlob = await AudioProcessor.webmToWav(webmBlob);
        }
    } catch (error) {
        console.error('Recording error:', error);
    }
};

async function upload(inputBox, outputFunc) {
    if (!audioBlob) return;
    
    try {
        const result = await AudioProcessor.uploadToServer(
            audioBlob,
            '/speech-to-text',
            'recording.wav'
        );
        inputBox.value = result.transcript
        console.log(result.transcript)
        outputFunc()
    } catch (error) {
        console.error('Upload error:', error);
    }
};

export class AudioManager {
    constructor(element) {
        this.recording = false;
        this.element = element

        document.addEventListener("keydown", (event) => {
            // console.log(event.code)
            if (event.code == 'AltLeft' && !this.element.classList.contains('hidden')) {
                
                this.button.click()
            }
        });
    }
    setup(button, input, output) {
        this.button = button;
        this.input = input;
        this.output = output;

        this.button.onclick = () => {
            record()
            this.recording = !this.recording
            if (!this.recording) {
                setTimeout(() => {
                    upload(this.input, this.output)
                }, 300)
            }
        }
    }
}