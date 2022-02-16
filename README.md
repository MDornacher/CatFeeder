# CatFeeder

Distinguish cats with automated cat feeder

---
## TODO:


### Hardware
#### Essential
- [ ] Update camera mount with smaller hooks and better support
- [ ] Reprint camera mount
- [X] Switch Raspberry Pi Zero with Raspberry Pi 4
#### Optional
- [ ] Add physical buttons (pause, reset, on-off switch)
- [ ] LED indicator
- [ ] Clean up cables
- [ ] Add tinker warning system
- [X] Monitor performance


### Software
#### Essential
- [X] Implement classifier
- [X] Add webcam stream
#### Optional
- [ ] Add unit and integration tests
- [ ] Wrap into service
- [X] Write clean log of feeding events for data analysis (e.g. with pandas)


### Classifier
#### Essential
- [X] Install tensorflow lite
#### Optional
- [X] Optimize model for speed (and accuracy)


### Publish
- [X] ~~Proper~~ secret handling for open sourcing project
- [ ] Collect / export all 3D models
- [ ] Draw circuit
- [ ] Write instructions