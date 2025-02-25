from .. import *

import awkward as ak
import numpy as np

class Generator:
    def __init__(self, gen_info, **config):
        self.__dict__.update(config)
        self.gen_info = gen_info

    def check(self, threshold=0.7, size=1000):
        eff = self.efficiency(size)
        return eff > threshold

    def event(self, size=1):
        return ak.zip({
            key : dist(size)
            for key, dist in self.gen_info.items()
        }, with_name="Momentum4D")
    
    def valid(self, event):
        return np.ones(len(event), dtype=bool)
    
    def physics(self, event):
        return dict()

    def efficiency(self, size=1000):
        event = self.event(size)
        valid_mask = self.valid(event)
        return np.mean(valid_mask)

    def __call__(self, size=1):
        event = self.event(size)
        valid_mask = self.valid(event)
        event = event[valid_mask]

        while len(event) < size:
            event = ak.concatenate([event, self.event(size)], axis=0)
            valid_mask = self.valid(event)
            event = event[valid_mask]

        physics = self.physics(event)
        return ak.zip(dict(
            event_pt=event.pt,
            event_eta=event.eta,
            event_phi=event.phi,
            event_m=event.m,
            **physics
        ), depth_limit=1)[:size]
