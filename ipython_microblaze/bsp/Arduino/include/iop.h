#pragma once

#define G1 0
#define G2 1
#define G3 2
#define G4 3

#define G5 4
#define G6 5
#define G7 6

#define A1 0
#define A2 1
#define A3 2
#define A4 3

#define I2C 0xF

#define GPIO_IN 1
#define GPIO_OUT 0

typedef int gpio;

gpio gpio_connect_grove(unsigned char port, unsigned char wire);
gpio gpio_connect(unsigned char pin);
void gpio_write(gpio channel, unsigned char value);
unsigned char gpio_read(gpio channel);
void gpio_set_direction(gpio channel, unsigned char direction);

typedef int i2c;

i2c i2c_connect_grove(unsigned char port);
i2c i2c_connect(unsigned char sda, unsigned char scl);
void i2c_read(i2c instance, unsigned char address, unsigned char* data, int length);
void i2c_write(i2c instance, unsigned char address, unsigned char* data, int length);

typedef int pwm;

pwm pwm_connect(unsigned char pin);
pwm pwm_connect_grove(unsigned char port, unsigned char wire);
void pwm_generate_cycles(pwm timer, int period, int pulse);
void pwm_generate_us(pwm timer, int period, int pulse);
void pwm_stop(pwm timer);

typedef int adc;

adc adc_connect(unsigned char pi);
adc adc_connect_grove(unsigned char port, unsigned char wire);
adc adc_connect_i2c(i2c bus, unsigned int address);
int adc_read_raw(adc);
float adc_read(adc);

void iop_init();

void delay(int ms);
void delayMicroseconds(int us);
