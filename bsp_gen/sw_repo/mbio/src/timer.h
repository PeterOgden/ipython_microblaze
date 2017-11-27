#pragma once

typedef unsigned short timer;

int timer_num_devices();
timer timer_open(int index);
void timer_delay_us(timer timer, int channel, int usdelay);
void timer_pwm_generate(timer timer, int pulse, int period);
void timer_pwm_stop(timer timer);
void timer_set_as_default(timer timer, int channel);

int delay(int ms);
int delayMicroseconds(int us);
