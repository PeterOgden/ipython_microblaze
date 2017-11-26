#pragma once

enum {
GPIO_OUT = 0,
GPIO_IN = 1
};

typedef unsigned short mb_gpio;

int mb_gpio_num_devices();
mb_gpio mb_gpio_open_pin(int index, int channel, int pin);
mb_gpio mb_gpio_open_range(int index, int channel, int low, int high);
mb_gpio mb_gpio_open_all(int index, int channel);
void mb_gpio_set_direction(mb_gpio dev, int direction);
void mb_gpio_write(mb_gpio dev, int val);
int mb_gpio_read(mb_gpio dev);

typedef unsigned short mb_i2c;

int mb_i2c_num_devices();
mb_i2c mb_i2c_open(int index);
int mb_i2c_read(mb_i2c device, unsigned char address, char* data, int length);
int mb_i2c_write(mb_i2c device, unsigned char address, const char* data, int length);

typedef unsigned short mb_spi;

int mb_spi_num_devices();
mb_spi mp_spi_open(int index, int clk_phase, int clk_polarity);
int mb_spi_transfer(mb_spi device, const char* in_data, char* out_data, int length);

typedef unsigned short mb_timer;

int mb_timer_num_devices();
mb_timer mb_timer_open(int index);
void mb_timer_delay_us(mb_timer timer, int channel, int usdelay);
void mb_timer_pwm_generate(mb_timer timer, int pulse, int period);
void mb_timer_pwm_stop(mb_timer timer);

typedef unsigned short mb_adc;
int mb_adc_num_devices();
mb_adc mb_adc_open(int index);
int mb_adc_read_raw(mb_adc device);
float mb_adc_read(mb_adc device);
int mb_adc_range(mb_adc device);
float mb_adc_vref(mb_adc device);

void mb_io_init();

int delay(int ms);
int delayMicroseconds(int us);
void mb_set_delay_timer(mb_timer timer, int channel);
