"""Disposable compatibility fixtures using this candidate's exact overlay."""
import sys
from connected_life import prepare_fixtures as prior
from device_repair.content import build
prior.build=build
if __name__=='__main__':prior.prepare(*sys.argv[1:])
