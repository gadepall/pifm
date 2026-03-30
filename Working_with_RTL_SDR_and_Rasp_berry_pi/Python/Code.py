#!/usr/bin/env python3
import sys
import signal
from argparse import ArgumentParser
from gnuradio import analog
from gnuradio import audio
from gnuradio import filter
from gnuradio import gr
from gnuradio.filter import firdes
import osmosdr

class FMReceiver(gr.top_block):
    def __init__(self, freq, gain, samp_rate=2000000):
        gr.top_block.__init__(self, "Terminal FM Receiver")

        self.samp_rate = samp_rate
        self.center_freq = freq
        self.gain = gain

        self.rtlsdr_source = osmosdr.source(args="numchan=1")
        self.rtlsdr_source.set_sample_rate(self.samp_rate)
        self.rtlsdr_source.set_center_freq(self.center_freq, 0)
        self.rtlsdr_source.set_gain(self.gain, 0)
        
        self.lpf = filter.fir_filter_ccf(
            4, 
            firdes.low_pass(1, self.samp_rate, 100000, 20000)
        )
        self.wfm_rcv = analog.wfm_rcv(
            quad_rate=500000,
            audio_decimation=10,
        )
        self.audio_sink = audio.sink(48000, "", True)

        self.connect(self.rtlsdr_source, self.lpf)
        self.connect(self.lpf, self.wfm_rcv)
        self.connect(self.wfm_rcv, self.audio_sink)

def main():
    parser = ArgumentParser(description="Listen to FM Radio via RTL-SDR")
    parser.add_argument("-f", "--freq", type=float, default=98.3e6, help="Frequency in Hz (default: 98.3e6)")
    parser.add_argument("-g", "--gain", type=int, default=40, help="Gain (default: 40)")
    args = parser.parse_args()

    print(f"Starting Radio...")
    print(f"Frequency: {args.freq/1e6:.1f} MHz")
    print(f"Gain:      {args.gain}")

    tb = FMReceiver(freq=args.freq, gain=args.gain)

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()
        sys.exit(0)

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    tb.start()
    print("Press Ctrl+C to stop.")
    
    # Keep the script alive while the flowgraph runs
    signal.pause()

if __name__ == '__main__':
    main()