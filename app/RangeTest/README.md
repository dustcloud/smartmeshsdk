# RadioTest

#### set up the mote
- mode slave
- radiotest off

#### send a packet on every channel every 10ms with a 40B paylaod (version 1.3)
radiotest tx pk 0x1111 8 0 40 10000
#### send a packet on channels (0,4,8,12) every 10ms with a 40B paylaod (version 1.4)
radiotest tx pk 0x1111 8 26 0 40 10000

#### receive packet on channel 1 during 60s
radiotest rx 0x1 60

