##### RadioTest

# send a packet every 20ms with a 40B paylaod
radiotest tx pk 0xffff 8 0 40 20000

# receive packet on channel 1 during 60s
radiotest rx 0x1 60

